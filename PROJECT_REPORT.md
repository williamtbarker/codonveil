# Project selection report

## Decision

CodonVeil was selected as the strongest one-run project: an ambiguity-aware, reference-relative codon audit for aligned coding sequences.

This project addresses a clearly evidenced technical need rather than claiming to reproduce a new biological method. Biopython documents that ambiguous codons such as `TAN` and `NNN` translate to `X`; that is appropriate for a single protein string but loses the distinction between translation-stable ambiguity and ambiguity that includes substitutions or termination. NCBI's genetic-code tables and the IUPAC nucleotide alphabet make this distinction exactly enumerable and independently testable.

## Candidate comparison

Each category is scored from 1–5. Total possible score: 30.

| Candidate | Useful | Distinct | Defensible | Feasible | Validatable | Portfolio | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| IUPAC codon-consequence auditor | 5 | 4 | 5 | 5 | 5 | 5 | **29** |
| Scientific-table contract inference/diff | 5 | 2 | 4 | 5 | 5 | 4 | 25 |
| Compression/order-independent paired FASTQ manifest | 4 | 3 | 4 | 4 | 5 | 4 | 24 |

The table-contract candidate faced mature prior art including Frictionless, Pandera, Great Expectations, and data-profiling systems. The FASTQ-manifest candidate overlapped substantially with `seqkit sum`, established checksums, and existing pipeline provenance tooling. CodonVeil has a smaller scope but a sharper informational contribution and a complete finite validation space.

## Prior art and added value

- **Biopython** is the obvious mature Python foundation for parsing and translation. Its public API documents translation of ambiguous codons to `X` when they might encode an amino acid or stop.
- **EMBOSS transeq** provides robust multi-frame translation and many genetic-code choices.
- **Nextclade** provides pathogen-specific alignment, mutation calling, and QC.
- General variant-annotation and codon-model tools solve broader problems but commonly require coordinates, variant formats, reference annotations, or phylogenetic models.

CodonVeil's added value is not a new genetic code or translator. It is the operational combination of:

1. exact set-valued expansion of every DNA-IUPAC triplet;
2. reference-relative labels separating synonymous ambiguity, possible and definite substitutions, stop risk, stop loss, and gaps;
3. strict aligned-CDS input validation;
4. deterministic Markdown, JSON, CSV, and TSV evidence;
5. optional policy gates with stable exit codes; and
6. no runtime dependencies.

Searches of GitHub/PyPI-style results and the major general-purpose tools did not reveal an exact packaged CLI with this same narrow contract. That is evidence of differentiation, not proof of novelty.

## Source and license review

The implementation uses the published IUPAC ambiguity definitions and NCBI standard genetic code as scientific facts. No external source code or datasets were copied. The bundled FASTA is synthetic and dedicated as part of this MIT-licensed repository. Biopython and EMBOSS are cited as prior art but are not dependencies.

## Language choice

Python fits the small combinatorial method, scientific scripting audience, and table/report interfaces. Runtime performance is not limiting: the largest codon expansion contains only 64 concrete codons. A Rust implementation would add packaging complexity without a scientifically meaningful advantage.

## Claim

CodonVeil is an original operational utility built from established notation and the standard genetic code. It is not a replication of a paper, a biological classifier, or a clinical validator.
