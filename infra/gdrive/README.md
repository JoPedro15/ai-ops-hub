# Google Drive Client

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

A robust infrastructure connector for Google Drive API v3, tailored for the **ai-ops-hub** ecosystem.

This service provides a high-level interface for file orchestration, abstracting the complexity of the
Google Discovery API.

## Features

- **Automated OAuth2**: Transparent token management with automatic refresh logic.
- **Hybrid Path Support**: Native compatibility with `pathlib.Path` and standard strings.
- **Smart Uploads**: Built-in overwrite logic that preserves File IDs for consistent downstream links.
- **Advanced Cleanup**: Orchestrated methods for prefix-based deletion and permanent folder clearing.
- **Auto-Export**: Automatically converts Google-native formats (Sheets) to Data Science standards (XLSX).

## Prerequisites

Before initialization, ensure you have:

1. A **Google Cloud Project** with the Drive API enabled.
1. A `credentials.json` file placed in the `data/` directory.
1. A `.env` file containing the `OUTPUT_FOLDER_ID`.

## Usage

The service integrates seamlessly with the centralized `config.py` definitions:

```python
from pathlib import Path
from infra.gdrive.service import GDriveService
from config import REPORTS_DIR

# Initialize (Uses CREDS_PATH and TOKEN_PATH from config.py by default)
service: GDriveService = GDriveService()

# Upload a report (Path objects supported)
report_path: Path = REPORTS_DIR / "analysis_v1.xlsx"
file_id: str = service.upload_file(
    file_path=report_path,
    folder_id="target_folder_id",
    overwrite=True
)

# Download and recover data
service.download_file(
    file_id=file_id,
    local_path="data/raw/recovered_data.xlsx"
)
```

## Quality Assurance

Managed via the root Quality Gate:

- **Linting**: Enforced by `Ruff` (standardized 88 line-length).
- **Security**: Monitored by `Bandit` and `detect-secrets`.
- **Testing**: Unified suite via `pytest`.

```Bash
# Execute full quality pipeline
make quality
```

______________________________________________________________________

João Pedro | Automation Engineer <br /> [GitHub profile](https://github.com/JoPedro15)
