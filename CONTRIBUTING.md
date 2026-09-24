# Contributing

Thank you for considering a contribution.

1. Open an issue describing the scientific or engineering problem.
2. Create a focused branch and include deterministic tests.
3. Install development tools with `python -m pip install -e '.[dev]'`.
4. Run `make verify` before submitting a pull request.

Changes to IUPAC definitions, genetic codes, or classification semantics must cite an authoritative source and include exhaustive or fixture-based validation. Do not add real human or confidential sequence data to tests. Synthetic fixtures are preferred.
