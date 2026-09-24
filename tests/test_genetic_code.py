from itertools import product

import pytest

from codonveil.genetic_code import IUPAC, STANDARD_CODE, expand_codon, possible_amino_acids


def test_standard_code_has_all_64_codons() -> None:
    assert len(STANDARD_CODE) == 64
    assert STANDARD_CODE["ATG"] == "M"
    assert {codon for codon, amino_acid in STANDARD_CODE.items() if amino_acid == "*"} == {
        "TAA",
        "TAG",
        "TGA",
    }


def test_known_degenerate_codons_preserve_information() -> None:
    assert expand_codon("TTY") == ("TTC", "TTT")
    assert possible_amino_acids("TTY") == {"F"}
    assert possible_amino_acids("TRG") == {"*", "W"}
    assert possible_amino_acids("NNN") == set(STANDARD_CODE.values())


def test_rna_is_normalized_but_mixed_alphabet_is_rejected() -> None:
    assert possible_amino_acids("AUG") == {"M"}
    with pytest.raises(ValueError, match="mix T and U"):
        possible_amino_acids("ATU")


def test_all_3375_iupac_codons_match_direct_concrete_expansion() -> None:
    symbols = tuple(IUPAC)
    checked = 0
    for ambiguous in map("".join, product(symbols, repeat=3)):
        concrete = expand_codon(ambiguous)
        expected = {
            STANDARD_CODE["".join(bases)]
            for bases in product(*(IUPAC[symbol] for symbol in ambiguous))
        }
        assert possible_amino_acids(ambiguous) == expected
        assert len(concrete) == len(set(concrete))
        checked += 1
    assert checked == 3375


@pytest.mark.parametrize("codon", ["AA", "AAAA", "AZG", "A-G"])
def test_invalid_codons_are_rejected(codon: str) -> None:
    with pytest.raises(ValueError):
        expand_codon(codon)
