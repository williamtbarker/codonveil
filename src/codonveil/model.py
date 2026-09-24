"""Typed public result model."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class AuditConfig:
    max_stop_risk: int | None = None
    max_partial_gap: int | None = None
    max_uncertain_codons: int | None = None

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if value is not None and value < 0:
                raise ValueError(f"{name} must be non-negative")


@dataclass(frozen=True)
class CodonResult:
    sample_id: str
    codon_index: int
    nucleotide_start: int
    reference_codon: str
    sample_codon: str
    reference_amino_acid: str
    possible_amino_acids: tuple[str, ...]
    concrete_codon_count: int
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SampleResult:
    sample_id: str
    codons: int
    matches: int
    synonymous_substitutions: int
    synonymous_ambiguities: int
    uncertain_codons: int
    stop_risks: int
    partial_gaps: int
    findings: tuple[CodonResult, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["findings"] = [finding.to_dict() for finding in self.findings]
        return data


@dataclass(frozen=True)
class AuditResult:
    reference_id: str
    sequence_length: int
    codons: int
    samples: tuple[SampleResult, ...]
    counts: dict[str, int]
    gate_failures: tuple[str, ...]
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "reference_id": self.reference_id,
            "sequence_length": self.sequence_length,
            "codons": self.codons,
            "sample_count": len(self.samples),
            "status": self.status,
            "counts": dict(sorted(self.counts.items())),
            "gate_failures": list(self.gate_failures),
            "samples": [sample.to_dict() for sample in self.samples],
        }
