# Validation record

## What was validated

The core scientific operation is finite: 15 DNA-IUPAC symbols in each of three codon positions produce 3,375 ambiguous codons. `scripts/validate_science.py` independently constructs each concrete Cartesian product and compares its amino-acid image with the package implementation.

The test suite also verifies:

- all 64 concrete codons are present and the three standard-code stops are correct;
- `TTY` resolves only to phenylalanine;
- `TRG` resolves to tryptophan or stop;
- `NNN` spans every standard-code output;
- RNA normalization and mixed DNA/RNA rejection;
- reference-relative substitution, stop-risk, stop-loss, gap, and gate behavior;
- deterministic byte-identical reports across repeated end-to-end runs; and
- strict rejection of malformed FASTA and invalid aligned-CDS contracts.

## Validation boundary

These checks establish that the implemented set expansion, classification rules, validation behavior, and reporting are internally consistent with NCBI translation table 1. They do not demonstrate:

- correctness of a user's alignment, CDS annotation, or reading frame;
- the biological source or frequency of an ambiguous base;
- expression or functional consequence of any possible translation;
- performance on a real cohort; or
- suitability for clinical or public-health decisions.

The bundled example is synthetic. No claim of biological validation is made.
