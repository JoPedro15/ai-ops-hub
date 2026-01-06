from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd

from infra.common.logger import logger
from infra.gdrive.service import GDriveService

__all__: list[str] = ["DataIngestor"]


class DataIngestor:
    """
    Service class to handle data acquisition and local caching logic.
    Ensures data integrity before loading into the processing pipeline.
    """

    def __init__(self, gdrive_service: GDriveService | None = None) -> None:
        """
        Initializes the ingestor with an optional injected GDriveService.

        Args:
            gdrive_service: Shared GDrive session. Creates a new one if None.
        """
        self.gdrive: GDriveService = gdrive_service or GDriveService()

    def get_spreadsheet_data(
        self,
        local_file_path: str | Path,
        file_id: str,
        min_file_size: int = 500,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Retrieves spreadsheet data from local cache or GDrive.
        Handles both modern (.xlsx) and legacy (.xls) Excel formats.

        Args:
            local_file_path: Destination path on local disk.
            file_id: Google Drive unique ID.
            min_file_size: Byte threshold to detect corrupted/empty downloads.
            force_download: If True, bypasses local cache.

        Returns:
            pd.DataFrame: Loaded dataset.
        """
        # Convert to Path object for modern filesystem manipulation
        path: Final[Path] = Path(local_file_path)

        file_exists: bool = path.exists()
        is_invalid: bool = False

        # 1. Integrity Check: Verify if file size meets the minimum threshold
        if file_exists:
            is_invalid = path.stat().st_size < min_file_size

        # 2. Cache Management: Remove file if corrupted or download is forced
        if is_invalid or force_download:
            reason: str = "Corrupted" if is_invalid else "Force download"
            logger.warning(f"Invalidating cache ({reason}): {path.name}")
            path.unlink(missing_ok=True)
            file_exists = False

        # 3. Data Acquisition: Fetch from Google Drive if not available locally
        if not file_exists:
            logger.info(f"Ingesting resource from GDrive ID: {file_id}")
            # Ensure the directory structure (e.g., data/raw) exists
            path.parent.mkdir(parents=True, exist_ok=True)
            self.gdrive.download_file(file_id=file_id, local_path=str(path))
        else:
            logger.info(f"Cache hit: Using local version {path.name}")

        # 4. Smart Data Loading: Detect engine based on file extension
        # .xls requires 'xlrd' while .xlsx requires 'openpyxl'
        engine: str = "xlrd" if path.suffix == ".xls" else "openpyxl"

        try:
            return pd.read_excel(path, engine=engine)
        except Exception as e:
            logger.error(f"Critical failure loading Excel file {path.name}: {e}")
            raise
