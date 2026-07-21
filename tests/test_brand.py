import pytest
from label_verifier.models import Verdict
from label_verifier.verifiers.brand import verify_brand


@pytest.mark.parametrize("expected, found, want", [
    ("OLD TOM DISTILLERY", "OLD TOM DISTILLERY", Verdict.MATCH),
    ("STONE'S THROW", "STONE'S THROW", Verdict.MATCH),
    ("STONE'S THROW", "Stone's Throw", Verdict.MATCH),
    ("STONE'S THROW", "STONES THROW", Verdict.MATCH),
    ("STONE'S THROW", "STONE THROW", Verdict.MISMATCH),
    ("STONE'S THROW", "STONE'S THROW™", Verdict.MATCH),
    ("OLD TOM", "OLD TOM DISTILLERY", Verdict.MISMATCH),
])
def test_brand_pairs(expected, found, want):
    assert verify_brand(expected, found).verdict == want


def test_brand_unreadable_when_found_missing():
    v = verify_brand("STONE'S THROW", None)
    assert v.verdict == Verdict.UNREADABLE


def test_brand_missing_when_expected_missing():
    v = verify_brand(None, "X")
    assert v.verdict == Verdict.MISSING
