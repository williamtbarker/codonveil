# CodonVeil

CodonVeil exposes protein consequences hidden by IUPAC ambiguity in aligned coding-sequence FASTA files. Instead of collapsing every ambiguous codon to `X`, it expands the exact set of concrete codons and distinguishes translation-stable ambiguity, possible substitutions, definite substitutions, stop risk, stop loss, and alignment gaps.

For example, `TTY` represents `TTC` or `TTT`; both encode phenylalanine. `TRG` represents `TAG` or `TGG`; one is a stop and the other encodes tryptophan. Treating both as an undifferentiated `X` discards materially different information.

## Why it is useful

Consensus and aligned coding sequences often contain IUPAC symbols. General-purpose translators correctly provide a single protein string, but downstream QC may need the full set-valued consequence at each codon. CodonVeil produces an auditable table and optional CI gates without inventing allele frequencies or biological interpretations.

## Installation

CodonVeil requires Python 3.10 or newer and has no runtime dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Quickstart

```bash
codonveil audit \
  --input examples/aligned_cds.fasta \
  --reference reference \
  --output-dir results
```

Expected headline:

```text
WARN: 5 samples; 3 uncertain codons; reports: results
```

The command writes:

- `report.md`: human-readable summary and finding table;
- `summary.json`: deterministic structured result;
- `samples.csv`: one row per sample;
- `codons.tsv`: one row per non-match codon.

The example deliberately contains a safe synonymous ambiguity, a possible amino-acid change, a stop-risk ambiguity, and a partial-gap codon.

## CI gates

Descriptive findings return exit code 0 by default. Add policy thresholds to turn selected conditions into failures:

```bash
codonveil audit \
  --input examples/aligned_cds.fasta \
  --reference reference \
  --output-dir gated-results \
  --max-stop-risk 0 \
  --max-partial-gap 0 \
  --max-uncertain-codons 0
```

The gated example writes its reports and exits with code 2. Invalid input or configuration exits with code 1.

## Python API

```python
from codonveil import AuditConfig, audit_alignment

result = audit_alignment(
    {"reference": "ATGTTT", "sample": "ATGTTY"},
    "reference",
    AuditConfig(max_stop_risk=0),
)
print(result.status)
print(result.samples[0].findings[0].status)
```

## Method

CodonVeil uses the standard genetic code (NCBI translation table 1) and the 15-symbol DNA IUPAC alphabet. Each ambiguous triplet is expanded as a Cartesian product of its represented bases. The amino-acid image of that concrete-codon set determines the classification relative to an unambiguous reference codon.

The implementation exhaustively validates all `15³ = 3,375` DNA-IUPAC codons against an independent direct expansion. Output ordering is deterministic by sample ID and codon position.

## Input contract

- Input is an aligned CDS FASTA, not arbitrary genomic sequence.
- All records must have the reference length, which must be divisible by three.
- The named reference must contain only `A`, `C`, `G`, and `T` and no internal stop.
- Samples may use DNA or RNA notation and the IUPAC alphabet plus alignment gaps.
- A sequence may not mix `T` and `U`.
- The standard genetic code is the only table supported in version 0.1.0.

## Assumptions and limitations

- IUPAC symbols specify possible bases, not probabilities. CodonVeil does not estimate allele frequencies.
- It assumes the alignment and reading frame are correct; it does not align sequences or annotate CDS boundaries.
- It does not use base qualities, read evidence, haplotypes, linkage across ambiguous positions, or phylogeny.
- It cannot determine whether an ambiguity reflects a real mixture, low coverage, sequencing error, contamination, or data processing.
- It reports translation possibilities, not protein expression, fitness, pathogenicity, or clinical significance.
- Alternative genetic codes, programmed frameshifts, RNA editing, selenocysteine, and context-dependent recoding are out of scope.

Do not use CodonVeil alone for diagnosis, treatment, outbreak attribution, or other clinical or public-health decisions.

## Relationship to existing software

[Biopython](https://biopython.org/docs/latest/api/Bio.Seq.html#Bio.Seq.translate) provides mature sequence translation and maps ambiguous codons such as `TAN` or `NNN` to `X`. [EMBOSS transeq](https://emboss.sourceforge.net/apps/release/6.6/emboss/apps/transeq.html) provides multi-frame translation across multiple genetic codes. [Nextclade](https://docs.nextstrain.org/projects/nextclade/en/stable/) performs pathogen-specific alignment, mutation calling, and QC.

CodonVeil does not replace those tools. Its narrower contribution is a dependency-free, reference-relative audit that preserves the exact amino-acid set behind every IUPAC codon and makes stop-risk and uncertainty policies available as deterministic tables and CI exits.

## Scientific references

- NCBI. [The Genetic Codes](https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi), including translation table 1.
- IUPAC-IUB Commission on Biochemical Nomenclature. “Abbreviations and Symbols for Nucleic Acids, Polynucleotides, and Their Constituents.” *European Journal of Biochemistry* 15 (1970): 203–208. [DOI: 10.1111/j.1432-1033.1970.tb00834.x](https://doi.org/10.1111/j.1432-1033.1970.tb00834.x).
- Cock PJA, et al. “Biopython: freely available Python tools for computational molecular biology and bioinformatics.” *Bioinformatics* 25(11), 2009. [DOI: 10.1093/bioinformatics/btp163](https://doi.org/10.1093/bioinformatics/btp163).

## Development

```bash
python -m pip install -e '.[dev]'
make verify
```

See `VALIDATION.md`, `VERIFICATION.md`, `DEVELOPMENT.md`, and `PROJECT_REPORT.md` for evidence, design provenance, and claims boundaries.

## License

MIT
