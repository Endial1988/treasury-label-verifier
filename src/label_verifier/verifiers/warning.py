"""Government Warning verifier — STRICT. Verbatim text; all-caps prefix required.

Bold/type-size/contrast detection is out of scope for text-based extraction —
the aggregation layer (aggregate.py) surfaces that as an explicit
Needs-Review note rather than silently treating it as passed.
"""
import re

from label_verifier.models import FieldVerdict, Verdict
from label_verifier.warning_data import CANONICAL_WARNING


def _ws_normalize(s: str) -> str:
    """Whitespace-only: collapse whitespace, trim. No lowercasing, no punctuation strip."""
    return re.sub(r"\s+", " ", s).strip()


def verify_warning(expected: str | None, found: str | None) -> FieldVerdict:
    reference = CANONICAL_WARNING
    if not found or not found.strip():
        return FieldVerdict(field="warning", expected=reference, found=found,
                            verdict=Verdict.UNREADABLE)
    ref_n = _ws_normalize(reference)
    found_n = _ws_normalize(found)
    verdict = Verdict.MATCH if ref_n == found_n else Verdict.MISMATCH
    note = None
    if verdict == Verdict.MISMATCH:
        if found_n.lower().startswith("government warning") and not found_n.startswith("GOVERNMENT WARNING"):
            note = "prefix not all-caps"
    return FieldVerdict(field="warning", expected=reference, found=found,
                        verdict=verdict, note=note)
