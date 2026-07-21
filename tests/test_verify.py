from label_verifier.verify import verify_label, FIELD_VERIFIERS
from label_verifier.models import Verdict


def test_registry_has_seven_fields():
    from label_verifier.verifiers import FIELD_VERIFIERS as F
    assert set(F) == {
        "brand", "class_type", "alcohol", "net_contents",
        "bottler", "country", "warning",
    }


def test_verify_label_all_match_overall_match():
    from label_verifier.warning_data import CANONICAL_WARNING
    expected = {
        "brand": "OLD TOM DISTILLERY",
        "class_type": "Kentucky Straight Bourbon Whiskey",
        "alcohol": "45% Alc./Vol. (90 Proof)",
        "net_contents": "750 mL",
        "bottler": "Old Tom Distillery, Lawrenceburg, KY",
        "country": None,
        "warning": CANONICAL_WARNING,
    }
    found = dict(expected)
    result = verify_label(expected, found, is_import=False)
    assert result.overall == Verdict.MATCH
    assert result.summary["match"] == 6
    assert result.summary["not_required"] == 1


def test_verify_label_one_mismatch_propagates():
    from label_verifier.warning_data import CANONICAL_WARNING
    expected = {"brand": "X", "class_type": "Bourbon", "alcohol": "45%",
                "net_contents": "750 mL", "bottler": "Old Tom, KY",
                "country": None, "warning": CANONICAL_WARNING}
    found = dict(expected)
    found["brand"] = "Y"
    result = verify_label(expected, found, is_import=False)
    assert result.overall == Verdict.MISMATCH
    assert result.summary.get("mismatch") == 1


def test_verify_label_country_not_required_domestic():
    result = verify_label({}, {}, is_import=False)
    country_v = next(v for v in result.label_verdicts if v.field == "country")
    assert country_v.verdict == Verdict.NOT_REQUIRED


def test_verify_label_unreadable_without_mismatch_is_not_overall_mismatch():
    from label_verifier.warning_data import CANONICAL_WARNING
    expected = {"brand": "X", "class_type": "Bourbon", "alcohol": "45%",
                "net_contents": "750 mL", "bottler": "Old Tom, KY",
                "country": None, "warning": CANONICAL_WARNING}
    found = dict(expected)
    found["brand"] = None
    result = verify_label(expected, found, is_import=False)
    assert result.overall == Verdict.UNREADABLE
    assert result.overall != Verdict.MISMATCH
