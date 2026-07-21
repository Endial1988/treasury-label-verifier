# Architecture

## Overview

```
Browser (form + upload)
        |
        v
FastAPI app (app.py) ---- validates upload type/size, never persists image
        |
        v
extract.py  --------------------  OCR / vision extraction (probabilistic)
   tesseract (self-hosted, no external API) -> raw text
   fields_from_text(): pure regex/line-position heuristic field splitter
   -> ExtractionResult { field: ExtractedField(text, confidence) }
        |
        v
verify.py  ---------------------  deterministic RULE layer (no model, no I/O)
   verifiers/{brand,class_type,alcohol,net_contents,bottler,country,warning}.py
   -> VerifyResult { per-field six-way Verdict, three-way overall }
        |
        v
aggregate.py  ------------------  reporting layer
   maps six-way Verdict -> pass/fail/needs_review + human explanation
   -> Report (rendered as HTML table, or JSON via /api/verify)
```

The extraction layer is the only probabilistic component. Everything
downstream of it — normalization, comparison, status precedence, and
explanation text — is deterministic Python with no model in the loop,
per governing-prompt engineering principle #2. `extract.py`'s AI output
(`ExtractedField`) is a strict pydantic schema; extraction never invents a
value — an unmatched field is `text=None`, which flows to `UNREADABLE` or
`MISSING`, never a guess.

## Layer boundaries

- **UI/input layer** (`app.py`, `templates/`): FastAPI + Jinja2, no JS
  framework. Validates content-type (`image/png`, `image/jpeg` only) and
  size (8 MB cap) before touching the image. All error paths return a
  friendly message and a non-500 status where the failure is the caller's
  fault (bad upload) and a 500 with an explicit "no result was produced"
  message where it's a service fault — the app never fabricates a
  Pass/Fail/Needs-Review verdict on error.
- **Image validation/preprocessing**: content-type + size check only; no
  perspective correction or glare handling in this prototype (documented
  stretch goal, not attempted).
- **OCR/vision extraction adapter** (`extract.py`): isolates the only I/O +
  probabilistic call (tesseract via `pytesseract`) behind
  `extract_fields(image_bytes) -> ExtractionResult`. The text-parsing half
  (`fields_from_text`) is a pure function with no I/O, so it's unit-tested
  without tesseract installed; the I/O half is exercised end-to-end via
  Docker (see `spike/README.md`, `tests/test_demo_cases_real_ocr.py`).
- **Structured extraction schema**: `ExtractedField`/`ExtractionResult`
  (pydantic) — validated, typed, never partially-populated with guessed data.
- **Deterministic normalization/comparison** (`normalize.py`,
  `verifiers/*.py`): pure functions, zero I/O, one verifier per field,
  uniform signature `(expected, found) -> FieldVerdict`.
- **Result aggregation/explanation** (`verify.py`, `aggregate.py`):
  `verify.py` computes the three-way overall status from the six-way
  per-field verdicts (a real `MISMATCH` anywhere -> Fail; no mismatch but
  something uncertain -> Needs Review; otherwise Pass — see the audit note
  in `docs/superpowers/plans/2026-07-05-spike-and-rule-layer.md` Addendum
  for why this must NOT collapse to binary). `aggregate.py` renders that
  into the public `pass`/`fail`/`needs_review` vocabulary with a
  human-readable explanation per field, and explicitly discloses that
  warning-text *formatting* (bold/size/contrast) is not evaluated by a
  text-only extractor — never silently treated as passed.
- **Security and data lifecycle**: no accounts, no API keys anywhere
  (self-hosted tesseract has none to leak), uploaded bytes live only in a
  request-scoped `BytesIO`/PIL `Image` and are never written to disk or a
  database.

## Deployment stack decision record

**Chosen:** Docker container (tesseract-ocr baked in) on Google Cloud Run.

**Why:** Phase 0 environment inspection found `gcloud` already authenticated
to an existing Google account on this machine, and the Docker daemon already
running — both usable without introducing new credentials or accounts.
Cloud Run accepts a container directly (`gcloud run deploy --source .`),
serves a public HTTPS URL with no login by default, and scales to zero when
idle (no standing cost between evaluator visits). This satisfies the
governing-prompt Phase 0 instruction to prefer the fastest reliable stack
already authenticated/installed, over introducing new infrastructure.

**Rejected:**
- **Azure** — explicitly a non-goal unless it's the fastest route; nothing
  Azure-related was pre-authenticated on this machine, so it would have
  meant new account setup.
- **GitHub Pages / static hosting** — the app has a real Python backend
  (OCR, deterministic comparison) and cannot run as static content.
- **Host-native deployment (no container)** — the host has no system
  tesseract and no passwordless sudo to install it; the container path
  installs tesseract inside its own image instead, which is also exactly
  what the spike used, so latency numbers transfer directly.

**Egress note:** tesseract is fully self-hosted; the app makes no outbound
calls to any external OCR/vision API at request time, which sidesteps the
firewall/egress constraint noted in the take-home stakeholder context.

## Known architectural limitations

- `extract.py`'s field splitter is heuristic (line position + regex), not a
  trained layout model. It assumes brand is the first non-empty OCR line
  and class/type the second — this breaks for label layouts that don't
  follow that convention, and for long brand names that word-wrap across
  multiple OCR lines (observed in the spike; see `spike/SPIKE_REPORT.md`).
- Government-warning *formatting* checks (bold, type size, separation,
  contrast, legibility) are structurally out of reach for a text-only OCR
  pipeline and are never evaluated — always disclosed, never silently
  passed.
- No image preprocessing (deskew, glare correction) — documented stretch
  goal.
