import os

import pandas as pd

# Standard absolute imports from our new infra structure
from infra.common import logger
from infra.gdrive import GDriveService

__all__: list[str] = ["DataIngestor"]


class DataIngestor:
    """
    Service class to handle data acquisition and local caching logic.
    Ensures data integrity before loading into the processing pipeline.
    """

    def __init__(self, gdrive_service: GDriveService | None = None) -> None:
        """
        Initializes the ingestor.
        Injects a GDriveService to reuse authentication sessions.

        Args:
            gdrive_service: An instance of GDriveService.
            If None, a new one will be created using env fallbacks.
        """
        if gdrive_service:
            self.gdrive: GDriveService = gdrive_service
        else:
            # SSoT: Path resolution via environment or project default
            self.gdrive = GDriveService()

    def get_spreadsheet_data(
        self,
        local_file_path: str,
        file_id: str,
        min_file_size: int = 500,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Retrieves spreadsheet data from a local cache or downloads it from GDrive.
        Automatically handles Google Sheets to Excel export conversion.

        Args:
            local_file_path: Target path on the local filesystem.
            file_id: Unique Google Drive file identifier.
            min_file_size: Minimum threshold in bytes to consider a file valid.
            force_download: If True, invalidates cache and triggers a new download.

        Returns:
            pd.DataFrame: The loaded dataset ready for processing.
        """
        file_exists: bool = os.path.exists(local_file_path)
        is_corrupted: bool = False

        # 1. Evaluate existing file health
        if file_exists:
            file_size: int = os.path.getsize(local_file_path)
            is_corrupted = file_size < min_file_size

        # 2. Handle Cache Invalidation
        if is_corrupted or force_download:
            reason: str = "File corrupted" if is_corrupted else "Force download"
            logger.warning(f"Cache Invalidation ({reason}): removing {local_file_path}")

            if os.path.exists(local_file_path):
                os.remove(local_file_path)
            file_exists = False

        # 3. Data Acquisition Phase
        if not file_exists:
            logger.info(
                "Resource missing or invalidated. "
                f"Ingesting from GDrive (ID: {file_id})..."
            )
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            self.gdrive.download_file(file_id=file_id, local_path=local_file_path)
        else:
            logger.info(f"File found: using cached version at {local_file_path}")

        # 4. Data Loading
        # Using 'openpyxl' engine for modern .xlsx compatibility
        return pd.read_excel(local_file_path, engine="openpyxl")
