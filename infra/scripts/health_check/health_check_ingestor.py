import os
from pathlib import Path

import openpyxl
import pandas as pd

from infra.ai_utils import DataIngestor
from infra.common import logger

__all__: list[str] = ["verify_data_ingestor"]


def verify_data_ingestor() -> bool:
    """
    Validates the Data Ingestor infrastructure.
    Checks: Dependencies, Path Integrity, and Cache Directory Permissions.
    """
    try:
        logger.subsection("Checking Data Ingestor Dependencies...")

        # 1. Dependency Smoke Test
        # Checking versions to ensure packages are correctly linked in the .venv
        _pandas_v: str = pd.__version__
        _engine_v: str = openpyxl.__version__

        # 2. Path & Credentials Validation
        # SSoT: Uses environment variable with default fallback
        creds_path: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "data/credentials.json")
        if not os.path.exists(creds_path):
            logger.warning(f"Ingestor Warning: Credentials not found at {creds_path}")
            # We don't return False here because the ingestor might
            # still work with local cache only, but we warn the user.

        # 3. Cache Write Permission Test
        # This is a critical 'Movement Standard' for the Ingestor
        root: Path = Path(__file__).parent.parent.parent.parent
        cache_dir: Path = root / "data" / "cache"

        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            test_file: Path = cache_dir / ".ingestor_write_test"
            test_file.write_text(f"io_check_via_{_engine_v}")
            test_file.unlink()
            logger.success("Cache Directory: IO verified (Write/Delete).")
        except Exception as e:
            logger.error(f"Cache IO Failure: {str(e)}")
            return False

        # 4. Service Instantiation Smoke Test
        # Testing the factory logic and GDrive integration
        ingestor: DataIngestor = DataIngestor()

        if ingestor.gdrive is None:
            logger.error(
                "Ingestor Failure: Service initialized with null GDrive engine."
            )
            return False

        logger.success("Data Ingestor: Ready for ingestion.")
        return True

    except Exception as e:
        logger.error(f"Data Ingestor Health Failure: {str(e)}")
        return False
