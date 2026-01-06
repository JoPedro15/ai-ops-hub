# AI-OPS-HUB Orchestrator
# Central Management for AI Lab & Automation Infrastructure

# --- Configuration ---
SHELL       := /bin/bash
.SHELLFLAGS := -ec

VENV        := .venv
CI          ?= false
PYTHON_BIN  := python3.13
ROOT        := $(shell pwd)

.DELETE_ON_ERROR:

# Binary detection strategy
ifeq ($(CI), true)
    PY  := python
    PIP := pip
else
    PY  := $(ROOT)/$(VENV)/bin/python
    PIP := $(ROOT)/$(VENV)/bin/pip
endif

# Tooling paths (Local vs CI)
ifeq ($(CI), true)
    RUFF    := ruff
    PRE     := pre-commit
    PYTEST  := pytest
    AUDIT   := pip-audit
else
    BIN     := $(ROOT)/$(VENV)/bin/
    RUFF    := $(BIN)ruff
    PRE     := $(BIN)pre-commit
    PYTEST  := $(BIN)pytest
    AUDIT   := $(BIN)pip-audit
endif

export PYTHONPATH := $(ROOT)

.PHONY: help setup quality security test-all clean lint-and-format verify-env update-deps health-check

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Main Pipelines ---

quality: clean
	@echo ">>> [PIPELINE] Starting Full Quality Gate..."
	@$(MAKE) lint-and-format
	@echo ">>> [VALIDATION] Running Pre-commit Hooks..."
	$(PRE) run --all-files
	@echo ">>> [SECURITY] Running Dependency Audit..."
	@$(MAKE) security
	@echo ">>> [TESTS] Executing Test Suite..."
	@$(MAKE) test-all
	@echo ">>> [SUCCESS] System is healthy and production-ready."

lint-and-format:
	@echo ">>> [RUFF] Running Unified Quality Engine..."
	$(RUFF) check . --fix
	$(RUFF) format .

# --- Infrastructure & Environment ---

setup: clean
	@echo ">>> [STEP 1/4] Initializing Venv (Python 3.13)..."
	@if [ ! -d "$(VENV)" ] && [ "$(CI)" = "false" ]; then $(PYTHON_BIN) -m venv $(VENV); fi
	@$(PIP) install --upgrade pip setuptools wheel
	@echo ">>> [STEP 2/4] Installing Requirements..."
	$(PIP) install -r requirements.txt
	@echo ">>> [STEP 3/4] Verifying Module Integrity..."
	@$(MAKE) verify-env
	@echo ">>> [STEP 4/4] Finalizing Git Hooks..."
	@if [ "$(CI)" = "false" ]; then $(PRE) install; fi

verify-env:
	@echo ">>> Running Dependency Audit..."
	@$(PY) infra/scripts/integrity_check.py

health-check:
	@echo ">>> [SYSTEM] Starting Infrastructure Health Check..."
	$(PY) -m infra.gdrive.service

# --- Security & Testing ---

security:
	@echo ">>> [SECURITY] Updating audit tools..."
	$(PIP) install --upgrade pip pip-audit
	@echo ">>> [SECURITY] Running Dependency Audit on requirements.txt..."
	# Pointing directly to the file prevents scanning corrupted local metadata
	$(AUDIT) -r requirements.txt --ignore-vuln CVE-2025-53000

test-all:
	@echo ">>> Running Pytest suite..."
	$(PYTEST) --verbose

# --- Maintenance ---

clean:
	@echo ">>> Cleaning Workspace Caches..."
	@echo ">>> Cleaning Caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	@echo ">>> Workspace clean."
