# Requirements

Classified per the governing execution prompt's precedence order:
official assessment instructions/TTB sources > governing prompt > this
document. Source material: `treasurytakehome-rgb/instructions` README
(official assessment repo) and the official TTB labeling pages listed below,
read as external, untrusted-but-authoritative stakeholder evidence — not
copied verbatim, and no other candidate's implementation was consulted.

## Explicit deliverables

- Source-code repository containing all source code. ✅ (this repo)
- README with setup and run instructions. ✅ `README.md`
- Brief documentation of approach, tools, and assumptions. ✅ this file + `docs/ARCHITECTURE.md` + README
- Publicly accessible deployed working prototype. — see `SUBMISSION_HANDOFF.md` for the deployed URL

## Core functional requirements

- Structured expected/application data input. ✅ web form (7 fields + import flag)
- Single label-image upload, PNG and JPEG. ✅ validated by content-type + size
- OCR/vision extraction into structured fields. ✅ tesseract + heuristic field-splitter (`extract.py`)
- Side-by-side expected-versus-extracted results. ✅ results table
- Field-level status and explanation. ✅ `aggregate.py` — every field carries a status and a human-readable explanation, never an opaque score
- Overall Pass / Fail / Needs Review decision. ✅ three-way precedence in `verify.py` + `aggregate.py`
- Useful error handling. ✅ bad file type, empty file, oversized file, corrupt image, OCR failure — all handled without crashing or fabricating a result
- At least one bundled/selectable demonstration case. ✅ 4 one-click demo cases

## Minimum initial fields (all implemented, distilled spirits scope)

Brand name, class/type, ABV (+ optional proof), net contents, bottler/producer
name+address, country of origin, government health warning statement.

## Field-specific verification policy (implemented in `src/label_verifier/verifiers/`)

| Field | Policy | Module |
|---|---|---|
| Brand | Case/whitespace/punctuation/™®-tolerant; accent-stripped | `brand.py` |
| Class/type | Normalized; specific-subtype-aware (bourbon vs. generic whiskey is drift, not synonymy) | `class_type.py` |
| Alcohol | ±0.1 %ABV tolerance; proof↔ABV conversion; internal %/proof consistency check | `alcohol.py` |
| Net contents | ±1% tolerance on canonical mL; ml/L/fl oz unit-agnostic | `net_contents.py` |
| Bottler/address | Tolerant name match; state name↔abbreviation normalized; flags missing address component | `bottler.py` |
| Country of origin | NOT_REQUIRED for domestic; MISSING if import and absent; tolerant name/code match | `country.py` |
| Government warning | Whitespace-only normalization; verbatim text + all-caps `GOVERNMENT WARNING:` prefix required; formatting (bold/size/contrast) explicitly reported as unverifiable, never silently passed | `warning.py` + `aggregate.py` |
| Missing/low-confidence extraction | Routed to `needs_review`, never `pass`, never invented | `verify.py` overall precedence |

## Nonfunctional requirements

- Simple, obvious interface. ✅ single page, plain HTML form, no JS framework
- ~5 s per label; measure and report honestly. ✅ measured and displayed per request (`elapsed_ms`); spike measured extraction alone at warm p95 ≈ 0.25–0.28 s (see `spike/SPIKE_REPORT.md`)
- No credentials/API keys in source or client code. ✅ self-hosted tesseract, no API key of any kind is used
- Images processed transiently, no persistence. ✅ in-memory `BytesIO`, never written to disk
- Status never color-alone. ✅ text + icon + color chip
- Keyboard accessibility, readable contrast. ✅ native form controls, labeled inputs, visible focus outline
- Deterministic, auditable verification separated from probabilistic extraction. ✅ `extract.py` (probabilistic OCR) is fully decoupled from `verifiers/*.py` (pure deterministic code, zero I/O)

## Stretch goals (not attempted — documented, not silently dropped)

Batch/multi-image processing, exportable JSON/CSV report (the `/api/verify`
JSON endpoint exists as a byproduct of the architecture but batch export was
not built), image-quality diagnostics, perspective correction/glare
handling, additional beverage-type rules (beer/wine).

## Explicit non-goals (per governing prompt)

COLA integration, user accounts/auth, persistent database, FedRAMP
authorization, complete TTB regulatory coverage, custom model training,
large-scale batch queues, enterprise Azure infrastructure (Cloud Run was
used instead — see `docs/ARCHITECTURE.md` decision record), runtime
multi-agent deliberation.

## Official TTB sources used

- https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/labeling
- https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-brand-label
- https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning
- https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-alcohol-content
- https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-checklist
- https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/anatomy-of-a-distilled-spirits-label-tool

**Limitation:** the TTB warning-statement and checklist pages timed out on
every live fetch attempted during development. The canonical warning text in
`warning_data.py` is the well-established 27 CFR §16.21 statutory wording
from training knowledge, not a live re-verification — documented here rather
than silently assumed correct.
