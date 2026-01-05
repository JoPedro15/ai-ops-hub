# ruff: noqa: S101
from __future__ import annotations

import json
import os
from typing import Any  # Added Dict for explicit typing

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def get_google_service_credentials(
    credentials_path: str,
    token_path: str,
    scopes: list[str],
) -> Credentials:
    """
    Handles the OAuth2 flow and returns valid credentials.

    Args:
        credentials_path: Path to the Google Cloud credentials JSON.
        token_path: Path where the access token will be stored/loaded.
        scopes: List of authorized Google API scopes.
    """
    creds: Credentials | None = None

    # The file token.json stores the user's access and refresh tokens
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"Credentials file not found at {credentials_path}. "
                    "Please download it from Google Cloud Console."
                )

            flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, scopes
            )
            # This opens a browser window for manual authentication
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds


def load_credentials_safe(file_path: str) -> dict[str, Any]:
    """
    Safe loader to prevent JSONDecodeError in CI/CD pipelines.
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return {"status": "empty_or_missing", "path": file_path}

    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"status": "invalid_json", "path": file_path}
