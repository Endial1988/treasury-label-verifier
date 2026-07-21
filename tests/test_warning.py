import pytest
from label_verifier.models import Verdict
from label_verifier.verifiers.warning import verify_warning
from label_verifier.warning_data import CANONICAL_WARNING


def test_warning_canonical_matches_itself():
    assert verify_warning(CANONICAL_WARNING, CANONICAL_WARNING).verdict == Verdict.MATCH


def test_warning_titlecase_prefix_mismatch():
    bad = CANONICAL_WARNING.replace("GOVERNMENT WARNING:", "Government Warning:")
    assert verify_warning(CANONICAL_WARNING, bad).verdict == Verdict.MISMATCH


def test_warning_missing_colon_mismatch():
    bad = CANONICAL_WARNING.replace("GOVERNMENT WARNING:", "GOVERNMENT WARNING")
    assert verify_warning(CANONICAL_WARNING, bad).verdict == Verdict.MISMATCH


def test_warning_only_first_paragraph_mismatch():
    bad = CANONICAL_WARNING.split("(2)", 1)[0].strip()
    assert verify_warning(CANONICAL_WARNING, bad).verdict == Verdict.MISMATCH


def test_warning_extra_whitespace_matches():
    bloated = CANONICAL_WARNING.replace(" ", "  ").replace("\n", "\n\n")
    assert verify_warning(CANONICAL_WARNING, bloated).verdict == Verdict.MATCH


def test_warning_misspelling_mismatch():
    bad = CANONICAL_WARNING.replace("Surgeon General", "Surgeon Generel")
    assert verify_warning(CANONICAL_WARNING, bad).verdict == Verdict.MISMATCH


def test_warning_unreadable_when_found_missing():
    assert verify_warning(CANONICAL_WARNING, None).verdict == Verdict.UNREADABLE
