# Extraction Spike (tesseract)

Goal: decide whether self-hosted tesseract meets the ~3 s warm extraction
budget at acceptable accuracy on 5 representative label categories, without
any external vision API (egress/firewall constraint per the take-home
stakeholder notes).

## Run (host has no system tesseract + no passwordless sudo, so run in a
container — the same base image the deployment Dockerfile uses)

```bash
docker run --rm -v "$PWD":/work -w /work python:3.12-slim bash -c '
  apt-get update -qq && apt-get install -y -qq tesseract-ocr tesseract-ocr-eng >/dev/null &&
  pip install -q pytesseract pillow &&
  python spike/make_labels.py &&
  python spike/run_spike.py
'
```

See `SPIKE_REPORT.md` for results and verdict.
