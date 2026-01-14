# ruff: noqa: S101
from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

# Setup path for root access
sys.path.append(str(Path(__file__).parents[3]))

from infra.common.config import (
    CREDS_PATH_GDRIVE,
    DATA_DIR,
    OUTPUT_FOLDER_ID,
    PROCESSED_DIR,
    RAW_DIR,
    REPORTS_DIR,
)
from infra.common.logger import logger
from infra.gdrive.service import GDriveService


def run_health_check() -> None:
    """
    Infrastructure Health Check for ai-ops-hub.
    Validates Local I/O, mandatory paths from config, and GDrive connectivity.
    """
    logger.info(">>> [HEALTH-CHECK] Starting Infrastructure Validation...")

    logger.info("Step 1: Validating Local Path Integrity...")
    mandatory_dirs: Final[list[Path]] = [DATA_DIR, RAW_DIR, PROCESSED_DIR, REPORTS_DIR]

    for directory in mandatory_dirs:
        test_file: Final[Path] = directory / ".health_check_test"
        try:
            directory.mkdir(parents=True, exist_ok=True)

            test_file.write_text("health_check_ping", encoding="utf-8")
            test_file.unlink()
            logger.success(
                f" - Local I/O Verified: {directory.relative_to(directory.parents[1])}"
            )
        except Exception as e:
            logger.error(f" - I/O Failure at {directory}: {e}")
            sys.exit(1)

    if not CREDS_PATH_GDRIVE.exists():
        logger.error(
            f" - Critical Failure: Credentials not found at {CREDS_PATH_GDRIVE}"
        )
        sys.exit(1)
    logger.success(" - GDrive Credentials File: Found.")

    logger.info("Step 2: Validating Google Drive Connection...")
    if not OUTPUT_FOLDER_ID:
        logger.warning(" - OUTPUT_FOLDER_ID missing. Skipping Remote Check.")
        return

    try:
        gdrive: Final[GDriveService] = GDriveService()
        files = gdrive.list_files(limit=5)

        logger.success(" - GDrive Connection: OK (OAuth Handshake Verified)")
        logger.info(f" - Found {len(files)} files in Target Folder.")

        for f in files:
            logger.info(f"   · {f['name']} ({f['id']})")

    except Exception as e:
        logger.error(f" - GDrive Access Failed: {e}")
        logger.warning(
            "Hint: If it's a 'Non-interactive' error, run this script manually in a terminal."
        )
        sys.exit(1)

    logger.success(">>> [HEALTH-CHECK] All systems operational!️")


if __name__ == "__main__":
    run_health_check()
