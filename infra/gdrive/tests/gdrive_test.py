# ruff: noqa: S101
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Final

import pytest

# New centralized imports
from config import CREDS_PATH, OUTPUT_FOLDER_ID
from dotenv import load_dotenv
from infra.common.logger import logger
from infra.gdrive.service import GDriveService

# Dedicated directory for local test artifacts
TEST_OUTPUT_DIR: Final[Path] = Path(__file__).parent / "test_output"


@pytest.fixture(scope="module")
def gdrive_setup() -> tuple[GDriveService, str]:
    """
    Setup GDriveService and target folder for integration tests.
    Uses centralized configuration from root config.py.
    """
    load_dotenv()
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Resolution: using centralized paths from config.py
    folder_id: str | None = os.getenv("OUTPUT_FOLDER_ID") or OUTPUT_FOLDER_ID

    if not folder_id:
        logger.warning("OUTPUT_FOLDER_ID not set. Skipping integration tests.")
        pytest.skip("OUTPUT_FOLDER_ID not set in .env or config.py")

    if not CREDS_PATH.exists():
        logger.error(f"Required credentials missing at: {CREDS_PATH}")
        pytest.fail(f"Missing credentials.json at {CREDS_PATH}")

    # Initializing Service - No need to pass paths if GDriveService
    # already uses config.py as default
    service: GDriveService = GDriveService(
        output_folder_id=folder_id,
    )

    return service, folder_id


@pytest.mark.integration
def test_gdrive_full_lifecycle(gdrive_setup: tuple[GDriveService, str]) -> None:
    """
    Tests the complete CRUD lifecycle, including:
    1. Folder Cleanup (Pre-flight)
    2. Single File Upload & Existence Check
    3. Overwrite Logic
    4. Multi-file Upload & Listing
    5. Download & Content Integrity Verification
    6. Prefix-based Deletion
    7. Final Folder Clearing
    """
    service, folder_id = gdrive_setup

    # Test Data
    file_name: str = "integration_test.txt"
    file_content: str = "AI-Ops Hub: Data Integrity Test Content"
    local_path: Path = TEST_OUTPUT_DIR / file_name
    download_path: Path = TEST_OUTPUT_DIR / f"downloaded_{file_name}"

    try:
        # --- 1. PRE-FLIGHT CLEANUP ---
        service.clear_folder_content(folder_id)
        logger.info(f"Cleared folder {folder_id} for fresh integration test.")

        # --- 2. UPLOAD & EXISTENCE ---
        local_path.write_text(file_content, encoding="utf-8")
        file_id: str = service.upload_file(str(local_path), folder_id)

        assert file_id is not None
        assert service.file_exists(file_name, folder_id) is True
        logger.success(f"Upload and Existence check passed for {file_name}")

        # --- 3. OVERWRITE TEST ---
        # Modify content and upload again with overwrite=True
        new_content: str = "Updated Content for Overwrite Test"
        local_path.write_text(new_content, encoding="utf-8")

        updated_id: str = service.upload_file(
            str(local_path), folder_id, overwrite=True
        )
        assert updated_id == file_id  # Should update the same file ID
        logger.success("Overwrite logic verified (File ID remained consistent).")

        # --- 4. DOWNLOAD & INTEGRITY ---
        service.download_file(file_id, str(download_path))
        downloaded_content: str = download_path.read_text(encoding="utf-8")

        assert downloaded_content == new_content
        logger.success("Download integrity verified: Local content matches GDrive.")

        # --- 5. MULTI-FILE & PREFIX DELETION ---
        # Uploading multiple files with a shared prefix
        prefix: str = "batch_test_"
        batch_files: list[str] = [f"{prefix}1.txt", f"{prefix}2.txt"]

        for name in batch_files:
            p = TEST_OUTPUT_DIR / name
            p.write_text("Batch content", encoding="utf-8")
            service.upload_file(str(p), folder_id)

        time.sleep(1.5)  # Wait for API consistency

        all_files = service.list_files(folder_id)
        # Should have original file + 2 batch files = 3
        assert len(all_files) >= 3

        # Delete by prefix
        deleted_ids: list[str] = service.delete_files_by_prefix(folder_id, prefix)
        assert len(deleted_ids) == 2
        logger.success(f"Prefix-based deletion verified for prefix: '{prefix}'")

        # --- 6. FINAL CLEANUP ---
        service.clear_folder_content(folder_id)
        time.sleep(1)
        final_list = service.list_files(folder_id)
        assert len(final_list) == 0
        logger.success("Final cleanup complete. Remote folder is empty.")

    finally:
        # Local Artifact Cleanup
        if TEST_OUTPUT_DIR.exists():
            for f in TEST_OUTPUT_DIR.iterdir():
                f.unlink()
            TEST_OUTPUT_DIR.rmdir()
        logger.info("Local test artifacts removed.")
