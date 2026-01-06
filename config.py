# ruff: noqa: S101
from __future__ import annotations

import os
from pathlib import Path
from typing import Final

# --- 1. Path Definitions (No project imports allowed here) ---
ROOT_DIR: Final[Path] = Path(__file__).parent

# Centralized Data & Secrets
# Auth files are kept in /data at the root level
DATA_DIR: Final[Path] = ROOT_DIR / "data"
CREDS_PATH: Final[Path] = DATA_DIR / "credentials.json"
TOKEN_PATH: Final[Path] = DATA_DIR / "token.json"

# --- 2. Infrastructure Settings ---
LOG_FORMAT: Final[str] = "[{time}] {level}: {message}"

# Google Drive specific folder ID from env vars
OUTPUT_FOLDER_ID: Final[str | None] = os.getenv("OUTPUT_FOLDER_ID")


def ensure_paths() -> None:
    """
    Ensures that mandatory directory structures exist.
    """
    # Create the /data directory if it doesn't exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure a .gitkeep exists so the folder structure is tracked
    gitkeep: Path = DATA_DIR / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()


if __name__ == "__main__":
    # Lazy import inside the main block to prevent circular dependency
    # during module initialization.
    from infra.common.logger import logger

    logger.info(f"Project Root: {ROOT_DIR}")
    ensure_paths()
    logger.success(f"Data directory verified at: {DATA_DIR}")
