# Extraction Spike Report — Self-Hosted Tesseract

**Date:** 2026-07-21
**Tesseract version:** 5.5.0 (Debian `tesseract-ocr` package, run inside `python:3.12-slim` container — host has no system tesseract and no passwordless sudo, so the spike ran in Docker, which is the same base the deployment image uses)
**Budget:** warm p95 <= 3.0 s extraction residual (5 s end-to-end SLA minus RULE-layer/render overhead).

## Latency results

| Label | cold (s) | warm p50 (s) | warm p95 (s) | Fits 3 s? |
|---|---|---|---|---|
| clean.png | 0.187 | 0.166 | 0.170 | YES |
| glare.png | 0.162 | 0.165 | 0.171 | YES |
| photographed.jpg | 0.151 | 0.148 | 0.149 | YES |
| proof_only.png | 0.159 | 0.159 | 0.176 | YES |
| title_case.png | 0.162 | 0.165 | 0.172 | YES |

Full run log: `spike/spike.log`. All five categories finish in well under 200 ms warm — over an order of magnitude inside the 3 s residual budget.

## Accuracy observations

- **clean.png:** all fields read correctly, including the full two-sentence GOVERNMENT WARNING text verbatim.
- **glare.png:** the synthetic glare wash (bottom-third translucent overlay) was light enough that tesseract still read every field correctly, including the warning. A harsher glare (near-saturating) would likely degrade this — the deployed system should still treat low-confidence tesseract output as `LOW_CONFIDENCE`/`UNREADABLE` rather than trusting it blindly (see Task 15).
- **title_case.png:** correctly extracted the warning text verbatim, including preserving `Government Warning:` in title case rather than normalizing it — confirms the strict warning verifier (Task 9) will correctly flag this as MISMATCH.
- **proof_only.png:** correctly extracted `90 Proof` with no `%` figure present — confirms the alcohol verifier's proof-to-ABV fallback path is needed and exercised.
- **photographed.jpg:** despite -3° rotation, posterization, and blur, the text was still fully legible to tesseract on this synthetic image. Real photographed labels (uneven lighting, deeper blur, extreme angles) are expected to be harder; this is a known limitation, not something this spike proves out.

## Verdict

**ADOPT** — self-hosted tesseract comfortably meets the latency budget (warm p95 ~0.15-0.18 s vs. a 3 s residual, i.e. ~94% headroom) and reads all 5 synthetic categories correctly, including the two adversarial cases that matter most for this app (title-case warning prefix, proof-only ABV). Document harsher glare/blur/rotation as known-degraded inputs that the extraction adapter should route to `LOW_CONFIDENCE`/`UNREADABLE` rather than a false `MATCH` — the RULE layer already has verdicts for this; the extraction adapter (Task 15) must actually emit them when tesseract confidence is low, since these synthetic images are easier than a real photographed label.

Egress note: tesseract is fully self-hosted (no external vision API call), satisfying the firewall/egress constraint noted in the take-home stakeholder context.

## Implications for the next phase

- The RULE layer (already implemented, 69/69 tests passing) is unaffected; it consumes whatever text the extractor produces.
- Extraction integration shape: `extract_fields(image) -> dict[field, ExtractedField]` behind the verifier registry, swappable without touching verifiers (Task 15).
- Deployment implication: the production container must install `tesseract-ocr` + `tesseract-ocr-eng` as an OS package (see `Dockerfile`), not rely on a Python-only wheel.
