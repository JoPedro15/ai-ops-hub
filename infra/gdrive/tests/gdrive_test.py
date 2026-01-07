# ruff: noqa: S101
from __future__ import annotations

import time
from pathlib import Path
from typing import Final

import pytest

# Centralized configuration and tools
from config import CREDS_PATH_GDRIVE, DATA_DIR, OUTPUT_FOLDER_ID
from dotenv import load_dotenv
from infra.common.logger import logger
from infra.gdrive.service import GDriveService

# Standardized path for test artifacts using project DATA_DIR
TEST_OUTPUT_DIR: Final[Path] = DATA_DIR / "test_output"


@pytest.fixture(scope="module")
def gdrive_setup() -> tuple[GDriveService, str]:
    """
    Initializes GDriveService and prepares the environment for integration tests.
    """
    load_dotenv()
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Resolution order: Env Var -> config.py Default
    folder_id: str | None = OUTPUT_FOLDER_ID

    if not folder_id:
        logger.warning("OUTPUT_FOLDER_ID not found. Skipping integration suite.")
        pytest.skip("Missing target folder ID for GDrive tests.")

    if not CREDS_PATH_GDRIVE.exists():
        logger.error(
            f"Credentials not found at {CREDS_PATH_GDRIVE}. Check your data/ folder."
        )
        pytest.fail("Missing credentials.json for authentication.")

    # Service should default to config.py paths internally
    service: GDriveService = GDriveService()

    return service, folder_id


@pytest.mark.integration
def test_gdrive_full_lifecycle(gdrive_setup: tuple[GDriveService, str]) -> None:
    """
    Validates the complete CRUD operation flow on Google Drive.
    """
    service, folder_id = gdrive_setup

    # Test Artifacts
    test_file_name: str = "integration_audit.txt"
    test_content: str = "AI-Ops Hub | Lifecycle Test | Integrity Verified"
    local_path: Path = TEST_OUTPUT_DIR / test_file_name
    download_path: Path = TEST_OUTPUT_DIR / f"recovery_{test_file_name}"

    try:
        # --- 1. PRE-FLIGHT CLEANUP ---
        # Ensures a deterministic starting state
        service.clear_folder_content(folder_id)
        logger.info(f"Pre-flight: Folder {folder_id} cleared.")

        # --- 2. UPLOAD & VERIFICATION ---
        local_path.write_text(test_content, encoding="utf-8")
        file_id: str = service.upload_file(str(local_path), folder_id)

        assert file_id is not None
        # Adding a small sleep to allow GDrive index to update
        time.sleep(1)
        assert service.file_exists(test_file_name, folder_id) is True
        logger.success(f"Upload verified: {test_file_name} exists on remote.")

        # --- 3. OVERWRITE VALIDATION ---
        updated_content: str = "New version of content for overwrite testing."
        local_path.write_text(updated_content, encoding="utf-8")

        # Overwrite should maintain the same File ID
        new_file_id: str = service.upload_file(
            str(local_path), folder_id, overwrite=True
        )
        assert new_file_id == file_id
        logger.success("Overwrite logic confirmed (File ID stability).")

        # --- 4. DOWNLOAD & INTEGRITY CHECK ---
        service.download_file(file_id, str(download_path))
        downloaded_text: str = download_path.read_text(encoding="utf-8")

        assert downloaded_text == updated_content
        logger.success("Bit-for-bit integrity verified after download.")

        # --- 5. BATCH OPERATIONS & PREFIX DELETION ---
        batch_prefix: str = "temp_batch_"
        for i in range(2):
            p = TEST_OUTPUT_DIR / f"{batch_prefix}{i}.tmp"
            p.write_text("Batch data", encoding="utf-8")
            service.upload_file(str(p), folder_id)

        # Allow time for batch processing in GDrive API
        time.sleep(2)

        current_files = service.list_files(folder_id)
        assert len(current_files) >= 3  # Original + 2 batch files

        # Cleanup by prefix
        deleted_count: list[str] = service.delete_files_by_prefix(
            folder_id, batch_prefix
        )
        assert len(deleted_count) == 2
        logger.success(f"Batch cleanup verified (Prefix: {batch_prefix}).")

        # --- 6. FINAL TEARDOWN ---
        service.clear_folder_content(folder_id)
        time.sleep(1)
        assert len(service.list_files(folder_id)) == 0
        logger.success("Integration lifecycle complete: Remote folder cleaned.")

    except Exception as e:
        logger.error("Integration test crashed", e)
        raise e

    finally:
        # Local cleanup of generated artifacts
        if TEST_OUTPUT_DIR.exists():
            for artifact in TEST_OUTPUT_DIR.iterdir():
                artifact.unlink()
            TEST_OUTPUT_DIR.rmdir()
        logger.info("Local test artifacts purged.")
