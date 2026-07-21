"""Bottler/producer name+address verifier — tolerant name; address presence required."""
import re

from label_verifier.models import FieldVerdict, Verdict
from label_verifier.normalize import tolerant_text

_STATES = {
    "alabama": "al", "alaska": "ak", "arizona": "az", "arkansas": "ar", "california": "ca",
    "colorado": "co", "connecticut": "ct", "delaware": "de", "florida": "fl", "georgia": "ga",
    "hawaii": "hi", "idaho": "id", "illinois": "il", "indiana": "in", "iowa": "ia",
    "kansas": "ks", "kentucky": "ky", "louisiana": "la", "maine": "me", "maryland": "md",
    "massachusetts": "ma", "michigan": "mi", "minnesota": "mn", "mississippi": "ms",
    "missouri": "mo", "montana": "mt", "nebraska": "ne", "nevada": "nv",
    "new hampshire": "nh", "new jersey": "nj", "new mexico": "nm", "new york": "ny",
    "north carolina": "nc", "north dakota": "nd", "ohio": "oh", "oklahoma": "ok",
    "oregon": "or", "pennsylvania": "pa", "rhode island": "ri", "south carolina": "sc",
    "south dakota": "sd", "tennessee": "tn", "texas": "tx", "utah": "ut", "vermont": "vt",
    "virginia": "va", "washington": "wa", "west virginia": "wv", "wisconsin": "wi",
    "wyoming": "wy",
}


def _normalize_addr(s: str) -> str:
    t = tolerant_text(s)
    for full, abbr in _STATES.items():
        t = t.replace(full, abbr)
    return t


def _has_address(s: str) -> bool:
    t = tolerant_text(s)
    if re.search(r"\b[a-z]{2}\b", t):
        return True
    for full in _STATES:
        if full in t:
            return True
    return False


def verify_bottler(expected: str | None, found: str | None) -> FieldVerdict:
    if expected is None:
        return FieldVerdict(field="bottler", expected=expected, found=found,
                            verdict=Verdict.MISSING)
    if not found or not found.strip():
        return FieldVerdict(field="bottler", expected=expected, found=found,
                            verdict=Verdict.UNREADABLE)

    e_norm = _normalize_addr(expected)
    f_norm = _normalize_addr(found)
    verdict = Verdict.MATCH if e_norm == f_norm else Verdict.MISMATCH
    note = None
    if verdict == Verdict.MISMATCH and not (_has_address(expected) and _has_address(found)):
        note = "address component missing on one side"
    return FieldVerdict(field="bottler", expected=expected, found=found,
                        verdict=verdict, note=note)
