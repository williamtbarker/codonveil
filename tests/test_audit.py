import pytest

from codonveil import AuditConfig, audit_alignment

REFERENCE = "ATGTTTGAATGGGCTTAA"


def test_classifies_set_valued_translation_consequences() -> None:
    result = audit_alignment(
        {
            "reference": REFERENCE,
            "exact": REFERENCE,
            "silent": "ATGTTYGAATGGGCNTAA",
            "possible": "ATGTWYGAATGGGCTTAA",
            "stop-risk": "ATGTTTGAATRGGCTTAA",
            "partial-gap": "ATGTTTGAATGGG-TTAA",
        },
        "reference",
    )
    assert result.status == "WARN"
    by_sample = {sample.sample_id: sample for sample in result.samples}
    assert by_sample["exact"].matches == 6
    assert by_sample["silent"].synonymous_ambiguities == 2
    assert by_sample["silent"].uncertain_codons == 0
    assert by_sample["possible"].findings[0].status == "possible_substitution"
    assert by_sample["possible"].findings[0].possible_amino_acids == ("F", "Y")
    assert by_sample["stop-risk"].findings[0].status == "stop_risk"
    assert by_sample["stop-risk"].findings[0].possible_amino_acids == ("W", "*")
    assert by_sample["partial-gap"].findings[0].status == "partial_gap"


def test_distinguishes_definite_change_and_stop_loss() -> None:
    result = audit_alignment(
        {
            "ref": "AAATAA",
            "substitution": "AARTAA",
            "stop-loss": "AAACAA",
            "possible-stop-loss": "AAATAN",
        },
        "ref",
    )
    statuses = {
        sample.sample_id: sample.findings[0].status for sample in result.samples if sample.findings
    }
    assert statuses == {
        "possible-stop-loss": "possible_stop_loss",
        "stop-loss": "definite_stop_loss",
        "substitution": "synonymous_ambiguity",
    }


def test_distinguishes_unambiguous_synonymous_substitution_from_exact_match() -> None:
    result = audit_alignment({"ref": "TTT", "sample": "TTC"}, "ref")
    sample = result.samples[0]
    assert sample.matches == 0
    assert sample.synonymous_substitutions == 1
    assert sample.findings[0].status == "synonymous_substitution"


def test_public_api_normalizes_lowercase_rna() -> None:
    result = audit_alignment({"ref": "aug", "sample": "AUG"}, "ref")
    assert result.status == "PASS"


def test_gates_fail_with_explanations() -> None:
    result = audit_alignment(
        {"ref": REFERENCE, "risk": "ATGTTTGAATRGG-TTAA"},
        "ref",
        AuditConfig(max_stop_risk=0, max_partial_gap=0, max_uncertain_codons=1),
    )
    assert result.status == "FAIL"
    assert len(result.gate_failures) == 3


@pytest.mark.parametrize(
    ("records", "reference", "message"),
    [
        ({"ref": "ATGA", "x": "ATGA"}, "ref", "divisible"),
        ({"ref": "ATGNNN", "x": "ATGAAA"}, "ref", "unambiguous"),
        ({"ref": "ATGTAA", "x": "ATG"}, "ref", "length"),
        ({"ref": "ATGTAGAAA", "x": "ATGTAGAAA"}, "ref", "internal stop"),
        ({"ref": "ATG"}, "ref", "non-reference"),
        ({"ref": "ATG", "x": "ATG"}, "missing", "not present"),
    ],
)
def test_invalid_alignments_are_rejected(
    records: dict[str, str], reference: str, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        audit_alignment(records, reference)


def test_negative_gate_is_rejected() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        AuditConfig(max_stop_risk=-1)
