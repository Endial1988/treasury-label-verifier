"""Alcohol content verifier — numeric tolerant (+/-0.1 %ABV); proof <-> ABV."""
import re

from label_verifier.models import FieldVerdict, Verdict
from label_verifier.normalize import tolerant_text

_TOL = 0.1  # %ABV


def _pct_and_proof(s: str) -> tuple[float | None, float | None]:
    low = (s or "").lower()
    pct = None
    proof = None
    m_pct = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|abv|alc)", low)
    if m_pct:
        pct = float(m_pct.group(1))
    m_pr = re.search(r"(\d+(?:\.\d+)?)\s*proof", low)
    if m_pr:
        proof = float(m_pr.group(1))
    return pct, proof


def verify_alcohol(expected: str | None, found: str | None) -> FieldVerdict:
    if expected is None:
        return FieldVerdict(field="alcohol", expected=expected, found=found,
                            verdict=Verdict.MISSING)
    if not found or not found.strip():
        return FieldVerdict(field="alcohol", expected=expected, found=found,
                            verdict=Verdict.UNREADABLE)

    e_pct, _ = _pct_and_proof(expected)
    f_pct, f_proof = _pct_and_proof(found)

    if e_pct is None:
        verdict = Verdict.MATCH if tolerant_text(expected) == tolerant_text(found) else Verdict.MISMATCH
        return FieldVerdict(field="alcohol", expected=expected, found=found, verdict=verdict)

    if f_pct is not None and f_proof is not None:
        if abs(f_pct - f_proof / 2.0) > _TOL:
            return FieldVerdict(field="alcohol", expected=expected, found=found,
                                verdict=Verdict.MISMATCH,
                                note="internal % vs proof inconsistency")

    found_pct = f_pct if f_pct is not None else (f_proof / 2.0 if f_proof is not None else None)
    if found_pct is None:
        return FieldVerdict(field="alcohol", expected=expected, found=found,
                            verdict=Verdict.UNREADABLE)

    verdict = Verdict.MATCH if abs(e_pct - found_pct) <= _TOL else Verdict.MISMATCH
    return FieldVerdict(field="alcohol", expected=expected, found=found, verdict=verdict)
