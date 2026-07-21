# TTB Alcohol Label Verification — Take-Home Prototype

**Prototype disclaimer:** this is a standalone proof of concept for a USAJOBS
take-home assessment (Treasury, IT Specialist (AI), announcement
`26-DO-12891471-DH`). It is **not** a COLA integration, a final regulatory
decision engine, or a production federal system.

## Status
- [x] Repo initialized
- [ ] RULE layer (deterministic verification)
- [ ] Extraction spike (tesseract latency)
- [ ] Extraction integration
- [ ] Web UI + deployment

## Local dev
```bash
python -m pip install -e ".[dev]"
pytest
```
