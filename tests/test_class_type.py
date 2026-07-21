import pytest
from label_verifier.models import Verdict
from label_verifier.verifiers.class_type import verify_class_type


@pytest.mark.parametrize("expected, found, want", [
    ("Kentucky Straight Bourbon Whiskey", "Kentucky Straight Bourbon Whiskey", Verdict.MATCH),
    ("Kentucky Straight Bourbon Whiskey", "Bourbon Whiskey", Verdict.MATCH),
    ("Bourbon Whiskey", "Whiskey", Verdict.MISMATCH),
    ("Scotch Whisky", "Scotch Whiskey", Verdict.MATCH),
    ("Rum", "Dark Rum", Verdict.MATCH),
    ("Vodka", "Gin", Verdict.MISMATCH),
])
def test_class_type_pairs(expected, found, want):
    assert verify_class_type(expected, found).verdict == want


def test_class_type_unreadable():
    assert verify_class_type("Bourbon Whiskey", None).verdict == Verdict.UNREADABLE
