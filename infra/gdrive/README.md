# Google Drive Infrastructure Module

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

A robust infrastructure service for Google Drive API v3, acting as the primary storage orchestration layer
for the **ai-ops-hub** ecosystem.

This module abstracts the complexity of the Google Discovery API, providing a high-level,
type-safe interface for the entire monorepo.

## Features

- **Automated OAuth2**: Transparent token management with automatic refresh logic using the
  centralized `infra/credentials/` vault.
- **Hybrid Path Support**: Native compatibility with `pathlib.Path` and standardized strings.
- **Smart Asset Persistence**: Built-in overwrite logic that preserves File IDs, ensuring consistent
  downstream links for AI models and datasets.
- **Orchestrated Cleanup**: Methods for prefix-based deletion and permanent folder clearing to maintain cloud hygiene.
- **Auto-Export Engine**: Automatically converts Google-native formats (Sheets) to Data Science standards (`.xlsx`).

## 🔐 Credentials & Security

Following our **Modular Credentials Vault** standard, this module expects:

1. **`credentials.json`**: Placed in `infra/credentials/gdrive/`.
1. **`token.json`**: Managed automatically in the same directory.
1. **Environment**: `OUTPUT_FOLDER_ID` defined in the root `.env`.

## 🚀 Internal Usage

The service is designed for direct injection into other modules (like `ai_utils`) or lab experiments:

```python
from pathlib import Path
from infra.gdrive.service import GDriveService
from config import REPORTS_DIR

# Initialize (Automatically resolves credentials from infra/credentials/gdrive/)
service: GDriveService = GDriveService()

# Managed Upload (Path objects supported)
report_path: Path = REPORTS_DIR / "crossfit_performance_stats.xlsx"
file_id: str = service.upload_file(
    file_path=report_path,
    folder_id="target_folder_id",
    overwrite=True
)

# Seamless Download
service.download_file(
    file_id=file_id,
    local_path=Path("data/raw/cars_dataset.xlsx")
)
```

## Health Monitoring

Integrity is verified via the [Infrastructure Health System](../../infra/scripts/health_check/README.md).

The `health_check_gdrive.py` module performs:

- Credential file discovery.
- API reachability smoke tests.
- Scope validation.

## Quality Standards

- **Linting**: Enforced by `Ruff` (88 line-length).
- **Security**: Monitored by `Bandit` and `detect-secrets`.
- **Zero-Print**: All operations use `infra.common.logger`.

______________________________________________________________________

João Pedro | Automation Engineer <br /> [GitHub profile](https://github.com/JoPedro15)
