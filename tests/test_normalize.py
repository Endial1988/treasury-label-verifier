from label_verifier.normalize import (
    nfc, strip_ws, lower, fold_punct, collapse_space, tolerant_text,
    extract_number, abv_to_percent, volume_to_ml,
)


def test_strip_ws_collapses_internal_runs():
    assert strip_ws("  STONE'S   THROW\n") == "STONE'S THROW"


def test_fold_punct_removes_punct_and_tm():
    # Exact spacing is not load-bearing (plan note: adjust to implementation);
    # the invariant that matters is the tolerant_text pipeline below.
    assert fold_punct("STONE'S-THROW™ & Co.") == "STONES THROW   Co "


def test_tolerant_text_pipeline():
    assert tolerant_text("STONE'S THROW™") == "stones throw"


def test_tolerant_text_handles_unicode():
    assert tolerant_text("Café — Old Tom") == "cafe old tom"


def test_extract_number_with_unit():
    assert extract_number("45% Alc./Vol. (90 Proof)") == (45.0, "%")
    assert extract_number("750 mL") == (750.0, "ml")


def test_extract_number_returns_none_when_no_number():
    assert extract_number("no number here") is None


def test_abv_to_percent_from_explicit_percent():
    assert abv_to_percent("45% Alc./Vol.") == 45.0


def test_abv_to_percent_from_proof_only():
    assert abv_to_percent("90 proof") == 45.0


def test_volume_to_ml_metric():
    assert volume_to_ml("750 mL") == 750.0
    assert volume_to_ml("0.75 L") == 750.0


def test_volume_to_ml_us_customary():
    # 750 mL / 29.5735 ml-per-floz = 25.36 fl oz (not 25.4 — that's ~1.17 mL off).
    assert abs(volume_to_ml("25.36 fl oz") - 750.0) < 1.0


def test_volume_to_ml_centiliters():
    # Common on European labels, e.g. "70cl e" (70 centiliters, estimated volume mark).
    assert volume_to_ml("70cl") == 700.0
    assert volume_to_ml("70 cl e") == 700.0
    assert volume_to_ml("75cl") == 750.0
