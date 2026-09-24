"""Core ambiguity-aware audit."""

from __future__ import annotations

from collections import Counter

from codonveil.genetic_code import (
    IUPAC,
    STANDARD_CODE,
    expand_codon,
    normalize_sequence,
    possible_amino_acids,
)
from codonveil.model import AuditConfig, AuditResult, CodonResult, SampleResult

UNCERTAIN_STATUSES = {
    "possible_substitution",
    "definite_ambiguous_substitution",
    "stop_risk",
    "possible_stop_loss",
    "gap",
    "partial_gap",
}
WARNING_STATUSES = UNCERTAIN_STATUSES | {
    "definite_substitution",
    "definite_stop",
    "definite_stop_loss",
}


def _classify(
    reference_codon: str, reference_amino_acid: str, sample_codon: str
) -> tuple[str, tuple[str, ...], int]:
    if sample_codon == "---":
        return "gap", (), 0
    if "-" in sample_codon:
        return "partial_gap", (), 0
    concrete = expand_codon(sample_codon)
    amino_acids = possible_amino_acids(sample_codon)
    ordered = tuple(sorted(amino_acids, key=lambda value: (value == "*", value)))

    if sample_codon == reference_codon:
        status = "match"
    elif reference_amino_acid == "*":
        if amino_acids == {"*"}:
            status = "synonymous_substitution" if len(concrete) == 1 else "synonymous_ambiguity"
        elif "*" in amino_acids:
            status = "possible_stop_loss"
        else:
            status = "definite_stop_loss"
    elif "*" in amino_acids:
        status = "definite_stop" if amino_acids == {"*"} else "stop_risk"
    elif amino_acids == {reference_amino_acid}:
        status = "synonymous_substitution" if len(concrete) == 1 else "synonymous_ambiguity"
    elif reference_amino_acid in amino_acids:
        status = "possible_substitution"
    elif len(amino_acids) == 1:
        status = "definite_substitution"
    else:
        status = "definite_ambiguous_substitution"
    return status, ordered, len(concrete)


def _validate(records: dict[str, str], reference_id: str) -> str:
    if reference_id not in records:
        raise ValueError(f"reference {reference_id!r} is not present in the FASTA input")
    reference = records[reference_id]
    if len(reference) % 3:
        raise ValueError("reference sequence length must be divisible by three")
    invalid_reference = sorted(set(reference) - set("ACGT"))
    if invalid_reference:
        raise ValueError("reference must contain only unambiguous A, C, G, and T")
    for sample_id, sequence in records.items():
        if len(sequence) != len(reference):
            raise ValueError(
                f"sequence {sample_id!r} has length {len(sequence)}; expected {len(reference)}"
            )
        invalid = sorted(set(sequence) - set(IUPAC) - {"-"})
        if invalid:
            raise ValueError(f"sequence {sample_id!r} has invalid symbols: {''.join(invalid)}")
    return reference


def audit_alignment(
    records: dict[str, str],
    reference_id: str,
    config: AuditConfig | None = None,
) -> AuditResult:
    """Audit aligned CDS records against an unambiguous reference."""
    effective_config = config or AuditConfig()
    normalized_records = {
        sample_id: normalize_sequence(sequence) for sample_id, sequence in records.items()
    }
    reference = _validate(normalized_records, reference_id)
    reference_codons = [reference[index : index + 3] for index in range(0, len(reference), 3)]
    reference_amino_acids = [STANDARD_CODE[codon] for codon in reference_codons]
    internal_stops = [index + 1 for index, aa in enumerate(reference_amino_acids[:-1]) if aa == "*"]
    if internal_stops:
        positions = ", ".join(str(position) for position in internal_stops)
        raise ValueError(
            f"reference contains internal stop codon(s) at codon position(s): {positions}"
        )

    samples: list[SampleResult] = []
    total_counts: Counter[str] = Counter()
    for sample_id in sorted(normalized_records):
        if sample_id == reference_id:
            continue
        sequence = normalized_records[sample_id]
        findings: list[CodonResult] = []
        sample_counts: Counter[str] = Counter()
        for index, (reference_codon, reference_aa) in enumerate(
            zip(reference_codons, reference_amino_acids, strict=True)
        ):
            sample_codon = sequence[index * 3 : index * 3 + 3]
            status, amino_acids, concrete_count = _classify(
                reference_codon, reference_aa, sample_codon
            )
            sample_counts[status] += 1
            total_counts[status] += 1
            if status != "match":
                findings.append(
                    CodonResult(
                        sample_id=sample_id,
                        codon_index=index + 1,
                        nucleotide_start=index * 3 + 1,
                        reference_codon=reference_codon,
                        sample_codon=sample_codon,
                        reference_amino_acid=reference_aa,
                        possible_amino_acids=amino_acids,
                        concrete_codon_count=concrete_count,
                        status=status,
                    )
                )
        uncertain = sum(sample_counts[status] for status in UNCERTAIN_STATUSES)
        samples.append(
            SampleResult(
                sample_id=sample_id,
                codons=len(reference_codons),
                matches=sample_counts["match"],
                synonymous_substitutions=sample_counts["synonymous_substitution"],
                synonymous_ambiguities=sample_counts["synonymous_ambiguity"],
                uncertain_codons=uncertain,
                stop_risks=sample_counts["stop_risk"] + sample_counts["possible_stop_loss"],
                partial_gaps=sample_counts["partial_gap"],
                findings=tuple(findings),
            )
        )

    if not samples:
        raise ValueError("FASTA input must contain at least one non-reference sample")

    uncertain_total = sum(total_counts[status] for status in UNCERTAIN_STATUSES)
    stop_risk_total = total_counts["stop_risk"] + total_counts["possible_stop_loss"]
    partial_gap_total = total_counts["partial_gap"]
    gate_failures: list[str] = []
    if (
        effective_config.max_stop_risk is not None
        and stop_risk_total > effective_config.max_stop_risk
    ):
        gate_failures.append(
            f"stop-risk codons {stop_risk_total} exceed maximum {effective_config.max_stop_risk}"
        )
    if (
        effective_config.max_partial_gap is not None
        and partial_gap_total > effective_config.max_partial_gap
    ):
        gate_failures.append(
            f"partial-gap codons {partial_gap_total} exceed maximum "
            f"{effective_config.max_partial_gap}"
        )
    if (
        effective_config.max_uncertain_codons is not None
        and uncertain_total > effective_config.max_uncertain_codons
    ):
        gate_failures.append(
            f"uncertain codons {uncertain_total} exceed maximum "
            f"{effective_config.max_uncertain_codons}"
        )

    has_warning = any(total_counts[status] for status in WARNING_STATUSES)
    status = "FAIL" if gate_failures else ("WARN" if has_warning else "PASS")
    counts = dict(total_counts)
    counts["uncertain_codon"] = uncertain_total
    counts["stop_risk_total"] = stop_risk_total
    return AuditResult(
        reference_id=reference_id,
        sequence_length=len(reference),
        codons=len(reference_codons),
        samples=tuple(samples),
        counts=counts,
        gate_failures=tuple(gate_failures),
        status=status,
    )
