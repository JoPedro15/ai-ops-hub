from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[3]))

from infra.common.logger import logger
from infra.gdrive.service import GDriveService

if __name__ == "__main__":
    try:
        logger.info(">>> Starting Google Drive OAuth Validation...")

        gdrive = GDriveService()
        files = gdrive.list_files(limit=5)

        logger.success(f"Connected! Found {len(files)} files.")
        for f in files:
            logger.info(f" - {f['name']} ({f['id']})")

    except Exception as e:
        logger.error(f"Failed to authenticate or list files: {e}")
