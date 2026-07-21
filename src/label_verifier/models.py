"""Shared types for the label-verification RULE layer.

Verdict vocabulary (per-field, six-way):
- MATCH          values agree after normalization
- MISMATCH       values disagree after normalization
- UNREADABLE     extraction could not read the field (extraction failure)
- LOW_CONFIDENCE extraction below confidence threshold
- MISSING        field required for this beverage type but absent from application
- NOT_REQUIRED   field not applicable (e.g. country of origin for a domestic product)

`overall` on VerifyResult reuses this same enum internally (MATCH/MISMATCH/
UNREADABLE) but is mapped by aggregate.py to the reporting vocabulary
`pass | fail | needs_review` — see aggregate.py for the authoritative mapping.
"""
from enum import Enum

from pydantic import BaseModel


class Verdict(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    UNREADABLE = "unreadable"
    LOW_CONFIDENCE = "low_confidence"
    MISSING = "missing"
    NOT_REQUIRED = "not_required"


class FieldVerdict(BaseModel):
    field: str
    expected: str | None
    found: str | None
    verdict: Verdict
    confidence: float | None = None
    note: str | None = None


class VerifyResult(BaseModel):
    label_verdicts: list[FieldVerdict]
    overall: Verdict
    summary: dict[str, int]
