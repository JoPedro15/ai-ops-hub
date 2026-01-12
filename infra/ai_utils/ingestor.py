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

    def get_data(
        self,
        local_file_path: str | Path,
        file_id: str,
        min_file_size: int = 500,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Retrieves dataset from local cache or GDrive.
        Handles .csv, .xlsx (Modern Excel), and .xls (Legacy Excel).

        Args:
            local_file_path: Destination path on local disk.
            file_id: Google Drive unique ID.
            min_file_size: Byte threshold to detect corrupted/empty downloads.
            force_download: If True, bypasses local cache.

        Returns:
            pd.DataFrame: Loaded dataset.

        Raises:
            ValueError: If the file format is not supported.
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

        # 5. Smart Data Loading: Engine selection based on extension
        suffix: str = path.suffix.lower()

        try:
            if suffix == ".csv":
                return pd.read_csv(path)

            if suffix == ".xls":
                return pd.read_excel(path, engine="xlrd")

            if suffix == ".xlsx":
                return pd.read_excel(path, engine="openpyxl")

            # Fallback for other formats supported by pandas (e.g. .parquet, .json)
            # or if the user didn't provide an extension but the content is valid.
            logger.warning(
                f"Extension '{suffix}' not explicitly handled. Attempting default load."
            )
            if suffix in [".parquet"]:
                return pd.read_parquet(path)

            # Default fallback to Excel reader as it's the most common use case here
            return pd.read_excel(path)

        except ImportError as e:
            logger.error(f"Missing dependency for '{suffix}' files: {e}")
            raise
        except Exception as e:
            logger.error(f"Critical failure loading file {path.name}: {e}")
            raise

    # Alias for backward compatibility if needed, though refactoring is preferred
    get_spreadsheet_data = get_data

    def __repr__(self) -> str:
        """String representation for easier debugging in logs."""
        return f"<DataIngestor(gdrive={self.gdrive.__class__.__name__})>"
