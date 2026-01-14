# 🚀 AI-Ops Hub Monorepo

![Python 3.13](https://img.shields.io/badge/python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![CI Quality Pipeline](https://github.com/JoPedro15/ai-ops-hub/actions/workflows/ci-pipeline.yml/badge.svg?branch=main)
![On-Demand Test Runner](https://github.com/JoPedro15/ai-ops-hub/actions/workflows/infrastructure-health.yml/badge.svg?branch=main)
<br />
![Ruff](https://img.shields.io/badge/linter-Ruff-000000?style=flat-square&logo=python&logoColor=white)
![Security](https://img.shields.io/badge/security-Bandit%20%7C%20Audit-44cc11?style=flat-square&logo=shield&logoColor=white)
![GNU Make](https://img.shields.io/badge/env-GNU%20Make-active?style=flat-square&logo=gnu-make&logoColor=white)
<br />
![Stack](https://img.shields.io/badge/stack-Pandas%20%7C%20SciPy%20%7C%20Sklearn-FF9900?style=flat-square&logo=scikit-learn&logoColor=white)
![MIT License](https://img.shields.io/badge/license-MIT-607D8B?style=flat-square)

The **ai-ops-hub** is a high-performance monorepo designed to unify production-grade infrastructure with advanced
AI research.

By consolidating the legacy *Automation Hub* and *AI Lab* into a single ecosystem, this project establishes
a **Single Source of Truth (SSoT)** for machine learning operations, data orchestration, and automated health monitoring.

## 🏗️ Architecture & Structure

The hub is organized into clear functional layers, ensuring absolute separation of concerns between core utilities
and experimental research.

| Layer            | Path     | Description                                                                |
| :--------------- | :------- | :------------------------------------------------------------------------- |
| `Data (Storage)` | `data/`  | Centralized directory for raw/processed data, models, logs, and secrets.   |
| `Infrastructure` | `infra/` | Industrial-grade core modules (GDrive, AI Utils, Common Logging).          |
| `Laboratory`     | `lab/`   | AI experiments, Jupyter notebooks, and regression scripts.                 |
| `Governance`     | `docs/`  | Engineering standards, quality gates, and architectural conventions.       |
| `Tooling`        | `root`   | Global configuration (`config.py`, `.env`) and quality gates (`Makefile`). |

## 🔌 Core Infrastructure (infra/)

Each module within the `infra/` directory is designed following the **Direct Import Pattern** for maximum
performance and IDE discoverability.

### 🧪 [AI Utilities](infra/ai_utils/README.md)

A complete toolkit for the ML lifecycle:

- **Ingestor**: Smart loading for CSV, Parquet, and Excel (auto-engine detection).
- **Processor**: Scikit-learn integration for robust data splitting, scaling, and encoding.
- **Visualizer**: Production-ready plotting for Regression (Residuals) and Classification (Confusion Matrix).

### 🔐 Modular Credentials Vault

To ensure enterprise-grade security and scalability, all authentication artifacts are stored in a modular
structure within `infra/credentials/`.

This isolates sensitive tokens from the data processing layer.

- **GDrive Store**: `infra/credentials/gdrive/` (contains `credentials.json` and `token.json`).

#### ☁️ [Google Drive Service](infra/gdrive/README.md)

A resilient orchestration layer for Cloud Storage, featuring:

- **Auto-Export**: Converts Google Docs/Sheets/Slides to standard formats (DOCX/XLSX/PPTX).
- **Headless Mode**: Native support for CI/CD environments without browser interaction.
- **Resilience**: Automated token refresh and safe pagination logic.

### 📜 Common Lib

Home of our **Standardized Logger**. Enforces the project-wide **Zero-Print Policy** with ANSI-colored terminal
output.

## 🛠️ Global Quality Gate (GNU Make)

We leverage a unified orchestration system to maintain parity between local development and CI/CD pipelines.

| Command        | Description                                                                          |
| :------------- | :----------------------------------------------------------------------------------- |
| `make setup`   | Full environment initialization: VENV creation, 3.13 dependencies, and path mapping. |
| `make quality` | The mandatory gate: Unified Ruff (Lint/Fmt/Sec) + Pre-commit + Pytest.               |
| `make health`  | Executes the Infrastructure Health System to verify core integration status.         |
| `make clean`   | Purges all temporary caches, build artifacts, and Jupyter checkpoints.               |
| `make jupyter` | Launches a local JupyterLab instance for research within the `lab/` context.         |

## 🩺 [Infrastructure Health System](infra/scripts/health_check/README.md)

The hub features a dynamic diagnostic suite that validates the entire stack before executing any heavy AI workload.
The system uses a **Discovery Pattern** to locate and run independent verification modules.

**Monitored Components**:

- **Logger**: Validates singleton integrity and ANSI formatting.
- **GDrive**: Performs credential checks and API reachability smoke tests.
- **Ingestor**: Verifies cache IO permissions and engine dependencies.
- **Processor**: Executes logic tests for One-Hot Encoding and NaN handling.
- **Lab**: Inspects `.ipynb` files for structural integrity and kernel metadata.

## 📖 Governance & Standards

To maintain the hub's integrity, all contributions must adhere to these engineering standards:

- **Type Safety**: Mandatory type annotations for all methods and experimental variables.
- **Zero-Print Policy**: Raw `print()` statements are strictly forbidden; use the `infra.common.logger`.
- **Headless Compatibility**: OAuth2 flows are designed to detect non-interactive environments (CI/CD).
- **Notebook Integrity**: All `.ipynb` files must pass linting and logic validation via `nbqa`.

______________________________________________________________________

João Pedro | Automation Engineer <br /> [GitHub profile](https://github.com/JoPedro15)
