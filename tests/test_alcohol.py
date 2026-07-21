import pytest
from label_verifier.models import Verdict
from label_verifier.verifiers.alcohol import verify_alcohol


@pytest.mark.parametrize("expected, found, want", [
    ("45% Alc./Vol. (90 Proof)", "45% Alc./Vol. (90 Proof)", Verdict.MATCH),
    ("45% Alc./Vol. (90 Proof)", "45%", Verdict.MATCH),
    ("45% Alc./Vol. (90 Proof)", "90 Proof", Verdict.MATCH),
    ("45% Alc./Vol. (90 Proof)", "46%", Verdict.MISMATCH),
    ("45% Alc./Vol. (90 Proof)", "45.05%", Verdict.MATCH),
    ("45% (90 proof)", "45% (88 proof)", Verdict.MISMATCH),
])
def test_alcohol_pairs(expected, found, want):
    assert verify_alcohol(expected, found).verdict == want


def test_alcohol_unreadable():
    assert verify_alcohol("45% Alc./Vol.", None).verdict == Verdict.UNREADABLE
