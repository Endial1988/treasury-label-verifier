from label_verifier.models import Verdict, FieldVerdict, VerifyResult


def test_verdict_has_six_members():
    names = {v.name for v in Verdict}
    assert names == {"MATCH", "MISMATCH", "UNREADABLE",
                     "LOW_CONFIDENCE", "MISSING", "NOT_REQUIRED"}


def test_verdict_values_are_lowercase_names():
    assert Verdict.MATCH.value == "match"
    assert Verdict.NOT_REQUIRED.value == "not_required"


def test_field_verdict_constructs_with_minimal_fields():
    v = FieldVerdict(field="brand", expected="X", found="X", verdict=Verdict.MATCH)
    assert v.field == "brand"
    assert v.confidence is None
    assert v.note is None


def test_verify_result_summary_counts_verdicts():
    fv = [FieldVerdict(field="brand", expected="X", found="X", verdict=Verdict.MATCH),
          FieldVerdict(field="warning", expected="Y", found="Z", verdict=Verdict.MISMATCH)]
    r = VerifyResult(label_verdicts=fv, overall=Verdict.MISMATCH,
                     summary={"match": 1, "mismatch": 1})
    assert r.summary["match"] == 1
