import tempfile
from pathlib import Path

import pandas as pd

from infra.ai_utils import DataIngestor
from infra.common.logger import logger

__all__: list[str] = ["verify_data_ingestor"]


def verify_data_ingestor() -> bool:
    """
    Validates the Data Ingestor's core functionality: reading different file formats.
    Checks for required engine dependencies and performs in-memory read tests.
    """
    logger.subsection("Checking Data Ingestor Engines...")
    all_ok = True

    # 1. Verify Engine Dependencies
    try:
        import openpyxl  # noqa: F401

        logger.success("Engine Check: 'openpyxl' for .xlsx is available.")
    except ImportError:
        logger.error("Engine Missing: 'openpyxl' is required for .xlsx files.")
        all_ok = False

    try:
        import xlrd  # noqa: F401

        logger.success("Engine Check: 'xlrd' for .xls is available.")
    except ImportError:
        logger.error("Engine Missing: 'xlrd' is required for legacy .xls files.")
        all_ok = False

    try:
        import pyarrow  # noqa: F401

        logger.success("Engine Check: 'pyarrow' for .parquet is available.")
    except ImportError:
        logger.warning("Engine Missing: 'pyarrow' is needed for .parquet files.")
        # Not marking as a failure as it's less common, but warning is important.

    if not all_ok:
        return False

    # 2. Perform In-Memory Read Tests
    ingestor = DataIngestor(gdrive_service=None)  # Test in local-only mode
    sample_df = pd.DataFrame({"col1": [1, 2], "col2": ["A", "B"]})

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)

        # Test files to create and read
        # Note: We do not test .xls creation as xlwt is deprecated/legacy.
        # We only verify that the xlrd reader engine is present above.
        test_files = {
            "test.csv": lambda df, p: df.to_csv(p, index=False),
            "test.xlsx": lambda df, p: df.to_excel(p, index=False, engine="openpyxl"),
        }

        for filename, writer in test_files.items():
            file_path = temp_path / filename
            try:
                writer(sample_df, file_path)
                # Use the ingestor to read the data back
                # We pass min_file_size=0 to accept small test files
                read_df = ingestor.get_data(
                    file_path, file_id="dummy_id", min_file_size=0
                )

                if not read_df.equals(sample_df):
                    logger.error(f"Integrity Fail: Data mismatch for {filename}.")
                    all_ok = False
                else:
                    logger.success(f"Format Check: Successfully read '{filename}'.")
            except Exception as e:
                logger.error(f"Format Check Fail: Cannot process '{filename}': {e}")
                all_ok = False

    if all_ok:
        logger.success("Data Ingestor: All formats and engines are operational.")

    return all_ok
