"""Ambiguity-aware coding-sequence auditing."""

from codonveil.audit import audit_alignment
from codonveil.genetic_code import expand_codon, possible_amino_acids
from codonveil.model import AuditConfig, AuditResult

__all__ = [
    "AuditConfig",
    "AuditResult",
    "audit_alignment",
    "expand_codon",
    "possible_amino_acids",
]
__version__ = "0.1.0"
