# TTB Alcohol Label Verification — Take-Home Prototype

**Prototype disclaimer:** this is a standalone proof of concept built for a
USAJOBS take-home assessment (Treasury, Departmental Offices, IT Specialist
(Artificial Intelligence), announcement `26-DO-12891471-DH`). It is decision
support, **not** a COLA integration, a final regulatory determination, or a
production federal system. Scope is deliberately limited to distilled
spirits (see `docs/REQUIREMENTS.md`).

## Workflow

1. Reviewer fills in the "application" data for a label (brand, class/type,
   ABV/proof, net contents, bottler+address, country of origin if imported,
   government warning) — or clicks one of 4 bundled demo cases instead.
2. Reviewer uploads the label image (PNG or JPEG, up to 8 MB).
3. The server OCRs the image (self-hosted tesseract), deterministically
   compares each extracted field against the application data, and returns
   a results table: expected value, extracted value, status
   (Pass/Fail/Needs Review, shown with color **and** icon **and** text),
   and a plain-language explanation for every field — plus an overall
   verdict with the same three-way vocabulary.

## Features

- 7 required TTB fields, each with a field-specific deterministic comparison
  policy (tolerant text match, numeric-with-tolerance, strict verbatim —
  see `docs/REQUIREMENTS.md` for the full table).
- Every result is explained; nothing is an opaque score.
- Overall status uses real three-way precedence (Fail on a genuine mismatch;
  Needs Review when nothing failed but something is uncertain/unreadable;
  Pass only when everything is confidently verified) — not a Pass/Fail
  binary that would hide "we couldn't read this."
- 4 bundled one-click demo cases: compliant match, harmless brand-formatting
  difference, material ABV mismatch, unreadable image.
- No login, no evaluator-supplied API key, no persistence of uploaded images.
- `/api/verify` JSON endpoint alongside the HTML UI.

## Architecture

See `docs/ARCHITECTURE.md` for the full diagram, layer boundaries, and the
deployment decision record. Short version: OCR (probabilistic, isolated in
`extract.py`) feeds a purely deterministic comparison layer
(`verify.py` + `verifiers/*.py`, zero I/O, no model) — the two are cleanly
separated so the audit trail from "what tesseract read" to "why this field
passed/failed" is always inspectable.

## Prerequisites

- Python 3.12+
- [tesseract-ocr](https://github.com/tesseract-ocr/tesseract) (system
  package) for real OCR. Not required to run the test suite or browse the
  UI — without it, the app degrades gracefully to Needs Review on every
  field rather than crashing (see "Known limitations").
- Docker, if you'd rather not install tesseract locally (recommended — see
  below).

## Local setup and run

**Option A — Docker (includes tesseract, closest to the deployed environment):**
```bash
docker build -t label-verifier .
docker run --rm -p 8080:8080 label-verifier
# open http://localhost:8080
```

**Option B — local Python venv (tesseract must be installed separately, e.g.
`sudo apt install tesseract-ocr tesseract-ocr-eng` / `pacman -S tesseract
tesseract-data-eng`):**
```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/uvicorn label_verifier.app:app --reload
# open http://127.0.0.1:8000
```

## Required environment variables

**None.** There are no API keys or credentials of any kind — extraction is
self-hosted tesseract, not an external vision API.

## Tests

```bash
.venv/bin/pytest -v
```

103 tests (99 always run + 4 real-OCR demo-case assertions that
`skip` automatically when tesseract isn't installed, e.g. on a bare host —
see `tests/test_demo_cases_real_ocr.py`). To run the full suite including
those 4 with a real tesseract binary:
```bash
docker build -t label-verifier .
docker run --rm -v "$PWD":/work -w /work label-verifier bash -c 'pip install -q pytest httpx && pytest -v'
```

Test breakdown: RULE-layer unit tests (models, normalization, 7 verifiers,
orchestrator, latency smoke), extraction field-splitter unit tests,
aggregation/reporting tests, FastAPI app tests (upload validation — bad
content-type, empty file, oversized file; end-to-end pass/fail/needs-review
paths via a monkeypatched extractor; service-error handling that confirms no
result is fabricated on a crash), and the 4 required demonstration
scenarios against real OCR.

## Deployment

See `SUBMISSION_HANDOFF.md` for the live deployed URL. Deployed via
`gcloud run deploy --source .` (Google Cloud Run) from the `Dockerfile` in
this repo — see `docs/ARCHITECTURE.md` for why Cloud Run was chosen over the
alternatives considered.

## Inputs and outputs

**Input:** 7 text fields (brand, class/type, alcohol content, net contents,
bottler/address, country of origin, government warning) + an import
checkbox + one PNG/JPEG image, OR a one-click demo case (no input needed).

**Output:** a results table — one row per field with expected value,
extracted value, status chip (Pass/Fail/Needs Review — color + icon + text),
and an explanation sentence — plus an overall status banner with its own
explanation, and the measured processing time for that request.

## Comparison-policy summary

See `docs/REQUIREMENTS.md` "Field-specific verification policy" for the full
table (brand: tolerant; class/type: tolerant with subtype-specificity;
alcohol: ±0.1% ABV with proof↔ABV conversion; net contents: ±1% mL;
bottler/address: tolerant with address-presence check; country: tolerant,
NOT_REQUIRED for domestic; government warning: strict verbatim text with
mandatory all-caps prefix, formatting checks explicitly disclosed as
unevaluated).

## Official TTB sources

See `docs/REQUIREMENTS.md` "Official TTB sources used" for the full list of
URLs and the one documented limitation (live TTB page fetches timed out
during development; the canonical warning text is from well-established
statutory wording, not a live re-verification).

## Assumptions

1. "Application" values are typed in by the reviewer for this prototype —
   no live COLA integration (explicit non-goal).
2. The ~5 s target is end-to-end, per single label, on a warm deployed
   instance; measured and displayed per-request rather than assumed.
3. Distilled spirits only for v1 (governing prompt's explicit scope
   narrowing) — beer/wine mentioned in the informal instructions repo are
   deferred, not silently dropped (see `docs/REQUIREMENTS.md`).
4. No persistent storage of any kind — every request is stateless.
5. A domestic product (no `is_import` flag) makes country-of-origin
   `NOT_REQUIRED`, per TTB guidance that origin statements are
   import-specific.

## Known limitations

- **Heuristic extraction, not a trained layout model.** `extract.py` assumes
  brand is the first OCR line and class/type the second; long brand names
  that word-wrap across multiple lines will not be reconstructed correctly.
  Documented and demonstrated in `spike/SPIKE_REPORT.md`.
- **Warning formatting (bold/type-size/contrast/spacing) is never
  evaluated** — a text-only OCR pipeline structurally cannot assess it. The
  UI always discloses this explicitly on the warning field rather than
  implying those checks passed.
- **No image preprocessing** (deskew, glare correction, perspective
  correction) — a real photographed label under heavy degradation can
  produce OCR misreads at the punctuation level (observed and documented in
  the spike report), which the strict warning verifier will correctly (if
  conservatively) flag as a mismatch rather than silently accept.
- **Single-image only** — no batch upload (documented stretch goal, not
  built, per the governing prompt's explicit "core before stretch" priority).
- Not a substitute for a human TTB reviewer's judgment on edge cases; it is
  decision support.

## Security and privacy notes

- No credentials or API keys anywhere in source, config, or client code —
  extraction is self-hosted tesseract with zero external calls.
- Uploaded images are processed entirely in memory (`BytesIO`/PIL `Image`)
  and are never written to disk, logged, or persisted in any store.
- No accounts, no login, no session state, no cookies used for
  authentication (there is none).
- Upload validated by content-type and an 8 MB size cap before any
  processing occurs.
- Full git history was scanned for secrets/PII before this repo was made
  public (see `SUBMISSION_HANDOFF.md` for the scan command and result).

## Deferred features (stretch goals, not attempted)

Batch/multi-image processing, exportable JSON/CSV review report beyond the
existing `/api/verify` JSON endpoint, image-quality diagnostics, perspective
correction/glare handling/preprocessing, beer/wine-specific rules.

## Status

- [x] RULE layer (7 deterministic field verifiers + orchestrator, TDD)
- [x] Extraction spike — tesseract, ADOPT verdict (see `spike/SPIKE_REPORT.md`)
- [x] Extraction integration (`extract.py`)
- [x] Aggregation/reporting layer (`aggregate.py`)
- [x] Web UI (`app.py`, FastAPI + Jinja2)
- [x] 4 bundled demonstration cases, verified against real OCR
- [x] Deployment — see `SUBMISSION_HANDOFF.md` for the live URL
