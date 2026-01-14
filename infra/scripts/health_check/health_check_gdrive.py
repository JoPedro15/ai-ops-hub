from pathlib import Path
from typing import Final

from infra.common.config import (
    CREDS_PATH_GDRIVE,
    GDRIVE_AILAB_FOLDER_ID,
    GDRIVE_DATA_FOLDER_ID,
    GDRIVE_DATA_PROCESSED_FOLDER_ID,
    GDRIVE_DATA_RAW_FOLDER_ID,
    GDRIVE_MODELS_DEV_FOLDER_ID,
    GDRIVE_MODELS_FOLDER_ID,
    GDRIVE_MODELS_PROD_FOLDER_ID,
    GDRIVE_REPORTS_FOLDER_ID,
    OUTPUT_FOLDER_ID,
)
from infra.common.logger import logger
from infra.gdrive.service import GDriveService

__all__: list[str] = ["verify_gdrive_connectivity"]


def verify_gdrive_connectivity() -> bool:
    """
    Performs a deep diagnostic for Google Drive integration.
    Validates credentials, folder IDs, and write permissions.
    """
    logger.subsection("Starting GDrive Connectivity Diagnostics...")

    # 1. Path & Environment Pre-check
    if not CREDS_PATH_GDRIVE.exists():
        logger.error(f"GDrive Failure: Missing credentials file at {CREDS_PATH_GDRIVE}")
        return False

    try:
        service: GDriveService = GDriveService()
        logger.success("GDrive Service: Instantiated successfully.")

        # 2. Validate all critical folder IDs from config
        folder_ids_to_check: Final[dict[str, str | None]] = {
            "OUTPUT_FOLDER_ID": OUTPUT_FOLDER_ID,
            "GDRIVE_AILAB_FOLDER_ID": GDRIVE_AILAB_FOLDER_ID,
            "GDRIVE_DATA_FOLDER_ID": GDRIVE_DATA_FOLDER_ID,
            "GDRIVE_DATA_RAW_FOLDER_ID": GDRIVE_DATA_RAW_FOLDER_ID,
            "GDRIVE_DATA_PROCESSED_FOLDER_ID": GDRIVE_DATA_PROCESSED_FOLDER_ID,
            "GDRIVE_MODELS_FOLDER_ID": GDRIVE_MODELS_FOLDER_ID,
            "GDRIVE_MODELS_DEV_FOLDER_ID": GDRIVE_MODELS_DEV_FOLDER_ID,
            "GDRIVE_MODELS_PROD_FOLDER_ID": GDRIVE_MODELS_PROD_FOLDER_ID,
            "GDRIVE_REPORTS_FOLDER_ID": GDRIVE_REPORTS_FOLDER_ID,
        }

        for name, folder_id in folder_ids_to_check.items():
            if not folder_id:
                logger.warning(f"GDrive Config: Missing ID for {name}. Skipping check.")
                continue
            try:
                service.service.files().get(
                    fileId=folder_id, fields="id, name"
                ).execute()
                logger.success(f"GDrive Folder: Verified access to {name}.")
            except Exception:
                logger.error(
                    f"GDrive Folder: Failed to access {name} (ID: {folder_id})."
                )
                return False

        # 3. Validate Write Permissions
        if OUTPUT_FOLDER_ID:
            test_file_name = ".health_check.tmp"
            test_file_path = Path(test_file_name)
            try:
                test_file_path.write_text("health-check", encoding="utf-8")
                # Use '_' for unused variable to satisfy linter
                _ = service.upload_file(
                    test_file_path, OUTPUT_FOLDER_ID, overwrite=True
                )
                service.delete_specific_file(test_file_name, OUTPUT_FOLDER_ID)
                logger.success("GDrive Permissions: Write/Delete access verified.")
            finally:
                test_file_path.unlink(missing_ok=True)
        else:
            logger.warning(
                "GDrive Permissions: Skipping write check (OUTPUT_FOLDER_ID not set)."
            )

        return True

    except Exception as e:
        error_msg: str = str(e).lower()
        if any(key in error_msg for key in ["refresh_token", "invalid_grant"]):
            logger.error("GDrive Auth: Token invalid. Manual re-auth required.")
        elif any(key in error_msg for key in ["unreachable", "connection"]):
            logger.error("GDrive Network: API unreachable. Check internet connection.")
        else:
            logger.error(f"GDrive Unexpected Failure: {str(e)}")
        return False
