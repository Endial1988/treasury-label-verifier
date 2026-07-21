# Submission Handoff

**Status: NOT YET SUBMITTED — awaiting your review and explicit approval per
the governing execution prompt. No email or form has been sent.**

## Candidate

- Candidate: Harlan Asberry
- USAJOBS position: IT Specialist (Artificial Intelligence)
- Department: U.S. Department of the Treasury, Departmental Offices
- Announcement number: `26-DO-12891471-DH`
- USAJOBS control number: `858700600`

## Repository and deployment

- **Source repository:** https://github.com/Endial1988/treasury-label-verifier (public)
- **Latest commit SHA:** `942ef60e7bcdc75288eb5429ded4c93e7fad6064`
- **Deployed application URL:** **PENDING.** Cloud Run deployment was
  deliberately held back this session, pending your go-ahead — it would
  create billable resources under your real Google account, and you asked
  to hold off. Everything else (repo, code, tests, docs) is complete and
  pushed. To finish: `gcloud run deploy --source .` from the repo root
  (Dockerfile already present and tested locally) under whichever GCP
  project you choose, then this section gets the resulting URL and
  Phase 4 re-verification (Section "Demonstration instructions" below, run
  against the deployed URL instead of localhost) needs to be repeated.

## Test / lint / security-scan results

```
$ .venv/bin/pytest -v
...
99 passed, 4 skipped in 0.42s
```
(The 4 skips are `tests/test_demo_cases_real_ocr.py` — they require the
`tesseract` binary, not installed on this dev host by design; see below.)

```
$ docker build -t label-verifier:dev .   # tesseract-ocr baked into the image
$ docker run --rm -v "$PWD":/work -w /work label-verifier:dev \
    bash -c 'pip install -q pytest httpx && pytest -v'
...
103 passed in <2s
```
All 103 tests pass with real tesseract, including the 4 real-OCR
demonstration-scenario assertions (`test_demo_cases_real_ocr.py`):
`compliant`→pass, `brand_format`→pass, `material_mismatch`→fail,
`unreadable`→needs_review — verified against the actual required outcome
for each of the 4 governing-prompt demo scenarios, not just "didn't crash."

**Secret scan:** full git history scanned for `.env`/credential/key
filenames and common secret-pattern regexes (AWS keys, private key
headers, `api_key=`/`password=` literals, OpenAI/GitHub token prefixes).
No matches. No personal application materials or private email content
were committed at any point (the repo was built directly in a new
directory, never containing the original take-home email or personal
correspondence).

**No linter was configured** — the codebase is small (≈900 LOC across 25
Python files); `pytest --collect-only` and successful imports across the
full suite serve as the practical syntax/type-sanity check. This is a
disclosed scope trade-off, not an oversight.

## Demonstration instructions

Once deployed, open the URL and either:
- Click one of the 4 bundled demo-case buttons (no upload needed), or
- Fill in the application-data form and upload a PNG/JPEG label image.

Locally (pre-deployment) verification, run instead:
```bash
docker build -t label-verifier .
docker run --rm -p 8080:8080 label-verifier
# open http://localhost:8080, click each of the 4 demo cases
```
Expected outcomes (verified this session, see test output above):
1. **Compliant** → Pass (all 7 fields match)
2. **Harmless brand-formatting difference** → Pass (case/punctuation only)
3. **Material ABV mismatch** → Fail
4. **Unreadable image** → Needs Review (no field silently guessed)

## Known limitations

See `README.md` "Known limitations" for the full list. Headline items:
heuristic (not trained-model) field extraction assumes brand is the first
OCR line; warning *formatting* (bold/size/contrast) is structurally
unevaluable from text-only OCR and is always disclosed as such, never
silently passed; no image preprocessing (deskew/glare correction); single
image only, no batch (documented stretch goal).

## Late submission and form-outage explanation

The July 1, 2026 application-received email instructed me to review an
attachment for a required take-home assessment within one week; the email
itself contained no attachment, only a link to a Microsoft submission form.
I did not complete the assessment within that original window. When
revisited, the Microsoft form reported it was no longer operational due to a
denial-of-service attack, and redirected candidates to email their name,
email address, source repository URL, and deployed application URL to
`take-home-test@treasury.gov` instead. This submission follows that revised
instruction. The assessment's own instructions (via the linked GitHub
instructions repository) describe the exercise as intended to take under an
hour and to test general agentic-coding ability at a high level — this
submission prioritizes a complete, credible, independently-produced working
prototype over exhaustive scope, consistent with that stated intent.

## Draft email (NOT sent — for your review)

To: take-home-test@treasury.gov
Subject: Take-Home Assessment Submission — Harlan Asberry — Announcement 26-DO-12891471-DH

```
Name: Harlan Asberry
Email: [your preferred contact email]
Announcement number: 26-DO-12891471-DH
Source repository: https://github.com/Endial1988/treasury-label-verifier
Deployed application URL: [PENDING — to be filled in after Cloud Run deployment]

Note on timing: the original application-received email (July 1) linked to a
Microsoft submission form for this assessment rather than including the
referenced attachment directly. On revisiting the form, it reported an
outage due to a denial-of-service attack and redirected candidates to this
email address with the fields above. This submission follows that revised
instruction.

The prototype verifies TTB distilled-spirits label images against submitted
application data across the 7 required fields (brand, class/type, ABV/proof,
net contents, bottler/address, country of origin, government warning),
using self-hosted OCR feeding a deterministic, field-specific comparison
layer, with every result explained rather than reported as an opaque score.
Repository README and docs/ describe setup, architecture, assumptions, and
known limitations in full.

Thank you for your consideration.

Harlan Asberry
```

**Do not send this email or fill in the deployed-URL placeholder and submit
without your explicit review and approval — per your original instructions,
I am stopping here for that review.**
