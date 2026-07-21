"""Registry of bundled demonstration cases (governing prompt Phase 3).

Each case pairs a pre-generated label image (demo_assets/) with the
"application" data a filer would have submitted, so a reviewer can exercise
all four required scenarios with one click and no file of their own.
"""
from pathlib import Path

from label_verifier.warning_data import CANONICAL_WARNING

# Package-relative, so this resolves correctly under an editable install,
# a normal `pip install .`, and inside the Docker image alike — unlike a
# repo-root-relative path, which only works in the dev source tree.
DEMO_ASSETS_DIR = Path(__file__).resolve().parent / "demo_assets"

DEMO_CASES = {
    "compliant": {
        "label": "1. Compliant label (expect: Pass)",
        "description": "Every field on the label matches the application exactly.",
        "image": "compliant.png",
        "expected": {
            "brand": "STONE'S THROW",
            "class_type": "Kentucky Straight Bourbon Whiskey",
            "alcohol": "45% Alc./Vol. (90 Proof)",
            "net_contents": "750 mL",
            "bottler": "Stone's Throw Distillery, Lawrenceburg, KY",
            "country": None,
            "warning": CANONICAL_WARNING,
        },
        "is_import": False,
    },
    "brand_format": {
        "label": "2. Harmless brand formatting difference (expect: Pass)",
        "description": "Printed brand is 'Stone's Throw' vs application 'STONE'S THROW' — case/punctuation only.",
        "image": "brand_format.png",
        "expected": {
            "brand": "STONE'S THROW",
            "class_type": "Kentucky Straight Bourbon Whiskey",
            "alcohol": "45% Alc./Vol. (90 Proof)",
            "net_contents": "750 mL",
            "bottler": "Stone's Throw Distillery, Lawrenceburg, KY",
            "country": None,
            "warning": CANONICAL_WARNING,
        },
        "is_import": False,
    },
    "material_mismatch": {
        "label": "3. Material ABV mismatch (expect: Fail)",
        "description": "Application declares 45% ABV; the printed label reads 40% ABV.",
        "image": "material_mismatch.jpg",
        "expected": {
            "brand": "STONE'S THROW",
            "class_type": "Kentucky Straight Bourbon Whiskey",
            "alcohol": "45% Alc./Vol. (90 Proof)",
            "net_contents": "750 mL",
            "bottler": "Stone's Throw Distillery, Lawrenceburg, KY",
            "country": None,
            "warning": CANONICAL_WARNING,
        },
        "is_import": False,
    },
    "unreadable": {
        "label": "4. Unreadable image (expect: Needs Review)",
        "description": "Blank/illegible label image — extraction cannot read any field.",
        "image": "unreadable.png",
        "expected": {
            "brand": "STONE'S THROW",
            "class_type": "Kentucky Straight Bourbon Whiskey",
            "alcohol": "45% Alc./Vol. (90 Proof)",
            "net_contents": "750 mL",
            "bottler": "Stone's Throw Distillery, Lawrenceburg, KY",
            "country": None,
            "warning": CANONICAL_WARNING,
        },
        "is_import": False,
    },
}
