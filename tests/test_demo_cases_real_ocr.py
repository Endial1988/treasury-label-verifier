"""Strong end-to-end assertions on the 4 bundled demo cases using REAL
tesseract OCR (not a monkeypatched stub). Skipped automatically when
tesseract isn't installed (e.g. this repo's dev host) — run via Docker
(see Dockerfile / spike/README.md) or in an environment with tesseract-ocr
installed to actually exercise these.
"""
import shutil

import pytest
from fastapi.testclient import TestClient

from label_verifier.app import app

pytestmark = pytest.mark.skipif(
    shutil.which("tesseract") is None,
    reason="tesseract binary not installed in this environment; see spike/README.md",
)

client = TestClient(app)

_EXPECTED_OVERALL = {
    "compliant": "pass",
    "brand_format": "pass",
    "material_mismatch": "fail",
    "unreadable": "needs_review",
}


@pytest.mark.parametrize("case_id, expected_overall", _EXPECTED_OVERALL.items())
def test_demo_case_real_ocr_overall_status(case_id, expected_overall):
    r = client.post(f"/demo/{case_id}")
    assert r.status_code == 200
    icon = {"pass": "PASS", "fail": "FAIL", "needs_review": "NEEDS REVIEW"}[expected_overall]
    assert f"Overall: {icon}" in r.text, f"{case_id}: expected overall={expected_overall}"
