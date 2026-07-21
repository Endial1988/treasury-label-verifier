"""Time tesseract on each label category, cold and warm.

Cold = first call after process start. Warm = subsequent calls, steady state.
The SLA-relevant number is warm p95 vs. the ~3.0 s extraction residual
(5 s end-to-end budget minus RULE-layer and network/render overhead).
"""
import statistics
import time
from pathlib import Path

import pytesseract
from PIL import Image

LABELS_DIR = Path(__file__).parent / "labels"
N_WARM = 10
RESIDUAL_S = 3.0


def pct(xs: list[float], p: float) -> float:
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round((p / 100.0) * (len(xs) - 1)))))
    return xs[k]


def time_one(path: Path) -> tuple[float, str]:
    img = Image.open(path)
    t0 = time.perf_counter()
    text = pytesseract.image_to_string(img)
    return time.perf_counter() - t0, text


def main() -> int:
    print(f"tesseract version: {pytesseract.get_tesseract_version()}")
    paths = sorted(LABELS_DIR.glob("*"))
    if not paths:
        print("no labels found - run make_labels.py first")
        return 1

    print(f"\n{'label':18} {'cold(s)':>9} {'warm_p50(s)':>12} {'warm_p95(s)':>12} {'fits 3s?':>9}")
    print("-" * 64)
    for p in paths:
        cold, cold_text = time_one(p)
        warm_times, warm_texts = [], []
        for _ in range(N_WARM):
            t, txt = time_one(p)
            warm_times.append(t)
            warm_texts.append(txt)
        p50, p95 = statistics.median(warm_times), pct(warm_times, 95)
        fits = p95 <= RESIDUAL_S
        print(f"{p.name:18} {cold:9.3f} {p50:12.3f} {p95:12.3f} {'YES' if fits else 'NO':>9}")
        print(f"  --- extracted text ({p.name}) ---")
        print("  " + warm_texts[0].replace("\n", "\n  ")[:500])
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
