"""Generate 5 representative label images for the tesseract spike.

Categories:
  1. clean        - high-contrast, perfect text
  2. glare        - bright wash over the warning region
  3. title_case   - warning prefix in title case
  4. proof_only   - alcohol stated as '90 Proof' only
  5. photographed - slight rotation + posterize + blur + JPEG compression
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

OUT = Path(__file__).parent / "labels"
OUT.mkdir(exist_ok=True)
W, H = 600, 900


def _font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _base_image(lines: list[tuple[str, int]], bg="white", fg="black") -> Image.Image:
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    y = 40
    for text, size in lines:
        d.text((40, y), text, font=_font(size), fill=fg)
        y += size + 24
    return img


CANON = ("GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink "
         "alcoholic beverages during pregnancy because of the risk of birth defects. "
         "(2) Consumption of alcoholic beverages impairs your ability to drive a car or "
         "operate machinery, and may cause health problems.")

_STANDARD_LINES = [
    ("OLD TOM DISTILLERY", 44),
    ("Kentucky Straight Bourbon Whiskey", 24),
    ("45% Alc./Vol. (90 Proof)", 28),
    ("750 mL", 28),
    ("Old Tom Distillery, Lawrenceburg, KY", 20),
]


def make_clean():
    img = _base_image(_STANDARD_LINES + [(CANON, 18)])
    img.save(OUT / "clean.png")


def make_glare():
    img = _base_image(_STANDARD_LINES + [(CANON, 18)])
    wash = Image.new("RGB", (W, H // 3), (255, 255, 255))
    mask = Image.new("L", (W, H // 3), 0)
    mask.paste(160, (0, 0, W, H // 3))
    img.paste(wash, (0, 2 * H // 3), mask)
    img.save(OUT / "glare.png")


def make_title_case():
    bad = CANON.replace("GOVERNMENT WARNING:", "Government Warning:")
    img = _base_image(_STANDARD_LINES + [(bad, 18)])
    img.save(OUT / "title_case.png")


def make_proof_only():
    lines = [
        ("OLD TOM DISTILLERY", 44),
        ("Kentucky Straight Bourbon Whiskey", 24),
        ("90 Proof", 28),
        ("750 mL", 28),
        ("Old Tom Distillery, Lawrenceburg, KY", 20),
        (CANON, 18),
    ]
    img = _base_image(lines)
    img.save(OUT / "proof_only.png")


def make_photographed():
    img = _base_image(_STANDARD_LINES + [(CANON, 18)])
    img = img.rotate(-3.0, expand=False, fillcolor=(240, 240, 240))
    img = ImageOps.posterize(img, 4)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    img.save(OUT / "photographed.jpg", quality=72)


if __name__ == "__main__":
    make_clean(); make_glare(); make_title_case(); make_proof_only(); make_photographed()
    print(f"wrote {len(list(OUT.glob('*')))} labels to {OUT}")
