# ruff: noqa: S101
from __future__ import annotations

import os
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

# --- Specific Assets ---
CAR_DATA_FILE_ID: Final[str | None] = os.getenv("CAR_DATA_FILE_ID")


def ensure_paths() -> None:
    """
    Ensures that the entire mandatory directory structure exists.
    """
    mandatory_paths: list[Path] = [
        DATA_DIR,
        CRED_DIR_GDRIVE,
        RAW_DIR,
        PROCESSED_DIR,
        MODELS_DIR,
        REPORTS_DIR,
        LOGS_DIR,
        DOCS_DIR,
        LAB_DIR,
    ]

    for path in mandatory_paths:
        path.mkdir(parents=True, exist_ok=True)
        gitkeep: Path = path / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()


if __name__ == "__main__":
    from infra.common.logger import logger

    critical_ids = [
        GDRIVE_DATA_RAW_FOLDER_ID,
        GDRIVE_DATA_PROCESSED_FOLDER_ID,
        CAR_DATA_FILE_ID,
    ]
    if not all(critical_ids):
        logger.warning(
            "Some Data Lifecycle IDs are missing in .env. Verify connectivity."
        )
    logger.section("Infrastructure Path Verification")
    logger.info(f"Targeting Credentials at: {CREDS_PATH_GDRIVE}")
    if CREDS_PATH_GDRIVE.exists():
        logger.success("Credentials file FOUND.")
    else:
        logger.error("Credentials file NOT FOUND at this location.")
    logger.info(f"Project Root identified at: {ROOT_DIR}")
    ensure_paths()
    logger.success("Full directory structure verified.")

    if not OUTPUT_FOLDER_ID:
        logger.warning("OUTPUT_FOLDER_ID not found. GDrive tests will be skipped.")
