"""Independent exhaustive validation of CodonVeil's ambiguity expansion."""

from itertools import product

from codonveil.genetic_code import IUPAC, STANDARD_CODE, expand_codon, possible_amino_acids


def main() -> None:
    checked = 0
    for symbols in product(IUPAC, repeat=3):
        ambiguous = "".join(symbols)
        direct = {
            STANDARD_CODE["".join(concrete)]
            for concrete in product(*(IUPAC[symbol] for symbol in symbols))
        }
        observed = possible_amino_acids(ambiguous)
        assert observed == direct, (ambiguous, observed, direct)
        assert len(expand_codon(ambiguous)) == len(set(expand_codon(ambiguous)))
        checked += 1
    assert checked == 3375
    print("PASS: all 3,375 DNA-IUPAC codons match direct concrete expansion")


if __name__ == "__main__":
    main()
