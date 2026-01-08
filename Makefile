# AI-OPS-HUB Orchestrator
# Central Management for AI Lab & Automation Infrastructure

# --- Configuration ---
SHELL       := /bin/bash
.SHELLFLAGS := -ec
VENV        := .venv
CI          ?= false
PYTHON_BIN  := python3.13
ROOT        := $(shell pwd)

# New modular credential paths
CRED_ROOT       := infra/credentials
GDRIVE_CRED_DIR := $(CRED_ROOT)/gdrive
DATA_DIR        := data

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
TIMESTAMP := $(shell date '+%Y%m%d_%H%M%S')
LOG_NAME  := infra_health_check_$(TIMESTAMP).log
INFRA_LOG := $(DATA_DIR)/logs/$(LOG_NAME)
.PHONY: help setup quality security test-all clean lint-and-format verify-env update-deps health-check

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Main Pipelines ---

quality: clean ## Run full quality gate
	@echo ">>> [PIPELINE] Starting Full Quality Gate..."
	@$(MAKE) lint-and-format
	@echo ">>> [VALIDATION] Running Pre-commit Hooks..."
	$(PRE) run --all-files || (echo ">>> [RETRY] Pre-commit fixed issues. Re-running validation..." && $(PRE) run --all-files)
	@echo ">>> [SECURITY] Running Dependency Audit..."
	@$(MAKE) security
	@echo ">>> [TESTS] Executing Test Suite..."
	@$(MAKE) test-all
	@echo ">>> [AUDIT] Running Dependency Audit..."
	@$(PY) infra/scripts/integrity_check.py
	@echo ">>> [SYSTEM] Running Final Health Checks..."
	@$(MAKE) health-check
	@echo ">>> [SUCCESS] System is healthy and production-ready."

lint-and-format: ## Check and fix code style with Ruff
	@echo ">>> [RUFF] Running Unified Quality Engine..."
	$(RUFF) check . --fix
	$(RUFF) format .

health-audit: ## Execute the complete pipeline (Quality + Security + Audit)
	@mkdir -p $(DATA_DIR)/logs
	@echo "[$(shell date '+%Y-%m-%d %H:%M:%S')] INFO    : >>> [AUDIT] Starting Infrastructure Health Check..." | tee $(INFRA_LOG)
	@echo "---" | tee -a $(INFRA_LOG)
	@
	@echo "[STAGE 1/2] Global Quality & Security" | tee -a $(INFRA_LOG)
	@echo ">>> Lint & Static Analysis" | tee -a $(INFRA_LOG)
	@$(MAKE) lint-and-format 2>&1 | tee -a $(INFRA_LOG)
	@echo ">>> Security SAST" | tee -a $(INFRA_LOG)
	@$(MAKE) security 2>&1 | tee -a $(INFRA_LOG)
	@echo ">>> Infrastructure Integrity" | tee -a $(INFRA_LOG)
	@$(MAKE) verify-env 2>&1 | tee -a $(INFRA_LOG)
	@
	@echo "---" | tee -a $(INFRA_LOG)
	@echo "[STAGE 2/2] Full System Stability Audit" | tee -a $(INFRA_LOG)
	@echo ">>> Run Health Checks" | tee -a $(INFRA_LOG)
	@$(MAKE) health-check CI=$(CI) 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | tee -a $(INFRA_LOG)
	@echo ">>> Run Tests" | tee -a $(INFRA_LOG)
	@$(MAKE) test-all 2>&1 | tee -a $(INFRA_LOG)
	@
	@echo ">>> [AUDIT] Session saved to: $(INFRA_LOG)"
	@echo "[$(shell date '+%Y-%m-%d %H:%M:%S')] SUCCESS : >>> [AUDIT] Pipeline completed successfully." | tee -a $(INFRA_LOG)

# --- Infrastructure & Environment ---

setup: clean ## Initialize environment, venv and install dependencies
	@echo ">>> [STEP 1/5] Initializing Modular Infrastructure..."
	@mkdir -p $(GDRIVE_CRED_DIR)
	@mkdir -p $(DATA_DIR)/logs
	@echo ">>> [STEP 2/5] Initializing Venv (Python 3.13)..."
	@if [ ! -d "$(VENV)" ] && [ "$(CI)" = "false" ]; then $(PYTHON_BIN) -m venv $(VENV); fi
	@$(PIP) install --upgrade pip setuptools wheel
	@echo ">>> [STEP 3/5] Installing Requirements..."
	$(PIP) install -r requirements.txt
	@echo ">>> [STEP 4/5] Verifying Module Integrity..."
	@$(MAKE) verify-env
	@echo ">>> [STEP 5/5] Finalizing Git Hooks..."
	@if [ "$(CI)" = "false" ]; then $(PRE) install; fi

verify-env: ## Validate internal module mapping and integrity check
	@echo ">>> Running Dependency Audit..."
	@$(PY) infra/scripts/integrity_check.py

health-check: ## Run all dynamically discovered health checks (GDrive, Lab, etc.)
	@echo ">>> [SYSTEM] Starting Automated Health Suite..."
	@$(PY) -m infra.scripts.health_check

# --- Security & Testing ---

security: ## Run dependency audit for known vulnerabilities (CVEs)
	@echo ">>> [SECURITY] Updating audit tools..."
	$(PIP) install --upgrade pip pip-audit
	@echo ">>> [SECURITY] Running Dependency Audit on requirements.txt..."
	# Pointing directly to the file prevents scanning corrupted local metadata
	$(AUDIT) -r requirements.txt --ignore-vuln CVE-2025-53000

test-all: ## Run the complete pytest suite
	@echo ">>> Running Pytest suite..."
	$(PYTEST) infra/ --verbose

# --- Maintenance ---

clean: ## Remove temporary files and python caches
	@echo ">>> Cleaning Workspace Caches..."
	@echo ">>> Cleaning Caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	@echo ">>> Workspace clean."
