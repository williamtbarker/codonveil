# Development notes

## Design choices

- The standard code is embedded explicitly so the runtime package remains dependency-free and auditable.
- IUPAC codons are treated as sets, never as probability distributions.
- The reference is required to be unambiguous; otherwise reference-relative labels would themselves be set-valued and substantially harder to interpret.
- Partial codon gaps are kept distinct from full codon gaps because the former often indicate a frame/alignment problem.
- Reports are written before returning exit code 2 so CI systems can retain diagnostic artifacts.
- Version 0.1.0 deliberately supports only full-length aligned CDS records and translation table 1.

## Future work that should require evidence

- Additional NCBI translation tables should be generated from an authoritative machine-readable source and cross-validated, not manually transcribed ad hoc.
- Variant-frequency inputs would require an explicit probabilistic model and must not assign equal probabilities to IUPAC alternatives by default.
- GenBank/GFF annotation support should preserve strand, phase, compound locations, and translational exceptions.
