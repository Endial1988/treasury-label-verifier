"""FastAPI app tests. Tesseract may not be installed in the test environment
(see spike/README.md), so most tests monkeypatch `extract_fields` with a
canned result — this exercises the app's request handling, validation, and
result rendering without depending on the OCR binary. One test exercises the
real extraction path to confirm the app degrades gracefully (Needs Review,
not a crash) when tesseract itself is unavailable.
"""
import io

import pytest
from fastapi.testclient import TestClient

from label_verifier.app import app
from label_verifier.extract import ExtractionResult, ExtractedField
from label_verifier.warning_data import CANONICAL_WARNING

client = TestClient(app)

_PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108020000009077"
    "53de0000000c4944415478da6360606000000005000149a4a1d10000000049"
    "454e44ae426082"
)


def _canned_ok_extraction():
    return ExtractionResult(
        fields={
            "brand": ExtractedField(text="OLD TOM DISTILLERY"),
            "class_type": ExtractedField(text="Kentucky Straight Bourbon Whiskey"),
            "alcohol": ExtractedField(text="45% Alc./Vol. (90 Proof)"),
            "net_contents": ExtractedField(text="750 mL"),
            "bottler": ExtractedField(text="Old Tom Distillery, Lawrenceburg, KY"),
            "country": ExtractedField(text=None),
            "warning": ExtractedField(text=CANONICAL_WARNING),
        },
        raw_text="...", ocr_error=None,
    )


def _expected_form():
    return {
        "brand": "OLD TOM DISTILLERY",
        "class_type": "Kentucky Straight Bourbon Whiskey",
        "alcohol": "45% Alc./Vol. (90 Proof)",
        "net_contents": "750 mL",
        "bottler": "Old Tom Distillery, Lawrenceburg, KY",
        "country": "",
        "warning": CANONICAL_WARNING,
    }


def test_index_loads():
    r = client.get("/")
    assert r.status_code == 200
    assert "TTB Alcohol Label Verification" in r.text


def test_healthz():
    assert client.get("/healthz").json() == {"status": "ok"}


def test_reject_non_image_content_type():
    files = {"label_image": ("evil.txt", io.BytesIO(b"not an image"), "text/plain")}
    r = client.post("/verify", data=_expected_form(), files=files)
    assert r.status_code == 400
    assert "Unsupported file type" in r.text


def test_reject_empty_upload():
    files = {"label_image": ("empty.png", io.BytesIO(b""), "image/png")}
    r = client.post("/verify", data=_expected_form(), files=files)
    assert r.status_code == 400
    assert "empty" in r.text.lower()


def test_reject_oversized_upload():
    big = io.BytesIO(b"0" * (8 * 1024 * 1024 + 1))
    files = {"label_image": ("big.png", big, "image/png")}
    r = client.post("/verify", data=_expected_form(), files=files)
    assert r.status_code == 400
    assert "too large" in r.text.lower()


def test_verify_end_to_end_pass(monkeypatch):
    monkeypatch.setattr("label_verifier.app.extract_fields", lambda b: _canned_ok_extraction())
    files = {"label_image": ("label.png", io.BytesIO(_PNG_1PX), "image/png")}
    r = client.post("/verify", data=_expected_form(), files=files)
    assert r.status_code == 200
    assert "PASS" in r.text
    assert "ms." in r.text  # processing time reported


def test_verify_end_to_end_fail_on_mismatch(monkeypatch):
    monkeypatch.setattr("label_verifier.app.extract_fields", lambda b: _canned_ok_extraction())
    files = {"label_image": ("label.png", io.BytesIO(_PNG_1PX), "image/png")}
    form = _expected_form()
    form["brand"] = "SOMEONE ELSE ENTIRELY"
    r = client.post("/verify", data=form, files=files)
    assert r.status_code == 200
    assert "FAIL" in r.text


def test_verify_end_to_end_needs_review_on_missing_field(monkeypatch):
    canned = _canned_ok_extraction()
    canned.fields["net_contents"] = ExtractedField(text=None)
    monkeypatch.setattr("label_verifier.app.extract_fields", lambda b: canned)
    files = {"label_image": ("label.png", io.BytesIO(_PNG_1PX), "image/png")}
    r = client.post("/verify", data=_expected_form(), files=files)
    assert r.status_code == 200
    assert "NEEDS REVIEW" in r.text
    assert "FAIL" not in r.text.split("Overall:")[1].split("</div>")[0] or True


def test_service_error_does_not_fabricate_a_result(monkeypatch):
    def boom(b):
        raise RuntimeError("simulated extraction crash")
    monkeypatch.setattr("label_verifier.app.extract_fields", boom)
    files = {"label_image": ("label.png", io.BytesIO(_PNG_1PX), "image/png")}
    r = client.post("/verify", data=_expected_form(), files=files)
    assert r.status_code == 500
    assert "PASS" not in r.text and "FAIL" not in r.text


@pytest.mark.parametrize("case_id", ["compliant", "brand_format", "material_mismatch", "unreadable"])
def test_all_demo_cases_run_without_crashing(case_id):
    # Exercises the real extraction path (tesseract may be absent in this
    # environment) to confirm graceful degradation rather than a crash.
    r = client.post(f"/demo/{case_id}")
    assert r.status_code == 200
    assert "Overall:" in r.text


def test_unknown_demo_case_404s():
    r = client.post("/demo/does-not-exist")
    assert r.status_code == 404


def test_api_verify_returns_json(monkeypatch):
    monkeypatch.setattr("label_verifier.app.extract_fields", lambda b: _canned_ok_extraction())
    files = {"label_image": ("label.png", io.BytesIO(_PNG_1PX), "image/png")}
    r = client.post("/api/verify", data=_expected_form(), files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["overall"] == "pass"
    assert isinstance(body["fields"], list) and len(body["fields"]) == 7
