"""Generate the 4 bundled demonstration label images required by the
governing take-home prompt Phase 3:
  1. compliant.png        - matches the application exactly -> Pass
  2. brand_format.png     - harmless brand case/punctuation difference -> Pass
  3. material_mismatch.jpg- ABV materially wrong -> Fail
  4. unreadable.png       - no legible text at all -> Needs Review

Committed to the repo (small images) since they are the bundled
demonstration data the deployed app ships with, not throwaway artifacts.
"""
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
W, H = 600, 900
MARGIN = 40


def _font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _wrap_to_width(d: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Word-wrap text to fit max_width pixels, measuring with the real font.

    A plain d.text() call never wraps — a long line just runs off the canvas
    edge and gets silently clipped, which is invisible until you OCR it back
    and find the tail missing.
    """
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if d.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _label(lines: list[tuple[str, int]], out_name: str, **save_kwargs):
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    y = MARGIN
    max_width = W - 2 * MARGIN
    for text, size in lines:
        font = _font(size)
        for wrapped_line in _wrap_to_width(d, text, font, max_width):
            d.text((MARGIN, y), wrapped_line, font=font, fill="black")
            y += size + 6
        y += 18  # gap between label fields
    img.save(OUT / out_name, **save_kwargs)


CANON = ("GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink "
         "alcoholic beverages during pregnancy because of the risk of birth defects. "
         "(2) Consumption of alcoholic beverages impairs your ability to drive a car or "
         "operate machinery, and may cause health problems.")


def make_compliant():
    _label([
        ("STONE'S THROW", 44),
        ("Kentucky Straight Bourbon Whiskey", 24),
        ("45% Alc./Vol. (90 Proof)", 28),
        ("750 mL", 28),
        ("Stone's Throw Distillery, Lawrenceburg, KY", 20),
        (CANON, 18),
    ], "compliant.png")


def make_brand_format():
    # Same as compliant but the printed brand differs only in case/apostrophe
    # style from the application's expected value ("STONE'S THROW").
    _label([
        ("Stone's Throw", 44),
        ("Kentucky Straight Bourbon Whiskey", 24),
        ("45% Alc./Vol. (90 Proof)", 28),
        ("750 mL", 28),
        ("Stone's Throw Distillery, Lawrenceburg, KY", 20),
        (CANON, 18),
    ], "brand_format.png")


def make_material_mismatch():
    # Printed ABV (40%) materially disagrees with the application's expected
    # value (45%) -> alcohol verifier MISMATCH -> overall Fail.
    _label([
        ("STONE'S THROW", 44),
        ("Kentucky Straight Bourbon Whiskey", 24),
        ("40% Alc./Vol. (80 Proof)", 28),
        ("750 mL", 28),
        ("Stone's Throw Distillery, Lawrenceburg, KY", 20),
        (CANON, 18),
    ], "material_mismatch.jpg", quality=85)


def make_unreadable():
    # A blank label with no text at all -> every field UNREADABLE -> Needs Review.
    img = Image.new("RGB", (W, H), (235, 235, 235))
    img.save(OUT / "unreadable.png")


if __name__ == "__main__":
    make_compliant()
    make_brand_format()
    make_material_mismatch()
    make_unreadable()
    print(f"wrote demo assets to {OUT}")
