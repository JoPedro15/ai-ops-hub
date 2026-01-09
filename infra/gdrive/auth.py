# ruff: noqa: S101
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Final

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from infra.common.logger import logger

# Default Scopes for Drive and Sheets
DEFAULT_SCOPES: Final[list[str]] = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_google_service_credentials(
    credentials_path: str | Path,
    token_path: str | Path,
    scopes: list[str] | None = None,
) -> Credentials:
    """
    Handles the OAuth2 flow and returns valid credentials.
    Standardized for ai-ops-hub headless and local environments.
    """
    selected_scopes: Final[list[str]] = scopes or DEFAULT_SCOPES
    creds_file: Final[Path] = Path(credentials_path)
    token_file: Final[Path] = Path(token_path)

    creds: Credentials | None = None

    # 1. Load existing token if available
    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(
                str(token_file), selected_scopes
            )
        except Exception as e:
            logger.warning(f"Existing token at {token_file.name} is invalid: {e}")

    # 2. Validation and Refresh Logic
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Access token expired. Refreshing session...")
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error("Failed to refresh token", e)
                creds = None  # Force re-authentication

        # 3. Manual Authentication Flow (Local Server)
        if not creds or not creds.valid:
            if not creds_file.exists():
                error_msg: str = f"Missing client secrets at {creds_file.absolute()}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            # Check if running in a TTY/Interactive environment
            if not sys.stdin.isatty():
                logger.error(
                    "Non-interactive environment detected. Manual login impossible."
                )
                raise PermissionError("Manual OAuth flow requires user interaction.")

            logger.section("Google OAuth2 Authentication")
            logger.info("Opening browser for authorization...")

            flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
                str(creds_file), selected_scopes
            )
            creds = flow.run_local_server(port=0)

        # 4. Save credentials for future use
        token_file.parent.mkdir(parents=True, exist_ok=True)
        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
        logger.success(f"Authentication successful. Token saved to {token_file.name}")

    return creds


def load_credentials_safe(file_path: str | Path) -> dict[str, Any]:
    """
    Safe loader to prevent JSONDecodeError in CI/CD pipelines.
    """
    path: Final[Path] = Path(file_path)

    if not path.exists() or path.stat().st_size == 0:
        return {"status": "empty_or_missing", "path": str(path.absolute())}

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in {path.name}", e)
        return {"status": "invalid_json", "path": str(path.absolute())}
