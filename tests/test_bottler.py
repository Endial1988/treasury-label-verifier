import pytest
from label_verifier.models import Verdict
from label_verifier.verifiers.bottler import verify_bottler


@pytest.mark.parametrize("expected, found, want", [
    ("Old Tom Distillery, Lawrenceburg, KY", "Old Tom Distillery, Lawrenceburg, KY", Verdict.MATCH),
    ("Old Tom Distillery, Lawrenceburg, KY", "Old Tom Distillery, Lawrenceburg, Kentucky", Verdict.MATCH),
    ("Old Tom Distillery, Lawrenceburg, KY", "Old Tom Distillery, Louisville, KY", Verdict.MISMATCH),
    ("Old Tom Distillery, Lawrenceburg, KY", "Old Tom Distillery", Verdict.MISMATCH),
    ("Old Tom Distillery", "Old Tom Distillery, Lawrenceburg, KY", Verdict.MISMATCH),
])
def test_bottler_pairs(expected, found, want):
    assert verify_bottler(expected, found).verdict == want


def test_bottler_unreadable():
    assert verify_bottler("Old Tom Distillery, KY", None).verdict == Verdict.UNREADABLE
