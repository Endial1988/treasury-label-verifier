# Extraction Spike Report — Self-Hosted Tesseract

**Date:** 2026-07-21
**Tesseract version:** 5.5.0 (Debian `tesseract-ocr` package, run inside `python:3.12-slim` container — host has no system tesseract and no passwordless sudo, so the spike ran in Docker, which is the same base the deployment image uses)
**Budget:** warm p95 <= 3.0 s extraction residual (5 s end-to-end SLA minus RULE-layer/render overhead).

## Latency results

| Label | cold (s) | warm p50 (s) | warm p95 (s) | Fits 3 s? |
|---|---|---|---|---|
| clean.png | 0.253 | 0.255 | 0.283 | YES |
| glare.png | 0.279 | 0.245 | 0.274 | YES |
| photographed.jpg | 0.253 | 0.239 | 0.262 | YES |
| proof_only.png | 0.240 | 0.247 | 0.274 | YES |
| title_case.png | 0.250 | 0.249 | 0.254 | YES |

Full run log: `spike/spike.log`. All five categories finish in under ~0.3 s warm — an order of magnitude inside the 3 s residual budget.

**Correction (2026-07-21):** the first version of this report was written from a
truncated console preview and claimed the full GOVERNMENT WARNING text was
verified verbatim on every category. It wasn't — the label generator drew the
warning as a single unwrapped line, which ran off the 600 px canvas and was
silently clipped, so OCR only ever saw the first ~50 characters. Fixed the
generator to word-wrap to the canvas width, regenerated all label images, and
reran the spike. The numbers and observations below are from that corrected
run.

## Accuracy observations

- **clean.png:** every field read correctly, including the full two-sentence GOVERNMENT WARNING text verbatim (now genuinely verified against `CANONICAL_WARNING`, not just eyeballed from a truncated preview).
- **glare.png:** the synthetic glare wash (bottom-third translucent overlay) was light enough that tesseract still read every field correctly, including the warning. A harsher glare (near-saturating) would likely degrade this — the deployed system should still treat low-confidence tesseract output as `LOW_CONFIDENCE`/`UNREADABLE` rather than trusting it blindly (see Task 15).
- **title_case.png:** correctly extracted the warning text verbatim, including preserving `Government Warning:` in title case rather than normalizing it — confirms the strict warning verifier (Task 9) correctly flags this as MISMATCH.
- **proof_only.png:** correctly extracted `90 Proof` with no `%` figure present — confirms the alcohol verifier's proof-to-ABV fallback path is needed and exercised.
- **photographed.jpg:** despite -3° rotation, posterization, and blur, all fields were still legible, with one small misread: the final period of the warning came back as a comma ("...health problems,"). The strict warning verifier correctly flags this as MISMATCH — which is the honest, intended behavior (a degraded image should not silently pass a verbatim-text check), but it means a real photographed label with this level of degradation would route to a human reviewer even when the true printed text is compliant. This is a genuine known limitation of whitespace-only strict matching against noisy OCR, not a bug — documented in README limitations.
- **Multi-line brand names:** at 44 pt, "OLD TOM DISTILLERY" (19 characters) no longer fits on one line within the wrapped canvas and now renders as two lines ("OLD TOM" / "DISTILLERY"). The extraction adapter's "brand = first non-empty line" heuristic (`extract.py`) does not merge these back into one field — this is a real, documented gap in the heuristic field-splitter for long single-field text, separate from OCR accuracy itself. Noted in README limitations; the two bundled demo labels that exercise the brand field ("STONE'S THROW", 13 characters) do not trigger this, so the bundled demos still pass/fail correctly.

## Verdict

**ADOPT** — self-hosted tesseract comfortably meets the latency budget (warm p95 ~0.25-0.28 s vs. a 3 s residual, i.e. ~90% headroom) and, once the label generator was fixed to actually render full-width text, reads all 5 synthetic categories correctly except for one punctuation-level misread under heavy synthetic degradation (photographed.jpg). Document harsher glare/blur/rotation as known-degraded inputs that the extraction adapter should route to `LOW_CONFIDENCE`/`UNREADABLE` rather than a false `MATCH` — the RULE layer already has verdicts for this; the extraction adapter (Task 15) must actually emit them when tesseract confidence is low, since these synthetic images are easier than a real photographed label.

Egress note: tesseract is fully self-hosted (no external vision API call), satisfying the firewall/egress constraint noted in the take-home stakeholder context.

## Implications for the next phase

- The RULE layer (already implemented, 69/69 tests passing) is unaffected; it consumes whatever text the extractor produces.
- Extraction integration shape: `extract_fields(image) -> dict[field, ExtractedField]` behind the verifier registry, swappable without touching verifiers (Task 15).
- Deployment implication: the production container must install `tesseract-ocr` + `tesseract-ocr-eng` as an OS package (see `Dockerfile`), not rely on a Python-only wheel.
