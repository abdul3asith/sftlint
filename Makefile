.PHONY: help install sync lint fix format typecheck test test-cov check clean build publish-test publish

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies (including dev)
	uv sync

sync: install  ## Alias for install

lint:  ## Run ruff linter (check only)
	uv run ruff check .

fix:  ## Auto-fix lint issues where possible
	uv run ruff check --fix .

format:  ## Format all code with ruff
	uv run ruff format .

typecheck:  ## Run mypy static type checker
	uv run mypy

test:  ## Run all tests
	uv run pytest || [ $$? -eq 5 ]

test-cov:  ## Run tests with coverage report
	uv run pytest --cov=sftlint --cov-report=term-missing --cov-report=html || [ $$? -eq 5 ]

check: lint typecheck test  ## Run lint + typecheck + tests (full CI locally)

clean:  ## Remove build artifacts and caches
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +

build:  ## Build distributable wheel and sdist
	uv build

publish-test:  ## Upload to TestPyPI (sanity check before real release)
	uv publish --publish-url https://test.pypi.org/legacy/

publish:  ## Upload to PyPI (real release)
	uv publish