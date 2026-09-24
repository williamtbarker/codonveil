"""Deterministic report writers."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from codonveil.model import AuditResult


def render_markdown(result: AuditResult) -> str:
    stop_risks = result.counts.get("stop_risk_total", 0)
    uncertain = result.counts.get("uncertain_codon", 0)
    lines = [
        "# CodonVeil audit",
        "",
        f"**{result.status}: {len(result.samples)} samples; "
        f"{uncertain} uncertain codons; {stop_risks} stop-risk codons.**",
        "",
        f"Reference: `{result.reference_id}`  ",
        f"Aligned CDS length: {result.sequence_length} nt ({result.codons} codons)",
        "",
        "## Sample summary",
        "",
        "| Sample | Matches | Synonymous substitution | Synonymous ambiguity | "
        "Uncertain | Stop risk | Partial gap |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for sample in result.samples:
        lines.append(
            f"| `{sample.sample_id}` | {sample.matches} | {sample.synonymous_substitutions} | "
            f"{sample.synonymous_ambiguities} | {sample.uncertain_codons} | "
            f"{sample.stop_risks} | {sample.partial_gaps} |"
        )
    lines.extend(["", "## Findings", ""])
    findings = [finding for sample in result.samples for finding in sample.findings]
    if not findings:
        lines.append("No non-match codons were found.")
    else:
        lines.extend(
            [
                "| Sample | Codon | Ref | Observed | Ref AA | Possible AA | Status |",
                "|---|---:|---|---|---|---|---|",
            ]
        )
        for finding in findings:
            possible = "/".join(finding.possible_amino_acids) or "—"
            lines.append(
                f"| `{finding.sample_id}` | {finding.codon_index} | "
                f"`{finding.reference_codon}` | `{finding.sample_codon}` | "
                f"{finding.reference_amino_acid} | {possible} | "
                f"`{finding.status}` |"
            )
    if result.gate_failures:
        lines.extend(["", "## Failed gates", ""])
        lines.extend(f"- {failure}" for failure in result.gate_failures)
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "IUPAC symbols define sets of possible bases, not probabilities. This audit reports "
            "set-valued translation consequences under the standard genetic code. It does not "
            "infer within-sample frequencies, sequence quality, biological fitness, or clinical "
            "meaning.",
            "",
        ]
    )
    return "\n".join(lines)


def write_reports(result: AuditResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "report.md").write_text(render_markdown(result), encoding="utf-8", newline="\n")
    (output_dir / "summary.json").write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    with (output_dir / "samples.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "sample_id",
                "codons",
                "matches",
                "synonymous_substitutions",
                "synonymous_ambiguities",
                "uncertain_codons",
                "stop_risks",
                "partial_gaps",
            ]
        )
        for sample in result.samples:
            writer.writerow(
                [
                    sample.sample_id,
                    sample.codons,
                    sample.matches,
                    sample.synonymous_substitutions,
                    sample.synonymous_ambiguities,
                    sample.uncertain_codons,
                    sample.stop_risks,
                    sample.partial_gaps,
                ]
            )
    with (output_dir / "codons.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "sample_id",
                "codon_index",
                "nucleotide_start",
                "reference_codon",
                "sample_codon",
                "reference_amino_acid",
                "possible_amino_acids",
                "concrete_codon_count",
                "status",
            ]
        )
        for sample in result.samples:
            for finding in sample.findings:
                writer.writerow(
                    [
                        finding.sample_id,
                        finding.codon_index,
                        finding.nucleotide_start,
                        finding.reference_codon,
                        finding.sample_codon,
                        finding.reference_amino_acid,
                        ",".join(finding.possible_amino_acids),
                        finding.concrete_codon_count,
                        finding.status,
                    ]
                )
