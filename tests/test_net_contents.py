import pytest
from label_verifier.models import Verdict
from label_verifier.verifiers.net_contents import verify_net_contents


@pytest.mark.parametrize("expected, found, want", [
    ("750 mL", "750 mL", Verdict.MATCH),
    ("750 mL", "0.75 L", Verdict.MATCH),
    ("750 mL", "750ml", Verdict.MATCH),
    ("750 mL", "751 mL", Verdict.MATCH),
    ("750 mL", "700 mL", Verdict.MISMATCH),
    ("750 mL", "25.4 fl oz", Verdict.MATCH),
    ("750 mL (25.4 fl oz)", "750 mL (24 fl oz)", Verdict.MISMATCH),
])
def test_net_contents_pairs(expected, found, want):
    assert verify_net_contents(expected, found).verdict == want


def test_net_contents_unreadable():
    assert verify_net_contents("750 mL", None).verdict == Verdict.UNREADABLE
