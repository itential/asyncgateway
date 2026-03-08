# !make

# Copyright 2025 Itential Inc. All Rights Reserved
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# ==============================================================================
# asyncgateway — async Python client for Itential Automation Gateway
# ==============================================================================
# Usage:
#   make              Show available targets
#   make test         Run unit tests
#   make ci           Run all checks (use before committing)
#
# Dependencies: uv (https://github.com/astral-sh/uv)
# ==============================================================================

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

UV    ?= uv
SRC   := src/asyncgateway
TESTS := tests

# ------------------------------------------------------------------------------
# Core
# ------------------------------------------------------------------------------

.PHONY: test coverage build

test: ## Run unit tests
	$(UV) run pytest $(TESTS)

coverage: ## Run tests with coverage report
	$(UV) run pytest \
		--cov=$(SRC) \
		--cov-report=term \
		--cov-report=html \
		$(TESTS)/

build: ## Build distribution packages (wheel + sdist)
	$(UV) build

# ------------------------------------------------------------------------------
# Quality checks
# ------------------------------------------------------------------------------

.PHONY: lint format format-check security

lint: ## Lint with ruff
	$(UV) run ruff check $(SRC) $(TESTS)

format: ## Format source files with ruff
	$(UV) run ruff format $(SRC) $(TESTS)

format-check: ## Check formatting without modifying files
	$(UV) run ruff format --check $(SRC) $(TESTS)

security: ## Run bandit security analysis
	$(UV) run bandit -r $(SRC) --configfile pyproject.toml

# ------------------------------------------------------------------------------
# CI
# ------------------------------------------------------------------------------

.PHONY: ci premerge

ci: clean lint security test ## Run all checks (required before committing)

premerge: ci ## Alias for ci (backwards compat)

# ------------------------------------------------------------------------------
# Tox (multi-version)
# ------------------------------------------------------------------------------

.PHONY: tox tox-py310 tox-py311 tox-py312 tox-py313
.PHONY: tox-coverage tox-lint tox-security tox-list

tox: ## Run tests across all Python versions (3.10-3.13)
	$(UV) run tox

tox-py310: ## Run tests with Python 3.10
	$(UV) run tox -e py310

tox-py311: ## Run tests with Python 3.11
	$(UV) run tox -e py311

tox-py312: ## Run tests with Python 3.12
	$(UV) run tox -e py312

tox-py313: ## Run tests with Python 3.13
	$(UV) run tox -e py313

tox-coverage: ## Run coverage report via tox
	$(UV) run tox -e coverage

tox-lint: ## Run lint via tox
	$(UV) run tox -e lint

tox-security: ## Run security scan via tox
	$(UV) run tox -e security

tox-list: ## List all available tox environments
	$(UV) run tox list

# ------------------------------------------------------------------------------
# Development
# ------------------------------------------------------------------------------

.PHONY: setup

setup: ## Set up development environment with pre-commit hooks
	@./scripts/setup-pre-commit.sh

# ------------------------------------------------------------------------------
# Housekeeping
# ------------------------------------------------------------------------------

.PHONY: clean

clean: ## Remove build artifacts and caches
	@rm -rf .pytest_cache .ruff_cache .tox coverage.* htmlcov dist build *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------

.PHONY: help

help: ## Show available targets
	@echo "Usage: make <target>"
	@echo ""
	@grep -E '^[a-zA-Z_/-]+:.*##' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' \
		| sort
	@echo ""
