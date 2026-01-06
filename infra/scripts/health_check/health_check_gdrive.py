import os
from pathlib import Path

from infra.common.logger import logger
from infra.gdrive import GDriveService

__all__: list[str] = ["verify_gdrive_connectivity"]


def verify_gdrive_connectivity() -> bool:
    """
    Performs a deep diagnostic for Google Drive integration.
    Validates credentials existence, token validity, and API reachability.
    """
    logger.subsection("Starting GDrive Connectivity Diagnostics...")

    # 1. Path & Environment Pre-check
    # We use the service's own root resolution logic to find credentials
    root: Path = Path(__file__).parent.parent.parent.parent
    creds_path: str = os.getenv(
        "GDRIVE_CREDENTIALS_PATH", str(root / "data" / "credentials.json")
    )

    if not os.path.exists(creds_path):
        logger.error(f"GDrive Failure: Missing credentials file at {creds_path}")
        return False

    try:
        # 2. Service Instantiation
        # This will trigger the auth flow and token refresh if necessary
        service: GDriveService = GDriveService()

        # 3. API Communication Test
        # Minimal 'list' operation to verify the token/auth flow
        files: list[dict[str, str]] = service.list_files(limit=1)

        logger.success(
            f"GDrive Service: Connection verified. Accessible items: {len(files)}"
        )
        return True

    except Exception as e:
        error_msg: str = str(e).lower()

        # 4. Intelligent Error Categorization (Rigor Protocol)
        if "refresh_token" in error_msg or "invalid_grant" in error_msg:
            logger.error(
                "GDrive Auth: Token expired or invalid. Manual re-auth required."
            )
        elif "unreachable" in error_msg or "connection" in error_msg:
            logger.error(
                "GDrive Network: API unreachable. Check internet connection or proxy."
            )
        elif "insufficient permissions" in error_msg:
            logger.error(
                "GDrive Scopes: Token lacks required permissions for this operation."
            )
        else:
            logger.error(f"GDrive Unexpected Failure: {str(e)}")

        return False
