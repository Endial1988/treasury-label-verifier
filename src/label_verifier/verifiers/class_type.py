"""Class/Type verifier — tolerant with synonym map; canonical class drift = MISMATCH."""
from label_verifier.models import FieldVerdict, Verdict
from label_verifier.normalize import tolerant_text

# Ordered most-specific-first: a more specific subtype (bourbon, scotch, rye)
# must win over the generic supertype (whiskey) when both appear as substrings,
# so dropping the subtype qualifier (e.g. "Bourbon Whiskey" -> "Whiskey") is
# correctly treated as class drift, not a harmless synonym.
_CANONICAL = [
    ("bourbon", "bourbon"),
    ("scotch", "scotch"),
    ("rye", "rye"),
    ("whiskey", "whiskey"), ("whisky", "whiskey"),
    ("rum", "rum"),
    ("vodka", "vodka"),
    ("gin", "gin"),
    ("tequila", "tequila"),
    ("cognac", "brandy"), ("brandy", "brandy"),
    ("wine", "wine"),
    ("ale", "beer"), ("lager", "beer"), ("beer", "beer"),
]


def _canonical_token(text: str) -> str | None:
    t = tolerant_text(text)
    for alias, canon in _CANONICAL:
        if alias in t:
            return canon
    return t


def verify_class_type(expected: str | None, found: str | None) -> FieldVerdict:
    if expected is None:
        return FieldVerdict(field="class_type", expected=expected, found=found,
                            verdict=Verdict.MISSING)
    if not found or not found.strip():
        return FieldVerdict(field="class_type", expected=expected, found=found,
                            verdict=Verdict.UNREADABLE)
    e_tok = _canonical_token(expected)
    f_tok = _canonical_token(found)
    verdict = Verdict.MATCH if e_tok == f_tok else Verdict.MISMATCH
    return FieldVerdict(field="class_type", expected=expected, found=found, verdict=verdict)
