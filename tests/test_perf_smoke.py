import time
from label_verifier.verify import verify_label
from label_verifier.warning_data import CANONICAL_WARNING

_BUDGET_S = 0.1


def test_rule_layer_within_100ms():
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
    t0 = time.perf_counter()
    for _ in range(100):
        verify_label(expected, found, is_import=False)
    elapsed = (time.perf_counter() - t0) / 100
    assert elapsed < _BUDGET_S, f"rule layer took {elapsed*1000:.2f} ms/label (budget {_BUDGET_S*1000} ms)"
