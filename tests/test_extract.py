"""Unit tests for the pure text-parsing half of extraction (no tesseract needed)."""
from label_verifier.extract import fields_from_text
from label_verifier.warning_data import CANONICAL_WARNING

_LABEL_TEXT = (
    "OLD TOM DISTILLERY\n"
    "Kentucky Straight Bourbon Whiskey\n"
    "45% Alc./Vol. (90 Proof)\n"
    "750 mL\n"
    "Old Tom Distillery, Lawrenceburg, KY\n"
    f"{CANONICAL_WARNING}\n"
)


def test_brand_is_first_line():
    f = fields_from_text(_LABEL_TEXT)
    assert f["brand"].text == "OLD TOM DISTILLERY"


def test_class_type_is_second_line():
    f = fields_from_text(_LABEL_TEXT)
    assert f["class_type"].text == "Kentucky Straight Bourbon Whiskey"


def test_alcohol_regex_finds_percent_and_proof():
    f = fields_from_text(_LABEL_TEXT)
    assert "45%" in f["alcohol"].text
    assert "90" in f["alcohol"].text


def test_net_contents_regex_finds_ml():
    f = fields_from_text(_LABEL_TEXT)
    assert f["net_contents"].text == "750 mL"


def test_bottler_line_found_by_state_token():
    f = fields_from_text(_LABEL_TEXT)
    assert "Lawrenceburg" in f["bottler"].text


def test_warning_captured_verbatim_to_end():
    f = fields_from_text(_LABEL_TEXT)
    assert f["warning"].text.startswith("GOVERNMENT WARNING:")
    assert "birth defects" in f["warning"].text


def test_proof_only_alcohol_still_found():
    text = "BRAND\nCLASS\n90 Proof\n750 mL\nBottler, TX\n"
    f = fields_from_text(text)
    assert "90" in f["alcohol"].text
    assert "proof" in f["alcohol"].text.lower()


def test_empty_text_yields_all_none_never_invented():
    f = fields_from_text("")
    assert all(v.text is None for v in f.values())


def test_missing_warning_section_is_none_not_guessed():
    text = "BRAND\nCLASS\n45%\n750 mL\nBottler, TX\n"
    f = fields_from_text(text)
    assert f["warning"].text is None


def test_country_product_of_phrase_extracted():
    text = "BRAND\nSCOTCH\n40%\n750 mL\nProduct of Scotland\n"
    f = fields_from_text(text)
    assert f["country"].text is not None
    assert "scotland" in f["country"].text.lower()
