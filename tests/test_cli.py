from pathlib import Path

from codonveil.cli import main

FIXTURE = Path(__file__).parents[1] / "examples" / "aligned_cds.fasta"


def test_cli_writes_deterministic_end_to_end_reports(tmp_path: Path, capsys: object) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    base = ["audit", "--input", str(FIXTURE), "--reference", "reference", "--output-dir"]
    assert main([*base, str(first)]) == 0
    assert main([*base, str(second)]) == 0
    assert (first / "report.md").read_bytes() == (second / "report.md").read_bytes()
    assert (first / "summary.json").read_bytes() == (second / "summary.json").read_bytes()
    assert (first / "samples.csv").read_bytes() == (second / "samples.csv").read_bytes()
    assert (first / "codons.tsv").read_bytes() == (second / "codons.tsv").read_bytes()


def test_cli_gate_returns_two_but_still_writes_report(tmp_path: Path) -> None:
    output = tmp_path / "gated"
    code = main(
        [
            "audit",
            "--input",
            str(FIXTURE),
            "--reference",
            "reference",
            "--output-dir",
            str(output),
            "--max-stop-risk",
            "0",
        ]
    )
    assert code == 2
    assert "**FAIL:" in (output / "report.md").read_text(encoding="utf-8")


def test_cli_invalid_input_returns_one(tmp_path: Path, capsys: object) -> None:
    code = main(
        [
            "audit",
            "--input",
            str(tmp_path / "missing.fasta"),
            "--reference",
            "ref",
            "--output-dir",
            str(tmp_path / "out"),
        ]
    )
    assert code == 1
