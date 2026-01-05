# ruff: noqa: S101
from __future__ import annotations

import os
import time
from pathlib import Path

import pytest
from dotenv import load_dotenv

from infra.common.logger import logger
from infra.gdrive.service import GDriveService

# Use a dedicated test output directory inside the test folder
TEST_OUTPUT_DIR: Path = Path(__file__).parent / "test_output"


@pytest.fixture(scope="module")
def gdrive_setup() -> tuple[GDriveService, str]:
    """
    Setup GDriveService and target folder for integration tests.
    Ensures environment variables and credentials are present.
    """
    load_dotenv()
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Resolution relative to ai-ops-hub/infra/gdrive/tests/
    # 3 levels up to reach project root
    root: Path = Path(__file__).parent.parent.parent.parent
    creds_path: Path = root / "data" / "credentials.json"
    token_path: Path = root / "data" / "token.json"

    folder_id: str | None = os.getenv("OUTPUT_FOLDER_ID")

    if not folder_id:
        logger.warning("OUTPUT_FOLDER_ID not set. Skipping integration tests.")
        pytest.skip("OUTPUT_FOLDER_ID not set.")

    if not creds_path.exists():
        logger.error(f"Required credentials missing at: {creds_path}")
        pytest.fail("Missing credentials.json for integration test.")

    # Initialize the new Service class
    service: GDriveService = GDriveService(
        credentials_path=str(creds_path),
        token_path=str(token_path),
        output_folder_id=folder_id,
    )

    return service, folder_id


@pytest.mark.integration
def test_gdrive_full_lifecycle(gdrive_setup: tuple[GDriveService, str]) -> None:
    """
    Tests the full CRUD lifecycle of files in Google Drive.

    Validation Steps:
    1. Clean cloud state
    2. Upload & Overwrite check
    3. Multi-file listing
    4. Specific deletion
    5. Prefix-based deletion
    6. Final cleanup
    """
    service, folder_id = gdrive_setup

    file_names: list[str] = ["test_1.txt", "test_2.txt", "test_3.txt"]
    local_paths: list[Path] = [TEST_OUTPUT_DIR / name for name in file_names]

    try:
        logger.section("GDrive Integration Lifecycle Start")

        # --- STEP 1: Pre-test Cleanup ---
        logger.info(f"Clearing folder {folder_id} before starting...")
        service.clear_folder_content(folder_id)

        # --- STEP 2: Single File Upload ---
        target_path: Path = local_paths[0]
        target_path.write_text(
            "Automation test content for ai-ops-hub", encoding="utf-8"
        )

        file_id_1: str = service.upload_file(str(target_path), folder_id)
        assert file_id_1 is not None
        assert service.file_exists(file_names[0], folder_id) is True
        logger.success("Single file upload and existence verified.")

        # --- STEP 3: Multiple Files & Listing ---
        for path in local_paths[1:]:
            path.write_text(f"Content for {path.name}", encoding="utf-8")
            service.upload_file(str(path), folder_id)

        time.sleep(1.5)  # Wait for API consistency (Propagation)

        files_list: list[dict[str, str]] = service.list_files(folder_id)
        assert len(files_list) == 3
        logger.success(f"Listed {len(files_list)} files successfully.")

        # --- STEP 4: Specific Deletion ---
        service.delete_specific_file(file_names[2], folder_id)
        time.sleep(1)
        assert service.file_exists(file_names[2], folder_id) is False
        assert len(service.list_files(folder_id)) == 2
        logger.success(f"Specific deletion of {file_names[2]} verified.")

        # --- STEP 5: Prefix Deletion ---
        # Testing the prefix logic: 'test_' should match 'test_1' and 'test_2'
        deleted_ids: list[str] = service.delete_files_by_prefix(folder_id, "test_")
        time.sleep(1)
        assert len(deleted_ids) == 2
        assert len(service.list_files(folder_id)) == 0
        logger.success("Prefix-based deletion verified. Folder is empty.")

    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")
        raise e

    finally:
        # Local cleanup
        for path in local_paths:
            if path.exists():
                path.unlink()
        if TEST_OUTPUT_DIR.exists():
            TEST_OUTPUT_DIR.rmdir()
        logger.info("Local test artifacts cleaned.")
