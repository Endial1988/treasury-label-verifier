"""Canonical U.S. Government Health Warning text for alcohol beverages.

Source: 27 CFR Sec.16.21 (Alcoholic Beverage Health Warning Statement).
Verbatim, including the all-caps prefix. Two subparagraphs.

Limitation: live TTB pages timed out during this session's verification pass
(see docs/ARCHITECTURE.md "Assumptions"); this text is taken from the
well-established statutory wording and should be re-confirmed against
https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning
when that site is reachable.
"""

CANONICAL_WARNING = (
    "GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink "
    "alcoholic beverages during pregnancy because of the risk of birth defects. "
    "(2) Consumption of alcoholic beverages impairs your ability to drive a car or operate "
    "machinery, and may cause health problems."
)
