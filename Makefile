.DEFAULT_GOAL := all

.PHONY: .uv
.uv: ## Check that uv is installed
	@uv --version || echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/'

.PHONY: .pre-commit
.pre-commit: ## Check that pre-commit is installed
	@pre-commit -V || echo 'Please install pre-commit: https://pre-commit.com/'

.PHONY: install
install: .uv .pre-commit ## Install the package, dependencies, and pre-commit for local development
	uv sync --frozen --all-extras --all-packages --group lint --group docs
	pre-commit install --install-hooks

.PHONY: sync
sync: .uv ## Update local packages and uv.lock
	uv sync --all-extras --all-packages --group lint --group docs

.PHONY: format
format: ## Format the code
	uv run ruff format
	uv run ruff check --fix --fix-only

.PHONY: lint
lint: ## Lint the code
	uv run ruff format --check
	uv run ruff check

.PHONY: typecheck-pyright
typecheck-pyright:
	@# PYRIGHT_PYTHON_IGNORE_WARNINGS avoids the overhead of making a request to github on every invocation
	PYRIGHT_PYTHON_IGNORE_WARNINGS=1 uv run pyright

.PHONY: typecheck-mypy
typecheck-mypy:
	uv run mypy

.PHONY: typecheck
typecheck: typecheck-pyright ## Run static type checking

.PHONY: typecheck-both  ## Run static type checking with both Pyright and Mypy
typecheck-both: typecheck-pyright typecheck-mypy

.PHONY: test
test: ## Run tests and collect coverage data
	uv run coverage run -m pytest
	@uv run coverage report

.PHONY: test-all-python
test-all-python: ## Run tests on Python 3.9 to 3.13
	UV_PROJECT_ENVIRONMENT=.venv39 uv run --python 3.9 --all-extras coverage run -p -m pytest
	UV_PROJECT_ENVIRONMENT=.venv310 uv run --python 3.10 --all-extras coverage run -p -m pytest
	UV_PROJECT_ENVIRONMENT=.venv311 uv run --python 3.11 --all-extras coverage run -p -m pytest
	UV_PROJECT_ENVIRONMENT=.venv312 uv run --python 3.12 --all-extras coverage run -p -m pytest
	UV_PROJECT_ENVIRONMENT=.venv313 uv run --python 3.13 --all-extras coverage run -p -m pytest

.PHONY: all
all: format lint typecheck ## Run code formatting, linting, static type checks, and tests with coverage report generation
