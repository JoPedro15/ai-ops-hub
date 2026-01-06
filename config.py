# ruff: noqa: S101
from __future__ import annotations

import os
from pathlib import Path
from typing import Final

# --- 1. Project Root & Base Data Path ---
ROOT_DIR: Final[Path] = Path(__file__).parent.resolve()
DATA_DIR: Final[Path] = ROOT_DIR / "data"

# --- 2. Centralized Authentication (Secrets) ---
# Keeping auth files in /data as per project architecture
CREDS_PATH: Final[Path] = DATA_DIR / "credentials.json"
TOKEN_PATH: Final[Path] = DATA_DIR / "token.json"

# --- 3. AI Lifecycle Directories ---
# Standardized sub-folders for model training and reporting
RAW_DIR: Final[Path] = DATA_DIR / "raw"
PROCESSED_DIR: Final[Path] = DATA_DIR / "processed"
MODELS_DIR: Final[Path] = DATA_DIR / "models"
REPORTS_DIR: Final[Path] = DATA_DIR / "reports"
LOGS_DIR: Final[Path] = DATA_DIR / "logs"

# --- 4. Infrastructure & Integration Settings ---
LOG_FORMAT: Final[str] = "[{time}] {level}: {message}"

# Cloud Storage folder IDs from environment variables
OUTPUT_FOLDER_ID: Final[str | None] = os.getenv("OUTPUT_FOLDER_ID")
GDRIVE_PROC_DATA_ID: Final[str | None] = os.getenv("GDRIVE_DATA_PROCESSED_FOLDER_ID")
GDRIVE_MODELS_PROD_ID: Final[str | None] = os.getenv("GDRIVE_MODELS_PROD_FOLDER_ID")
GDRIVE_MODELS_DEV_ID: Final[str | None] = os.getenv("GDRIVE_MODELS_DEV_FOLDER_ID")


def ensure_paths() -> None:
    """
    Ensures that the entire mandatory directory structure exists.
    Creates .gitkeep files to maintain directory structure in Git.
    """
    mandatory_paths: list[Path] = [
        DATA_DIR,
        RAW_DIR,
        PROCESSED_DIR,
        MODELS_DIR,
        REPORTS_DIR,
        LOGS_DIR,
    ]

    for path in mandatory_paths:
        path.mkdir(parents=True, exist_ok=True)

        # Ensure a .gitkeep exists so empty folders are tracked by Git
        gitkeep: Path = path / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()


if __name__ == "__main__":
    # Lazy import to prevent circular dependency during module initialization
    from infra.common.logger import logger

    logger.section("Infrastructure Path Verification")
    logger.info(f"Project Root identified at: {ROOT_DIR}")

    ensure_paths()

    logger.success(f"Full directory structure verified at: {DATA_DIR}")
    if not OUTPUT_FOLDER_ID:
        logger.warning("OUTPUT_FOLDER_ID not found in environment variables.")
