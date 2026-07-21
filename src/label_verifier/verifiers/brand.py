"""Brand Name verifier — tolerant (case, punct, whitespace, TM/(R))."""
from label_verifier.models import FieldVerdict, Verdict
from label_verifier.normalize import tolerant_text


def verify_brand(expected: str | None, found: str | None) -> FieldVerdict:
    if expected is None:
        return FieldVerdict(field="brand", expected=expected, found=found,
                            verdict=Verdict.MISSING)
    if not found or not found.strip():
        return FieldVerdict(field="brand", expected=expected, found=found,
                            verdict=Verdict.UNREADABLE)
    e = tolerant_text(expected)
    f = tolerant_text(found)
    verdict = Verdict.MATCH if e == f else Verdict.MISMATCH
    return FieldVerdict(field="brand", expected=expected, found=found, verdict=verdict)
