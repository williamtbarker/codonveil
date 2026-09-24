"""Strict, dependency-free FASTA parsing."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from codonveil.genetic_code import IUPAC, normalize_sequence


def parse_fasta(handle: TextIO) -> dict[str, str]:
    records: dict[str, str] = {}
    identifier: str | None = None
    chunks: list[str] = []

    def store() -> None:
        nonlocal identifier, chunks
        if identifier is None:
            return
        sequence = normalize_sequence("".join(chunks))
        if not sequence:
            raise ValueError(f"FASTA record {identifier!r} has no sequence")
        invalid = sorted(set(sequence) - set(IUPAC) - {"-"})
        if invalid:
            raise ValueError(
                f"FASTA record {identifier!r} contains invalid symbol(s): {''.join(invalid)}"
            )
        records[identifier] = sequence

    for line_number, raw_line in enumerate(handle, start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            store()
            identifier = line[1:].split(maxsplit=1)[0]
            if not identifier:
                raise ValueError(f"empty FASTA identifier on line {line_number}")
            if identifier in records:
                raise ValueError(f"duplicate FASTA identifier {identifier!r}")
            chunks = []
        elif identifier is None:
            raise ValueError(f"sequence data before first FASTA header on line {line_number}")
        else:
            chunks.append(line)
    store()
    if not records:
        raise ValueError("FASTA input contains no records")
    return records


def read_fasta(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8", newline=None) as handle:
        return parse_fasta(handle)
