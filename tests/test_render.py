import json
from pathlib import Path

from codonveil import audit_alignment
from codonveil.render import render_markdown, write_reports


def test_clean_alignment_renders_pass(tmp_path: Path) -> None:
    result = audit_alignment({"ref": "ATGAAA", "sample": "ATGAAA"}, "ref")
    assert result.status == "PASS"
    assert "No non-match codons" in render_markdown(result)
    write_reports(result, tmp_path)
    payload = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["status"] == "PASS"
