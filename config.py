# config.py
import os
from pathlib import Path
from typing import Final

# Project Root Discovery
ROOT_DIR: Final[Path] = Path(__file__).parent.absolute()

# Centralized Data & Secrets
DATA_DIR: Final[Path] = ROOT_DIR / "data"
CREDS_PATH: Final[Path] = DATA_DIR / "credentials.json"
TOKEN_PATH: Final[Path] = DATA_DIR / "token.json"

# Infrastructure Settings
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
OUTPUT_FOLDER_ID: Final[str] = os.getenv("OUTPUT_FOLDER_ID", "")


def ensure_paths() -> None:
    """
    Ensures that mandatory directory structures exist.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # If run directly, it will verify and create the paths
    ensure_paths()
