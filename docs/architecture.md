# 🏗️ AI-Ops Hub: Modular Monorepo Architecture

This project follows a **Centralized Modular Architecture** designed to balance foundational infrastructure with agile AI experimentation. By using a single orchestration layer (Root), we ensure maximum consistency and zero redundant configuration.

## 🏗️ Architecture Overview

The system is organized into three strategic layers:

### 1. Infrastructure Layer (`/infra`)

**The Foundational Layer.** Contains high-reliability, reusable services and utilities.

- **`infra/common`**: SSoT for cross-domain utilities like the unified Logger.
- **`infra/gdrive`**: Encapsulated Google Drive API service.
- **`infra/ai_utils`**: Specialized ingestors and processors for data pipelines.
- **Rules**: Modules here must be stateless where possible and strictly type-annotated. They should avoid circular dependencies by importing from direct paths.

### 2. Lab Layer (`/lab`)

**The Research & Orchestration Layer.** (Formerly Projects)

- **Goal**: Where AI experiments, notebooks, and automation scripts reside.
- **Rules**: Consumes `infra` modules via the **Facade Pattern** (e.g., `from infra import logger`). Business logic and model training happen here.

### 3. Governance Layer (Root `/`)

**The Centralized Control Plane.**

- **Goal**: Unified management of the entire ecosystem.
- **Components**:
  - `pyproject.toml`: Single Source of Truth for dependencies and tool configs (Ruff, Pytest).
  - `Makefile`: Centralized orchestration of quality gates and environment setup.
  - `.pre-commit-config.yaml`: Global security and style enforcement.

______________________________________________________________________

## 🛠️ Engineering Standards

To maintain **High Rigor**, every contribution must follow these protocols:

### ⚡ The Facade Pattern

External consumers (in `/lab`) should interface with infrastructure through the package roots to keep imports clean:
`from infra.ai_utils import DataIngestor` ✅

### 🛡️ Quality Gate (The Promotion Rule)

A component or experiment is only considered "Production-Ready" if it passes:

1. **Static Analysis**: `make quality` (Ruff linting & formatting).
1. **Security Audit**: `pip-audit` & `bandit` checks.
1. **Integrity Check**: `make verify-env` (Successful module resolution).

### 🏷️ Strict Typing

Python 3.13 type annotations are mandatory for all `infra` modules to ensure IDE stability and prevent runtime type errors in automation pipelines.
