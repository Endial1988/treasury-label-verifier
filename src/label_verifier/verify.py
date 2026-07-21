"""Orchestrator: run all field verifiers and aggregate into a VerifyResult.

Audit fix (2026-07-20): overall status must distinguish a genuine failure
(MISMATCH on some field) from mere uncertainty (UNREADABLE / LOW_CONFIDENCE /
MISSING on a field with no real mismatch elsewhere) — see governing prompt
Sec.5 items 5-7. `aggregate.py` maps the resulting three-way outcome to the
public pass/fail/needs_review vocabulary.
"""
from label_verifier.models import FieldVerdict, Verdict, VerifyResult
from label_verifier.verifiers import FIELD_VERIFIERS

_HARD_FAIL = {Verdict.MISMATCH}
_UNCERTAIN = {Verdict.UNREADABLE, Verdict.LOW_CONFIDENCE, Verdict.MISSING}


def verify_label(expected: dict, found: dict, is_import: bool = False) -> VerifyResult:
    """Run all 7 field verifiers. `expected` and `found` map field name -> value.

    Missing keys are treated as None. The country verifier receives is_import.
    """
    verdicts: list[FieldVerdict] = []
    for field, fn in FIELD_VERIFIERS.items():
        e = expected.get(field)
        f = found.get(field)
        if field == "country":
            verdicts.append(fn(e, f, is_import=is_import))
        else:
            verdicts.append(fn(e, f))

    summary: dict[str, int] = {}
    for v in verdicts:
        summary[v.verdict.value] = summary.get(v.verdict.value, 0) + 1

    if any(v.verdict in _HARD_FAIL for v in verdicts):
        overall = Verdict.MISMATCH
    elif any(v.verdict in _UNCERTAIN for v in verdicts):
        overall = Verdict.UNREADABLE
    else:
        overall = Verdict.MATCH
    return VerifyResult(label_verdicts=verdicts, overall=overall, summary=summary)
