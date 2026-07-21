"""FastAPI web app: expected-data form + label upload -> verification report.

No login, no evaluator-supplied API key, no persistence. Uploaded images are
processed in memory (BytesIO) and never written to disk.
"""
from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, Form, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from label_verifier.aggregate import build_report, Report
from label_verifier.demo_cases import DEMO_CASES, DEMO_ASSETS_DIR
from label_verifier.extract import extract_fields
from label_verifier.verify import verify_label

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg"}

app = FastAPI(title="TTB Alcohol Label Verification (Prototype)")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/demo-assets", StaticFiles(directory=str(DEMO_ASSETS_DIR)), name="demo-assets")

FIELD_LABELS = {
    "brand": "Brand Name",
    "class_type": "Class / Type",
    "alcohol": "Alcohol Content (ABV / Proof)",
    "net_contents": "Net Contents",
    "bottler": "Bottler / Producer (Name & Address)",
    "country": "Country of Origin",
    "warning": "Government Warning Statement",
}


def _run_verification(expected: dict, is_import: bool, image_bytes: bytes) -> tuple[Report, float, str | None]:
    t0 = time.perf_counter()
    extraction = extract_fields(image_bytes)
    found = {field: ev.text for field, ev in extraction.fields.items()}
    result = verify_label(expected, found, is_import=is_import)
    report = build_report(result)
    elapsed = time.perf_counter() - t0
    return report, elapsed, extraction.ocr_error


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {
        "request": request,
        "field_labels": FIELD_LABELS,
        "demo_cases": DEMO_CASES,
        "error": None,
    })


@app.post("/verify", response_class=HTMLResponse)
async def verify(
    request: Request,
    brand: str = Form(""),
    class_type: str = Form(""),
    alcohol: str = Form(""),
    net_contents: str = Form(""),
    bottler: str = Form(""),
    country: str = Form(""),
    is_import: bool = Form(False),
    warning: str = Form(""),
    label_image: UploadFile = File(...),
):
    if label_image.content_type not in ALLOWED_CONTENT_TYPES:
        return templates.TemplateResponse(request, "index.html", {
            "request": request, "field_labels": FIELD_LABELS, "demo_cases": DEMO_CASES,
            "error": f"Unsupported file type '{label_image.content_type}'. Please upload a PNG or JPEG image.",
        }, status_code=400)

    image_bytes = await label_image.read()
    if len(image_bytes) == 0:
        return templates.TemplateResponse(request, "index.html", {
            "request": request, "field_labels": FIELD_LABELS, "demo_cases": DEMO_CASES,
            "error": "The uploaded file was empty. Please choose a label image and try again.",
        }, status_code=400)
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        return templates.TemplateResponse(request, "index.html", {
            "request": request, "field_labels": FIELD_LABELS, "demo_cases": DEMO_CASES,
            "error": "The uploaded file is too large (max 8 MB). Please upload a smaller image.",
        }, status_code=400)

    expected = {
        "brand": brand or None,
        "class_type": class_type or None,
        "alcohol": alcohol or None,
        "net_contents": net_contents or None,
        "bottler": bottler or None,
        "country": country or None,
        "warning": warning or None,
    }

    try:
        report, elapsed, ocr_error = _run_verification(expected, is_import, image_bytes)
    except Exception as e:
        # Never fabricate a result on a service error.
        return templates.TemplateResponse(request, "index.html", {
            "request": request, "field_labels": FIELD_LABELS, "demo_cases": DEMO_CASES,
            "error": f"Verification failed unexpectedly: {e}. No result was produced.",
        }, status_code=500)

    return templates.TemplateResponse(request, "result.html", {
        "request": request, "report": report, "field_labels": FIELD_LABELS,
        "elapsed_ms": round(elapsed * 1000), "ocr_error": ocr_error,
        "expected": expected,
    })


@app.post("/demo/{case_id}", response_class=HTMLResponse)
def run_demo(request: Request, case_id: str):
    case = DEMO_CASES.get(case_id)
    if case is None:
        return templates.TemplateResponse(request, "index.html", {
            "request": request, "field_labels": FIELD_LABELS, "demo_cases": DEMO_CASES,
            "error": f"Unknown demo case '{case_id}'.",
        }, status_code=404)

    image_path = DEMO_ASSETS_DIR / case["image"]
    image_bytes = image_path.read_bytes()
    report, elapsed, ocr_error = _run_verification(case["expected"], case["is_import"], image_bytes)

    return templates.TemplateResponse(request, "result.html", {
        "request": request, "report": report, "field_labels": FIELD_LABELS,
        "elapsed_ms": round(elapsed * 1000), "ocr_error": ocr_error,
        "expected": case["expected"], "demo_label": case["label"],
    })


@app.get("/healthz", response_class=JSONResponse)
def healthz():
    return {"status": "ok"}


@app.post("/api/verify", response_class=JSONResponse)
async def api_verify(
    brand: str = Form(""),
    class_type: str = Form(""),
    alcohol: str = Form(""),
    net_contents: str = Form(""),
    bottler: str = Form(""),
    country: str = Form(""),
    is_import: bool = Form(False),
    warning: str = Form(""),
    label_image: UploadFile = File(...),
):
    """JSON API — same logic as /verify, for programmatic/test access."""
    if label_image.content_type not in ALLOWED_CONTENT_TYPES:
        return JSONResponse({"error": f"unsupported content type '{label_image.content_type}'"}, status_code=400)
    image_bytes = await label_image.read()
    if not image_bytes:
        return JSONResponse({"error": "empty file"}, status_code=400)
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        return JSONResponse({"error": "file too large"}, status_code=400)

    expected = {
        "brand": brand or None, "class_type": class_type or None, "alcohol": alcohol or None,
        "net_contents": net_contents or None, "bottler": bottler or None,
        "country": country or None, "warning": warning or None,
    }
    try:
        report, elapsed, ocr_error = _run_verification(expected, is_import, image_bytes)
    except Exception as e:
        return JSONResponse({"error": f"verification failed: {e}"}, status_code=500)

    payload = report.model_dump()
    payload["elapsed_ms"] = round(elapsed * 1000)
    payload["ocr_error"] = ocr_error
    return JSONResponse(payload)
