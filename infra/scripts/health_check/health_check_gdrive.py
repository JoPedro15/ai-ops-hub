from config import CREDS_PATH_GDRIVE
from infra.common.logger import logger
from infra.gdrive.service import GDriveService

__all__: list[str] = ["verify_gdrive_connectivity"]


def verify_gdrive_connectivity() -> bool:
    """
    Performs a deep diagnostic for Google Drive integration.
    Uses centralized configuration paths for robustness.
    """
    logger.subsection("Starting GDrive Connectivity Diagnostics...")

    # 1. Path & Environment Pre-check
    if not CREDS_PATH_GDRIVE.exists():
        logger.error(f"GDrive Failure: Missing credentials file at {CREDS_PATH_GDRIVE}")
        return False

    try:
        # 2. Service Instantiation & 3. API Test
        service: GDriveService = GDriveService()
        files: list[dict[str, str]] = service.list_files(limit=1)

        logger.success(
            f"GDrive Service: Connection verified. Accessible items: {len(files)}"
        )
        return True

    except Exception as e:
        error_msg: str = str(e).lower()

        # 4. Intelligent Error Categorization (Rigor Protocol)
        if any(key in error_msg for key in ["refresh_token", "invalid_grant"]):
            logger.error("GDrive Auth: Token invalid. Manual re-auth required.")

        elif any(key in error_msg for key in ["unreachable", "connection"]):
            logger.error("GDrive Network: API unreachable. Check internet connection.")
        elif "insufficient permissions" in error_msg:
            logger.error("GDrive Scopes: Token lacks required permissions.")
        else:
            logger.error(f"GDrive Unexpected Failure: {str(e)}")

        return False
