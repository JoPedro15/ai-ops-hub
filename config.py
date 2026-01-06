# ruff: noqa: S101
from __future__ import annotations

import os
from pathlib import Path
from typing import Final

from infra.common import logger

# Project Root Discovery
ROOT_DIR = Path(__file__).parent

# Centralized Data & Secrets
# As requested, keeping auth files in /data at the root level
DATA_DIR: Final[Path] = ROOT_DIR / "data"
CREDS_PATH: Final[Path] = DATA_DIR / "credentials.json"
TOKEN_PATH: Final[Path] = DATA_DIR / "token.json"

# Infrastructure Settings
LOG_FORMAT: str = "[{time}] {level}: {message}"

# Google Drive specific folder ID from env vars
OUTPUT_FOLDER_ID: Final[str | None] = os.getenv("OUTPUT_FOLDER_ID")


def ensure_paths() -> None:
    """
    Ensures that mandatory directory structures exist.
    """
    # Create the /data directory if it doesn't exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Optional: ensure a .gitkeep exists so the folder is tracked but files are ignored
    gitkeep: Path = DATA_DIR / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()


if __name__ == "__main__":
    # If run directly, it will verify and create the paths
    logger.info(f"Project Root: {ROOT_DIR}")
    ensure_paths()
    logger.success(f"Data directory verified at: {DATA_DIR}")
