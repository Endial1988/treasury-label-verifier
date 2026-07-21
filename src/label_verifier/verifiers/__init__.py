"""Verifier registry: canonical field name -> verifier callable.

Each verifier has signature (expected, found, **opts) -> FieldVerdict.
'country' additionally accepts is_import; the orchestrator passes it via opts.
"""
from label_verifier.verifiers.brand import verify_brand
from label_verifier.verifiers.class_type import verify_class_type
from label_verifier.verifiers.alcohol import verify_alcohol
from label_verifier.verifiers.net_contents import verify_net_contents
from label_verifier.verifiers.bottler import verify_bottler
from label_verifier.verifiers.country import verify_country
from label_verifier.verifiers.warning import verify_warning

FIELD_VERIFIERS = {
    "brand": verify_brand,
    "class_type": verify_class_type,
    "alcohol": verify_alcohol,
    "net_contents": verify_net_contents,
    "bottler": verify_bottler,
    "country": verify_country,
    "warning": verify_warning,
}

__all__ = ["FIELD_VERIFIERS"]
