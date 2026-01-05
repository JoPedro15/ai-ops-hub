from __future__ import annotations

import json
import os
from typing import Any  # Added missing imports

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def get_google_service_credentials(
    credentials_path: str, token_path: str, scopes: list[str]
) -> Credentials:
    """
    Handles the OAuth2 flow and returns valid credentials.
    """
    creds: Credentials | None = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Note: run_local_server will fail in headless CI environments.
            # This flow is intended for local development.
            flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, scopes
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def load_credentials(file_path: str) -> dict[str, Any]:
    """
    Load Google Drive credentials with safety checks for CI environments.

    This prevents JSONDecodeError when files are initialized as empty
    by the CI pipeline or pre-commit hooks.
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return {"status": "missing_credentials", "path": file_path}

    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"status": "invalid_json", "path": file_path}
