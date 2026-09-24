# Verification record

This file records release-candidate verification for v0.1.0 on Linux with CPython 3.12.14.

## Commands

```bash
python -m ruff format --check .
python -m ruff check .
python -m mypy
python -m pytest
python scripts/validate_science.py
python -m build
python -m twine check dist/*
python -m codonveil audit \
  --input examples/aligned_cds.fasta \
  --reference reference \
  --output-dir build/smoke
```

## Results

- Ruff formatting: 22 files formatted; passed.
- Ruff linting: passed with no findings.
- Strict mypy: 9 source files passed.
- Pytest: 30 passed.
- Branch-aware coverage: 94.75%.
- Exhaustive scientific oracle: all 3,375 DNA-IUPAC codons passed.
- Wheel and source distribution: built successfully.
- Twine metadata checks: both distributions passed.
- Clean wheel installation: passed in a fresh virtual environment.
- Installed CLI quickstart: passed.
- Repeated Markdown, JSON, CSV, and TSV reports: byte-identical.
- Runtime dependency check: no broken requirements; the package has no runtime dependencies.
- `CITATION.cff`: valid against CFF schema 1.2.0.
- Strict stop-risk gate: wrote reports and returned documented exit code 2.

Only CPython 3.12 was available in the release environment. The GitHub Actions matrix is configured for CPython 3.10 and 3.12 on Linux and macOS; those jobs cannot run until the repository is published.
