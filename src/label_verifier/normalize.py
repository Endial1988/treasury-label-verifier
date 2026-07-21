"""Text normalization primitives for the RULE layer."""
from __future__ import annotations

import re
import unicodedata

_PUNCT_DELETE = set("'\"™®")
_PUNCT_TO_SPACE = set(".,-_/&—–")


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def strip_accents(s: str) -> str:
    """Decompose and drop combining marks, e.g. 'Café' -> 'Cafe'."""
    decomposed = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def lower(s: str) -> str:
    return s.lower()


def strip_ws(s: str) -> str:
    """Trim and collapse any run of whitespace to a single space."""
    return re.sub(r"\s+", " ", s).strip()


def fold_punct(s: str) -> str:
    """Delete quotes/TM/(R) outright; turn separator punctuation into a space."""
    out = []
    for ch in s:
        if ch in _PUNCT_DELETE:
            continue
        if ch in _PUNCT_TO_SPACE:
            out.append(" ")
        else:
            out.append(ch)
    return "".join(out)


def collapse_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def tolerant_text(s: str) -> str:
    """Pipeline for tolerant text fields: brand, class/type, name.

    fold_punct runs before strip_accents: NFKD (used for accent stripping)
    also expands compatibility symbols like TM/(R) into literal letters
    ('™' -> 'TM'), so symbol deletion must happen first or it silently stops
    matching.
    """
    return collapse_space(lower(strip_accents(fold_punct(nfc(s)))))


def extract_number(s: str) -> tuple[float, str] | None:
    """Return (value, unit_token) for the first 'number + unit' in s, else None."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*([a-zA-Z%./]+)?", s)
    if not m:
        return None
    value = float(m.group(1))
    unit = (m.group(2) or "").lower().rstrip(".,;")
    return value, unit


def abv_to_percent(s: str) -> float | None:
    """Extract %ABV. If only proof is given, convert proof -> %ABV (proof/2)."""
    val_unit = extract_number(s)
    if val_unit is None:
        return None
    value, unit = val_unit
    low = (s or "").lower()
    if "%" in low or "alc" in low or "abv" in low:
        return value
    if "proof" in low or "pr" in unit:
        return value / 2.0
    return value


def volume_to_ml(s: str) -> float | None:
    """Extract net contents in mL. Accept ml, cl, L, fl oz."""
    val_unit = extract_number(s)
    if val_unit is None:
        return None
    value, unit = val_unit
    low = (s or "").lower()
    if unit == "cl" or ("cl" in low and "ml" not in low):
        return value * 10.0
    if "l" == unit or unit.startswith("l") or "liter" in low:
        if "m" in low:
            return value
        return value * 1000.0
    if "fl" in low or "oz" in low:
        return value * 29.5735
    return value
