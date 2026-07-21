"""Extraction adapter: label image -> structured, schema-validated fields.

Split into a pure text-parsing layer (`fields_from_text`, fully unit-testable
without tesseract installed) and a thin I/O layer (`extract_fields`) that
calls tesseract. This is a heuristic, line-position/regex-based field
splitter, not a trained model — appropriate for a prototype, and documented
as a known limitation in README.md. It never invents text: any field it
can't confidently locate comes back as `text=None`, which the RULE layer
then reports as UNREADABLE/MISSING rather than a fabricated value.
"""
from __future__ import annotations

import io
import re

from pydantic import BaseModel

from label_verifier.verifiers.bottler import _STATES


class ExtractedField(BaseModel):
    text: str | None
    confidence: float | None = None


class ExtractionResult(BaseModel):
    fields: dict[str, ExtractedField]
    raw_text: str
    ocr_error: str | None = None


_FIELDS = ("brand", "class_type", "alcohol", "net_contents", "bottler", "country", "warning")

_ALCOHOL_RE = re.compile(
    r"\d+(?:\.\d+)?\s*%[^\n]*?\(\s*\d+(?:\.\d+)?\s*proof\s*\)"  # "45% ... (90 Proof)"
    r"|\d+(?:\.\d+)?\s*%"                                        # "45%"
    r"|\d+(?:\.\d+)?\s*proof",                                   # "90 Proof" alone
    re.I,
)
_NET_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:m\s?l|l\b|fl\.?\s*oz)", re.I)
_WARNING_START_RE = re.compile(r"government\s+warning\s*:?", re.I)
_COUNTRY_RE = re.compile(r"product\s+of\s+[a-z ]+", re.I)
_STATE_ABBRS = set(_STATES.values())


def _non_empty_lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def _has_address_token(line: str) -> bool:
    low = line.lower()
    words = re.findall(r"\b[a-z]{2}\b", low)  # whole 2-letter words only
    if any(w in _STATE_ABBRS for w in words):
        return True
    return any(state in low for state in _STATES)


def fields_from_text(raw_text: str) -> dict[str, ExtractedField]:
    """Pure heuristic field splitter — no I/O, fully unit-testable."""
    lines = _non_empty_lines(raw_text)
    out: dict[str, ExtractedField] = {f: ExtractedField(text=None) for f in _FIELDS}

    if not lines:
        return out

    # Brand: first line (top-of-label convention).
    out["brand"] = ExtractedField(text=lines[0])
    # Class/type: second line, if it doesn't look like an ABV/net-contents/address line.
    if len(lines) > 1 and not _ALCOHOL_RE.search(lines[1]) and not _NET_RE.search(lines[1]):
        out["class_type"] = ExtractedField(text=lines[1])

    m = _ALCOHOL_RE.search(raw_text)
    if m:
        out["alcohol"] = ExtractedField(text=m.group(0).strip())

    m = _NET_RE.search(raw_text)
    if m:
        out["net_contents"] = ExtractedField(text=m.group(0).strip())

    for line in lines:
        if _has_address_token(line) and line not in (out["brand"].text, out["class_type"].text):
            out["bottler"] = ExtractedField(text=line)
            break

    m = _COUNTRY_RE.search(raw_text)
    if m:
        out["country"] = ExtractedField(text=m.group(0).strip())

    wm = _WARNING_START_RE.search(raw_text)
    if wm:
        # Warning text runs from the matched prefix to the end of the raw text
        # (it's always the last mandatory element on a label).
        warning_text = raw_text[wm.start():].replace("\n", " ")
        warning_text = re.sub(r"\s+", " ", warning_text).strip()
        out["warning"] = ExtractedField(text=warning_text)

    return out


def extract_fields(image_bytes: bytes) -> ExtractionResult:
    """Run OCR on image bytes and split the result into structured fields.

    Never raises on a bad/corrupt image — returns ocr_error instead, with all
    fields None, so the caller can route straight to UNREADABLE rather than
    crashing or guessing.
    """
    try:
        import pytesseract
        from PIL import Image, UnidentifiedImageError
    except ImportError as e:  # pragma: no cover - environment misconfiguration
        return ExtractionResult(fields={f: ExtractedField(text=None) for f in _FIELDS},
                                raw_text="", ocr_error=f"OCR dependencies unavailable: {e}")

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.load()
    except Exception as e:
        return ExtractionResult(fields={f: ExtractedField(text=None) for f in _FIELDS},
                                raw_text="", ocr_error=f"could not decode image: {e}")

    try:
        raw_text = pytesseract.image_to_string(img)
    except Exception as e:
        return ExtractionResult(fields={f: ExtractedField(text=None) for f in _FIELDS},
                                raw_text="", ocr_error=f"OCR failed: {e}")

    fields = fields_from_text(raw_text)
    return ExtractionResult(fields=fields, raw_text=raw_text, ocr_error=None)
