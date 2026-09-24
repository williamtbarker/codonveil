from io import StringIO

import pytest

from codonveil.fasta import parse_fasta


def test_parse_multiline_fasta_and_normalize_rna() -> None:
    records = parse_fasta(StringIO(">ref description\nAUG\nUUY\n>sample\nATGTTT\n"))
    assert records == {"ref": "ATGTTY", "sample": "ATGTTT"}


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("ACGT\n", "before first FASTA"),
        (">x\n>x\nAAA\n", "has no sequence"),
        (">x\nAAA\n>x\nAAA\n", "duplicate"),
        (">x\n", "has no sequence"),
        (">x\nAZA\n", "invalid symbol"),
    ],
)
def test_invalid_fasta_is_rejected(text: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        parse_fasta(StringIO(text))
