import pytest
from label_verifier.models import Verdict
from label_verifier.verifiers.country import verify_country


def test_country_match_import():
    assert verify_country("Scotland", "Scotland", is_import=True).verdict == Verdict.MATCH


def test_country_mismatch_import():
    assert verify_country("Scotland", "United Kingdom", is_import=True).verdict == Verdict.MISMATCH


def test_country_missing_when_import_and_absent():
    assert verify_country("France", None, is_import=True).verdict == Verdict.MISSING


def test_country_not_required_when_domestic():
    assert verify_country(None, None, is_import=False).verdict == Verdict.NOT_REQUIRED


def test_country_product_of_phrase_tolerated():
    assert verify_country("Scotland", "Product of Scotland", is_import=True).verdict == Verdict.MATCH
