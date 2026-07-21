"""Map the RULE layer's six-way per-field Verdict onto the reporting
vocabulary (pass / fail / needs_review) with a human-readable explanation
per field — the governing requirement is that every result be explained,
never an opaque score, and that uncertainty is never silently reported as a
pass. See docs/superpowers/plans/2026-07-05-spike-and-rule-layer.md
Addendum (2026-07-20) for why overall/field status are a separate three-way
vocabulary from the six-way Verdict enum.
"""
from __future__ import annotations

from pydantic import BaseModel

from label_verifier.models import Verdict, VerifyResult

Status = str  # "pass" | "fail" | "needs_review"

_STATUS_MAP: dict[Verdict, Status] = {
    Verdict.MATCH: "pass",
    Verdict.NOT_REQUIRED: "pass",
    Verdict.MISMATCH: "fail",
    Verdict.UNREADABLE: "needs_review",
    Verdict.LOW_CONFIDENCE: "needs_review",
    Verdict.MISSING: "needs_review",
}

_EXPLANATIONS: dict[Verdict, str] = {
    Verdict.MATCH: "Extracted value matches the application after normalization.",
    Verdict.NOT_REQUIRED: "Not applicable for this label (e.g. country of origin on a domestic product).",
    Verdict.MISMATCH: "Extracted value does not match the application.",
    Verdict.UNREADABLE: "Could not read this field from the uploaded image.",
    Verdict.LOW_CONFIDENCE: "Extraction confidence was below the threshold for a reliable comparison.",
    Verdict.MISSING: "This field was not provided in the application data.",
}


class ReportField(BaseModel):
    field: str
    expected: str | None
    found: str | None
    status: Status
    verdict: Verdict
    explanation: str
    note: str | None = None


class Report(BaseModel):
    fields: list[ReportField]
    overall: Status
    overall_explanation: str
    summary: dict[str, int]


_WARNING_FORMATTING_NOTE = (
    "Text content verified verbatim. Boldness, type size, contrast, and "
    "spacing cannot be reliably determined from OCR text extraction alone — "
    "those formatting checks are not evaluated and must be confirmed by a "
    "human reviewer."
)


def build_report(result: VerifyResult) -> Report:
    fields: list[ReportField] = []
    for fv in result.label_verdicts:
        status = _STATUS_MAP[fv.verdict]
        explanation = fv.note or _EXPLANATIONS[fv.verdict]
        note = fv.note
        if fv.field == "warning":
            # Never let silence read as "formatting checks passed" (audit finding 3).
            note = f"{note + ' ' if note else ''}{_WARNING_FORMATTING_NOTE}"
        fields.append(ReportField(
            field=fv.field, expected=fv.expected, found=fv.found,
            status=status, verdict=fv.verdict, explanation=explanation, note=note,
        ))

    overall_status = _STATUS_MAP[result.overall]
    if overall_status == "fail":
        overall_explanation = "One or more required fields do not match the application."
    elif overall_status == "needs_review":
        overall_explanation = "No field failed outright, but at least one could not be confidently verified."
    else:
        overall_explanation = "All required fields were confidently verified and match the application."

    return Report(fields=fields, overall=overall_status,
                  overall_explanation=overall_explanation, summary=result.summary)
