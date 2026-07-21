from label_verifier.aggregate import build_report
from label_verifier.verify import verify_label
from label_verifier.warning_data import CANONICAL_WARNING


def _base_expected():
    return {
        "brand": "OLD TOM DISTILLERY",
        "class_type": "Kentucky Straight Bourbon Whiskey",
        "alcohol": "45% Alc./Vol. (90 Proof)",
        "net_contents": "750 mL",
        "bottler": "Old Tom Distillery, Lawrenceburg, KY",
        "country": None,
        "warning": CANONICAL_WARNING,
    }


def test_all_match_yields_overall_pass():
    expected = _base_expected()
    result = verify_label(expected, dict(expected), is_import=False)
    report = build_report(result)
    assert report.overall == "pass"
    assert all(f.status == "pass" for f in report.fields)


def test_mismatch_yields_overall_fail():
    expected = _base_expected()
    found = dict(expected)
    found["brand"] = "Different Name"
    report = build_report(verify_label(expected, found, is_import=False))
    assert report.overall == "fail"
    brand_field = next(f for f in report.fields if f.field == "brand")
    assert brand_field.status == "fail"
    assert brand_field.explanation


def test_unreadable_without_mismatch_yields_needs_review_not_fail():
    expected = _base_expected()
    found = dict(expected)
    found["net_contents"] = None
    report = build_report(verify_label(expected, found, is_import=False))
    assert report.overall == "needs_review"


def test_warning_field_always_carries_formatting_disclosure():
    expected = _base_expected()
    report = build_report(verify_label(expected, dict(expected), is_import=False))
    warning_field = next(f for f in report.fields if f.field == "warning")
    assert "formatting" in warning_field.note.lower() or "bold" in warning_field.note.lower()


def test_every_field_has_a_nonempty_explanation():
    expected = _base_expected()
    report = build_report(verify_label(expected, dict(expected), is_import=False))
    assert all(f.explanation.strip() for f in report.fields)
    assert report.overall_explanation.strip()
