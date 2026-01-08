# ruff: noqa: S101
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

load_dotenv()

# --- Project Root & Base Paths ---
ROOT_DIR: Final[Path] = Path(__file__).parent.resolve()
DATA_DIR: Final[Path] = ROOT_DIR / "data"
INFRA_DIR: Final[Path] = ROOT_DIR / "infra"
DOCS_DIR: Final[Path] = ROOT_DIR / "docs"
LAB_DIR: Final[Path] = ROOT_DIR / "lab"

# --- Centralized Authentication (Secrets) ---
CRED_DIR_GDRIVE: Final[Path] = INFRA_DIR / "credentials" / "gdrive"
CREDS_PATH_GDRIVE: Final[Path] = CRED_DIR_GDRIVE / "credentials.json"
TOKEN_PATH_GDRIVE: Final[Path] = CRED_DIR_GDRIVE / "token.json"

# --- AI Lifecycle Directories ---
LOGS_DIR: Final[Path] = DATA_DIR / "logs"
MODELS_DIR: Final[Path] = DATA_DIR / "models"
RAW_DIR: Final[Path] = DATA_DIR / "raw"
PROCESSED_DIR: Final[Path] = DATA_DIR / "processed"
REPORTS_DIR: Final[Path] = DATA_DIR / "reports"

# --- Infrastructure & Integration Settings ---
LOG_FORMAT: Final[str] = "[{time}] {level}: {message}"

# --- Google Drive Infrastructure IDs ---

# Core & Lab
OUTPUT_FOLDER_ID: Final[str | None] = os.getenv("OUTPUT_FOLDER_ID")
GDRIVE_AILAB_FOLDER_ID: Final[str | None] = os.getenv("GDRIVE_AILAB_FOLDER_ID")

# Data Lifecycle
GDRIVE_DATA_FOLDER_ID: Final[str | None] = os.getenv("GDRIVE_DATA_FOLDER_ID")
GDRIVE_DATA_RAW_FOLDER_ID: Final[str | None] = os.getenv("GDRIVE_DATA_RAW_FOLDER_ID")
GDRIVE_DATA_PROCESSED_FOLDER_ID: Final[str | None] = os.getenv(
    "GDRIVE_DATA_PROCESSED_FOLDER_ID"
)

# Models & Analytics
GDRIVE_MODELS_FOLDER_ID: Final[str | None] = os.getenv("GDRIVE_MODELS_FOLDER_ID")
GDRIVE_MODELS_DEV_FOLDER_ID: Final[str | None] = os.getenv(
    "GDRIVE_MODELS_DEV_FOLDER_ID"
)
GDRIVE_MODELS_PROD_FOLDER_ID: Final[str | None] = os.getenv(
    "GDRIVE_MODELS_PROD_FOLDER_ID"
)
GDRIVE_REPORTS_FOLDER_ID: Final[str | None] = os.getenv("GDRIVE_REPORTS_FOLDER_ID")


def validate_config() -> None:
    """
    Validates infrastructure integrity using sys for logging.
    Ensures all physical paths exist and critical IDs are present.
    """
    mandatory_paths: list[Path] = [
        DATA_DIR,
        RAW_DIR,
        PROCESSED_DIR,
        MODELS_DIR,
        REPORTS_DIR,
        LOGS_DIR,
        DOCS_DIR,
        LAB_DIR,
        CRED_DIR_GDRIVE,
    ]

    for path in mandatory_paths:
        path.mkdir(parents=True, exist_ok=True)
        gitkeep: Path = path / ".gitkeep"
        if not gitkeep.exists() and not any(path.iterdir()):
            gitkeep.touch()

    critical_ids: dict[str, str | None] = {
        "OUTPUT_FOLDER_ID": OUTPUT_FOLDER_ID,
        "GDRIVE_DATA_RAW_FOLDER_ID": GDRIVE_DATA_RAW_FOLDER_ID,
        "GDRIVE_DATA_PROCESSED_FOLDER_ID": GDRIVE_DATA_PROCESSED_FOLDER_ID,
        "GDRIVE_MODELS_FOLDER_ID": GDRIVE_MODELS_FOLDER_ID,
        "GDRIVE_MODELS_DEV_FOLDER_ID": GDRIVE_MODELS_DEV_FOLDER_ID,
        "GDRIVE_MODELS_PROD_FOLDER_ID": GDRIVE_MODELS_PROD_FOLDER_ID,
        "GDRIVE_REPORTS_FOLDER_ID": GDRIVE_REPORTS_FOLDER_ID,
    }

    missing_critical = [name for name, val in critical_ids.items() if not val]

    if missing_critical:
        missing_str: str = ", ".join(missing_critical)
        sys.stderr.write(
            f"❌ FATAL ERROR: Missing critical environment variables: {missing_str}\n"
        )
        sys.stderr.write("Please check your .env file or GitHub Secrets.\n")
        sys.exit(1)

    for name, val in critical_ids.items():
        if val and ("/" in val or "\\" in val):
            sys.stderr.write(
                f"❌ FATAL ERROR: Variable {name} looks like a local path, "
                "but must be a GDrive ID.\n"
            )
            sys.exit(1)


validate_config()
