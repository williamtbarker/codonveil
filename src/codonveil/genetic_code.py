"""Standard-code translation over the complete DNA IUPAC alphabet."""

from __future__ import annotations

from itertools import product

IUPAC: dict[str, str] = {
    "A": "A",
    "C": "C",
    "G": "G",
    "T": "T",
    "R": "AG",
    "Y": "CT",
    "S": "CG",
    "W": "AT",
    "K": "GT",
    "M": "AC",
    "B": "CGT",
    "D": "AGT",
    "H": "ACT",
    "V": "ACG",
    "N": "ACGT",
}

_ROWS = {
    "TT": "FFLL",
    "TC": "SSSS",
    "TA": "YY**",
    "TG": "CC*W",
    "CT": "LLLL",
    "CC": "PPPP",
    "CA": "HHQQ",
    "CG": "RRRR",
    "AT": "IIIM",
    "AC": "TTTT",
    "AA": "NNKK",
    "AG": "SSRR",
    "GT": "VVVV",
    "GC": "AAAA",
    "GA": "DDEE",
    "GG": "GGGG",
}
_THIRD = "TCAG"
STANDARD_CODE: dict[str, str] = {
    first_two + third: amino_acids[index]
    for first_two, amino_acids in _ROWS.items()
    for index, third in enumerate(_THIRD)
}


def normalize_sequence(sequence: str) -> str:
    """Normalize case and RNA U while rejecting mixed DNA/RNA alphabets."""
    normalized = "".join(sequence.split()).upper()
    if "T" in normalized and "U" in normalized:
        raise ValueError("a sequence cannot mix T and U")
    return normalized.replace("U", "T")


def expand_codon(codon: str) -> tuple[str, ...]:
    """Return every concrete DNA codon represented by an IUPAC codon."""
    normalized = normalize_sequence(codon)
    if len(normalized) != 3:
        raise ValueError("a codon must contain exactly three nucleotides")
    if "-" in normalized:
        raise ValueError("gapped codons cannot be expanded")
    invalid = sorted(set(normalized) - set(IUPAC))
    if invalid:
        raise ValueError(f"invalid IUPAC nucleotide(s): {''.join(invalid)}")
    return tuple("".join(bases) for bases in product(*(IUPAC[base] for base in normalized)))


def possible_amino_acids(codon: str) -> frozenset[str]:
    """Return the set of standard-code translations represented by a codon."""
    return frozenset(STANDARD_CODE[concrete] for concrete in expand_codon(codon))
