.PHONY: format lint typecheck test science package smoke verify clean

format:
	python -m ruff format --check .

lint:
	python -m ruff check .

typecheck:
	python -m mypy

test:
	python -m pytest

science:
	python scripts/validate_science.py

package:
	python -m build
	python -m twine check dist/*

smoke:
	python -m codonveil audit --input examples/aligned_cds.fasta --reference reference --output-dir build/smoke

verify: format lint typecheck test science package smoke

clean:
	python -c "import shutil; [shutil.rmtree(path, ignore_errors=True) for path in ('build', 'dist', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'htmlcov')]; shutil.rmtree('src/codonveil.egg-info', ignore_errors=True)"
