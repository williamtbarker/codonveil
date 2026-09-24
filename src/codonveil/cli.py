"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from codonveil.audit import audit_alignment
from codonveil.fasta import read_fasta
from codonveil.model import AuditConfig
from codonveil.render import write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codonveil",
        description=(
            "Audit the protein consequences hidden by IUPAC ambiguity in aligned CDS FASTA."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit = subparsers.add_parser("audit", help="audit an aligned coding-sequence FASTA")
    audit.add_argument("--input", required=True, type=Path, help="aligned CDS FASTA")
    audit.add_argument("--reference", required=True, help="unambiguous reference record ID")
    audit.add_argument(
        "--output-dir", required=True, type=Path, help="new or existing report directory"
    )
    audit.add_argument("--max-stop-risk", type=int, default=None)
    audit.add_argument("--max-partial-gap", type=int, default=None)
    audit.add_argument("--max-uncertain-codons", type=int, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = AuditConfig(
            max_stop_risk=args.max_stop_risk,
            max_partial_gap=args.max_partial_gap,
            max_uncertain_codons=args.max_uncertain_codons,
        )
        records = read_fasta(args.input)
        result = audit_alignment(records, args.reference, config)
        write_reports(result, args.output_dir)
        print(
            f"{result.status}: {len(result.samples)} samples; "
            f"{result.counts.get('uncertain_codon', 0)} uncertain codons; "
            f"reports: {args.output_dir}"
        )
        return 2 if result.gate_failures else 0
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
