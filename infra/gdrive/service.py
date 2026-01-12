# ruff: noqa: S101
from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Any, Final

# Centralized imports from root config
from config import CREDS_PATH_GDRIVE, OUTPUT_FOLDER_ID, TOKEN_PATH_GDRIVE
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from infra.common.logger import logger

# Modular internal imports
from infra.gdrive.auth import get_google_service_credentials

# Explicitly defining the public API of this module
__all__: list[str] = ["GDriveService"]


class GDriveService:
    """
    Module to interact with Google Drive API v3.
    Handles authentication, file management, and advanced cleanup logic.
    """

    # MIME Type Mappings for Google Workspace Export
    _MIME_EXPORT_MAP: Final[dict[str, str]] = {
        "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # Sheets -> XLSX
        "application/vnd.google-apps.document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # Docs -> DOCX
        "application/vnd.google-apps.presentation": "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # Slides -> PPTX
    }

    def __init__(
        self,
        credentials_path: str = str(CREDS_PATH_GDRIVE),
        token_path: str = str(TOKEN_PATH_GDRIVE),
        output_folder_id: str | None = None,
    ) -> None:
        """
        Initializes the service using centralized configuration.
        """
        # Path Resolution Strategy: Arg > Project Default (from config.py)
        self.credentials_path: str = credentials_path
        self.token_path: str = token_path

        if not Path(self.credentials_path).exists():
            logger.error(
                f"Critical Failure: GDrive credentials not found at {self.credentials_path}"
            )

        # Output folder: Arg > Config Default
        self.output_folder_id: str | None = output_folder_id or OUTPUT_FOLDER_ID

        # Ensure directory for auth artifacts exists
        Path(self.token_path).parent.mkdir(parents=True, exist_ok=True)

        self.scopes: Final[list[str]] = ["https://www.googleapis.com/auth/drive"]
        self.service: Resource = self._init_service()

    def _init_service(self) -> Resource:
        """
        Builds the authorized Google Drive API service resource.
        """
        if not os.path.exists(self.credentials_path):
            logger.error(f"Credentials file not found at: {self.credentials_path}")
            raise FileNotFoundError(
                f"Missing Google credentials: {self.credentials_path}"
            )

        creds: Any = get_google_service_credentials(
            self.credentials_path, self.token_path, self.scopes
        )
        return build("drive", "v3", credentials=creds)

    def upload_file(
        self, file_path: str | Path, folder_id: str, overwrite: bool = True
    ) -> str:
        """
        Uploads a file to a specific GDrive folder.
        If overwrite is True, it replaces existing files with the same name.
        """
        str_path: str = str(file_path)
        file_name: str = os.path.basename(str_path)
        media: MediaFileUpload = MediaFileUpload(str_path, resumable=True)

        if overwrite:
            # Escape single quotes in file names for the query
            safe_name: str = file_name.replace("'", "\\'")
            query: str = (
                f"name = '{safe_name}' and '{folder_id}' in parents and trashed = false"
            )
            response: dict[str, Any] = (
                self.service.files().list(q=query, fields="files(id)").execute()
            )
            existing_files: list[dict[str, str]] = response.get("files", [])

            if existing_files:
                file_id: str = existing_files[0]["id"]
                logger.info(f"Overwriting file: {file_name} (ID: {file_id})")
                updated_file = (
                    self.service.files()
                    .update(fileId=file_id, media_body=media)
                    .execute()
                )
                return str(updated_file.get("id"))

        file_metadata: dict[str, Any] = {"name": file_name, "parents": [folder_id]}
        logger.info(f"Creating new file: {file_name}")
        new_file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        return str(new_file.get("id"))

    def file_exists(self, file_name: str, folder_id: str) -> bool:
        """
        Verifies if a file exists within a specific folder.
        """
        safe_name: str = file_name.replace("'", "\\'")
        query: str = (
            f"name = '{safe_name}' and '{folder_id}' in parents and trashed = false"
        )
        results: dict[str, Any] = (
            self.service.files()
            .list(q=query, spaces="drive", fields="files(id)")
            .execute()
        )

        return len(results.get("files", [])) > 0

    def _fetch_files(
        self, query: str, fields: str = "id, name", max_pages: int = 20
    ) -> list[dict[str, str]]:
        """
        Internal helper to fetch all files matching a query with pagination support.
        Args:
            max_pages: Safety limit to prevent infinite loops (default: 20).
        """
        all_files: list[dict[str, str]] = []
        page_token: str | None = None
        page_count: int = 0

        while True:
            if page_count >= max_pages:
                logger.warning(
                    f"Pagination limit reached ({max_pages} pages). Stopping fetch."
                )
                break

            results: dict[str, Any] = (
                self.service.files()
                .list(
                    q=query,
                    fields=f"nextPageToken, files({fields})",
                    pageToken=page_token,
                    spaces="drive",
                )
                .execute()
            )

            all_files.extend(results.get("files", []))
            page_token = results.get("nextPageToken")
            page_count += 1

            if not page_token:
                break

        return all_files

    def download_file(self, file_id: str, local_path: str | Path) -> None:
        """
        Downloads a file. Supports standard binary files and Google Editor exports.
        Automatically converts Sheets to XLSX, Docs to DOCX, Slides to PPTX.
        """
        str_local_path: str = str(local_path)
        file_metadata: dict[str, Any] = (
            self.service.files().get(fileId=file_id, fields="mimeType, name").execute()
        )

        mime_type: str = file_metadata.get("mimeType", "")
        logger.info(f"Downloading {file_metadata.get('name')} (MIME: {mime_type})")

        # Check if it's a Google Workspace file that needs export
        if mime_type in self._MIME_EXPORT_MAP:
            export_mime: str = self._MIME_EXPORT_MAP[mime_type]
            logger.info(f"Exporting Google Workspace file to: {export_mime}")
            request = self.service.files().export_media(
                fileId=file_id, mimeType=export_mime
            )
        else:
            # Standard binary download
            request = self.service.files().get_media(fileId=file_id)

        with io.FileIO(str_local_path, "wb") as fh:
            downloader: MediaIoBaseDownload = MediaIoBaseDownload(fh, request)
            done: bool = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.info(f"Download Progress: {int(status.progress() * 100)}%")

        logger.success(f"File saved to: {str_local_path}")

    def list_files(
        self, folder_id: str | None = None, limit: int = 10
    ) -> list[dict[str, str]]:
        """
        Lists files in a specific folder or the default output folder.
        """
        query: str = "trashed = false"
        target_folder: str | None = folder_id or self.output_folder_id

        if target_folder:
            query += f" and '{target_folder}' in parents"

        results: dict[str, Any] = (
            self.service.files()
            .list(q=query, spaces="drive", fields="files(id, name)", pageSize=limit)
            .execute()
        )

        return results.get("files", [])

    def _list_and_delete(self, query: str) -> list[str]:
        """
        Fetches files matching a query and deletes them permanently.
        """
        files_to_delete: list[dict[str, str]] = self._fetch_files(query)
        deleted_ids: list[str] = []

        for f in files_to_delete:
            self.service.files().delete(fileId=f["id"]).execute()
            deleted_ids.append(f["id"])
            logger.success(f"Permanently deleted: {f['name']} ({f['id']})")

        return deleted_ids

    def delete_specific_file(self, file_name: str, folder_id: str) -> bool:
        """
        Deletes a specific file by name within a folder.
        """
        safe_name: str = file_name.replace("'", "\\'")
        query: str = (
            f"name = '{safe_name}' and '{folder_id}' in parents and trashed = false"
        )
        deleted: list[str] = self._list_and_delete(query)
        return len(deleted) > 0

    def clear_folder_content(self, folder_id: str) -> list[str]:
        """
        Clears all contents of a specific folder.
        """
        if not folder_id:
            logger.warning("No folder_id provided for clearing content.")
            return []

        query: str = f"'{folder_id}' in parents and trashed = false"
        return self._list_and_delete(query)

    def delete_files_by_prefix(self, folder_id: str, file_prefix: str) -> list[str]:
        """
        Deletes files matching a specific prefix within a folder.
        """
        if not folder_id or not file_prefix:
            logger.warning("Prefix or Folder ID missing for deletion.")
            return []

        query: str = (
            f"'{folder_id}' in parents and "
            f"name contains '{file_prefix}' and "
            f"trashed = false"
        )
        files_found: list[dict[str, str]] = self._fetch_files(query)

        # Precise filtering to avoid partial matches
        file_ids_to_delete: list[str] = [
            f["id"] for f in files_found if f["name"].startswith(file_prefix)
        ]

        deleted_ids: list[str] = []
        for fid in file_ids_to_delete:
            try:
                self.service.files().delete(fileId=fid).execute()
                deleted_ids.append(fid)
                logger.success(f"Deleted prefix match: {fid}")
            except Exception as e:
                logger.error(f"Failed to delete file {fid}: {str(e)}")

        return deleted_ids
