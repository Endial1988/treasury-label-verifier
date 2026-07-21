"""Net contents verifier — numeric tolerant (+/-1% mL); unit-agnostic."""
import re

from label_verifier.models import FieldVerdict, Verdict
from label_verifier.normalize import volume_to_ml, tolerant_text

_TOL_FRAC = 0.01


def _all_volumes_ml(s: str) -> list[float]:
    out = []
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*([a-zA-Z%.]+)?", s or ""):
        try:
            value = float(m.group(1))
        except ValueError:
            continue
        unit = (m.group(2) or "").lower()
        if "oz" in unit or "fl" in unit:
            out.append(value * 29.5735)
        elif unit.startswith("l") and not unit.startswith("ml"):
            out.append(value * 1000.0)
        else:
            out.append(value)
    return out


def verify_net_contents(expected: str | None, found: str | None) -> FieldVerdict:
    if expected is None:
        return FieldVerdict(field="net_contents", expected=expected, found=found,
                            verdict=Verdict.MISSING)
    if not found or not found.strip():
        return FieldVerdict(field="net_contents", expected=expected, found=found,
                            verdict=Verdict.UNREADABLE)

    e_ml = volume_to_ml(expected)
    if e_ml is None:
        verdict = Verdict.MATCH if tolerant_text(expected) == tolerant_text(found) else Verdict.MISMATCH
        return FieldVerdict(field="net_contents", expected=expected, found=found, verdict=verdict)

    found_vols = _all_volumes_ml(found)
    if len(found_vols) >= 2:
        a, b = found_vols[0], found_vols[1]
        if max(a, b) > 0 and abs(a - b) / max(a, b) > _TOL_FRAC:
            return FieldVerdict(field="net_contents", expected=expected, found=found,
                                verdict=Verdict.MISMATCH, note="internal unit inconsistency")

    f_ml = volume_to_ml(found)
    if f_ml is None:
        return FieldVerdict(field="net_contents", expected=expected, found=found,
                            verdict=Verdict.UNREADABLE)

    verdict = Verdict.MATCH if abs(e_ml - f_ml) / max(e_ml, 1e-9) <= _TOL_FRAC else Verdict.MISMATCH
    return FieldVerdict(field="net_contents", expected=expected, found=found, verdict=verdict)
