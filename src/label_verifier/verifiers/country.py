"""Country of origin verifier — tolerant; NOT_REQUIRED for domestic; import-required."""
from label_verifier.models import FieldVerdict, Verdict
from label_verifier.normalize import tolerant_text

# NOTE: "Scotland" is kept distinct from generic "United Kingdom" — TTB origin
# statements treat the constituent-country name as the specific, expected value;
# collapsing both to one "uk" token would let a genuine origin mismatch pass.
_COUNTRY_CANON = {
    "united states": "us", "usa": "us", "us": "us", "america": "us",
    "scotland": "scotland",
    "united kingdom": "uk", "uk": "uk", "great britain": "uk",
    "france": "fr", "ireland": "ie", "mexico": "mx", "canada": "ca",
    "germany": "de", "italy": "it", "spain": "es", "japan": "jp",
}


def _canon(s: str) -> str:
    t = tolerant_text(s)
    t = t.replace("product of", "").strip()
    for name, code in _COUNTRY_CANON.items():
        if name in t:
            return code
    return t


def verify_country(expected: str | None, found: str | None,
                   is_import: bool = False) -> FieldVerdict:
    if not is_import:
        return FieldVerdict(field="country", expected=expected, found=found,
                            verdict=Verdict.NOT_REQUIRED)
    if not expected:
        return FieldVerdict(field="country", expected=expected, found=found,
                            verdict=Verdict.MISSING)
    if not found or not found.strip():
        return FieldVerdict(field="country", expected=expected, found=found,
                            verdict=Verdict.MISSING)
    verdict = Verdict.MATCH if _canon(expected) == _canon(found) else Verdict.MISMATCH
    return FieldVerdict(field="country", expected=expected, found=found, verdict=verdict)
