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
        # 1. Path Normalization: Ensure absolute path for reliability in CI
        path: Final[Path] = Path(local_file_path).resolve()
        file_exists: bool = path.exists()

        # 2. Integrity Check: Verify if file size meets the minimum threshold
        is_invalid: bool = False
        if file_exists:
            # stat().st_size can be 0 if a download was interrupted
            is_invalid = path.stat().st_size < min_file_size

        # 3. Cache Management: Remove file if corrupted or download is forced
        if is_invalid or force_download:
            reason: str = "Corrupted" if is_invalid else "Force Download"
            logger.warning(f"Invalidating cache for '{path.name}'. Reason: {reason}")
            path.unlink(missing_ok=True)
            file_exists = False

        # 4. Data Acquisition: Fetch from Google Drive if not available locally
        if not file_exists:
            logger.info(f"Ingesting resource from GDrive ID: {file_id}")
            # Ensure the directory structure (e.g., data/raw) exists
            path.parent.mkdir(parents=True, exist_ok=True)
            self.gdrive.download_file(file_id=file_id, local_path=str(path))
        else:
            logger.info(f"Cache hit: Using local version {path.name}")

        # 5. Smart Data Loading: Engine selection & Validation
        # .xls (Legacy) -> 'xlrd' | .xlsx (Modern) -> 'openpyxl'
        engine: Final[str] = "xlrd" if path.suffix == ".xls" else "openpyxl"

        try:
            return pd.read_excel(path, engine=engine)
        except ImportError:
            # Critical check for CI environment dependencies
            logger.error(f"Missing required engine '{engine}' for {path.suffix} files.")
            raise
        except Exception as e:
            logger.error(f"Critical failure loading Excel file {path.name}: {e}")
            raise

    def __repr__(self) -> str:
        """String representation for easier debugging in logs."""
        return f"<DataIngestor(gdrive={self.gdrive.__class__.__name__})>"
