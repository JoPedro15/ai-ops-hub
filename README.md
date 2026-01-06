# 🚀 AI-Ops Hub Monorepo

## 🎯 Overview

The ai-ops-hub is a high-performance monorepo that unifies production-grade infrastructure with advanced AI research

By consolidating the legacy Automation Hub and AI Lab into a single ecosystem, this project establishes a Single Source
of Truth (SSoT) for machine learning operations, data orchestration, and automated health monitoring.

## 🏗️ Architecture & Structure

The hub is organized into clear functional layers, ensuring absolute separation of concerns between core utilities
and experimental research.

| Layer            | Path     | Description                                                                |
| :--------------- | :------- | :------------------------------------------------------------------------- |
| `Data (Storage)` | `data/`  | Centralized directory for raw/processed data, models, logs, and secrets.   |
| `Infrastructure` | `infra/` | Industrial-grade core modules (GDrive, AI Utils, Common Logging).          |
| `Laboratory`     | `lab/`   | AI experiments, Jupyter notebooks, and regression scripts.                 |
| `Governance`     | `docs/`  | Engineering standards, quality gates, and architectural conventions.       |
| `Tooling`        | `root`   | Global configuration (`config.py`, `.env`) and quality gates (\`Makefile). |

## 🔌 Core Infrastructure (infra/)

Each module within the `infra/` directory is designed following the Direct Import Pattern for maximum performance
and IDE discoverability.

### AI Utilities

Managed data acquisition and feature engineering. Supports automated cache invalidation and hybrid Excel processing (`.xls` and `.xlsx`).

### Google Drive Service

A resilient orchestration layer for Cloud Storage, featuring automated OAuth2 flows, prefix-based cleanup, and bit-for-bit integrity checks.

### Common Lib

Home of our Standardized Logger. Enforces the project-wide Zero-Print Policy with ANSI-colored terminal output and local file persistence.

## 🛠️ Global Quality Gate (GNU Make)

We leverage a unified orchestration system to maintain parity between local development and CI/CD pipelines.

| Command        | Description                                                                          |
| :------------- | :----------------------------------------------------------------------------------- |
| `make setup`   | Full environment initialization: VENV creation, 3.13 dependencies, and path mapping. |
| `make quality` | The mandatory gate: Unified Ruff (Lint/Fmt/Sec) + Pre-commit + Pytest.               |
| `make health`  | Executes the Infrastructure Health System to verify core integration status.         |
| `make clean`   | Purges all temporary caches, build artifacts, and Jupyter checkpoints.               |
| `make jupyter` | Launches a local JupyterLab instance for research within the `lab/` context.         |

## 🩺 Infrastructure Health System

The hub features a dynamic diagnostic suite that validates the entire stack before executing any heavy AI workload.
The system uses a Discovery Pattern to locate and run independent verification modules.

**Monitored Components**:

- **Logger**: Validates singleton integrity and ANSI formatting.
- **GDrive**: Performs credential checks and API reachability smoke tests.
- **Ingestor**: Verifies cache IO permissions and engine dependencies (`openpyxl`, \`xlrd).
- **Processor**: Executes logic tests for One-Hot Encoding and NaN handling.
- **Lab**: Inspects `.ipynb` files for structural integrity and kernel metadata.

**How it Works**

- **Auto-Discovery**: Scans for modules following the `health_check_*.py` convention.
- **Contract-Based**: Each check must implement `run_check() -> tuple[bool, str]`.
- **Audit Trail**: Results are mirrored to `data/logs/infrastructure.log` via the core Logger.

# 📖 Governance & Standards

To maintain the hub's integrity, all contributions must adhere to these engineering standards:

- **Type Safety**: Mandatory type annotations for all methods and experimental variables.
- **Zero-Print Policy**: Raw `print()` statements are strictly forbidden; use the `infra.common.logger`.
- **Headless Compatibility**: OAuth2 flows are designed to detect non-interactive environments (CI/CD).
- **Notebook Integrity**: All `.ipynb` files must pass linting and logic validation via `nbqa`.

______________________________________________________________________

João Pedro | Automation Engineer <br /> [GitHub profile](https://github.com/JoPedro15)
