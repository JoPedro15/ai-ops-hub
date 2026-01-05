# 📂 Google Drive Client

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

A robust infrastructure connector for Google Drive API v3, tailored for the **AI-Ops Hub** ecosystem.
This service abstracts the complexity of the Google Discovery API, providing a high-level interface
for file orchestration.

It provides a standardized interface for file orchestration, abstracting the complexity of the Google Discovery API.

## ⚙️ Features

- **Automated OAuth2**: Supports `service_account` and `authorized_user` flows with transparent token management.
- **Service Pattern**: Optimized for dependency injection into AI processing pipelines.
- **Type-Safe Operations**: Fully annotated methods for 100% reliable automation scripts.
- **Advanced Cleanup**: Built-in logic for prefix-based deletion and safe trashing of output directories.

## 📋 Prerequisites

Before initialization, ensure you have:

1. A **Google Cloud Project** with the Drive API enabled.
1. A `credentials.json` file placed in the `data/` directory (git-ignored).
1. Python 3.13+ environment managed via the root `Makefile`.

## 🛠 Orchestration

This service is part of the `infra` layer. Installation and environment readiness are managed at the root level:

```bash
# Initialize the entire hub environment
make setup

# Run GDrive specific verification
make verify-env
```

## 🏗 Usage

Leverage the **Facade Pattern** by importing the service from the `infra` package:

```python
from infra.gdrive import GDriveService

# Initialize (Default paths: data/credentials.json | data/token.json)
service: GDriveService = GDriveService()

# List files in a specific folder
files: list[dict[str, str]] = service.list_files(
    folder_id="your_folder_id_here",
    limit=10
)

# Upload with automatic overwrite check
file_id: str = service.upload_file(
    file_path="reports/analysis.xlsx",
    folder_id="your_folder_id_here",
    overwrite=True
)
```

### Core API Reference

| Method                   | Signature                                        | Description                                     |
| :----------------------- | :----------------------------------------------- | :---------------------------------------------- |
| `upload_file`            | `(path: str, f_id: str, overwrite: bool) -> str` | Uploads file and returns the GDrive File ID.    |
| `download_file`          | `file_id: str, local_path: str) -> None`         | Downloads file (Auto-converts GSheets to XLSX). |
| `list_files`             | `(folder_id: str, limit: int) -> list[dict]`     | Lists non-trashed files in a folder.            |
| `delete_files_by_prefix` | `(folder_id: str, prefix: str) -> list[str]`     | Performs precise cleanup based on filename.     |
| `clear_folder_content`   | `(folder_id: str) -> list[str]`                  | Safely moves all folder content to Trash.       |

## 🧪 Quality Assurance

Managed via the root Quality Gate:

- **Linting**: Enforced by `Ruff` (standardized 88 line-length).
- **Security**: Monitored by `Bandit` and `detect-secrets`.
- **Testing**: Unified suite via `pytest`.

```Bash
# Execute full quality pipeline
make quality
```

______________________________________________________________________

**João Pedro** | Automation Engineer
<br />
[GitHub](https://github.com/JoPedro15) • [Automation Hub](https://github.com/JoPedro15/automation-hub) • [AI Lab](https://github.com/JoPedro15/ai-lab)
<br />
