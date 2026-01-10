from pathlib import Path
from typing import Final
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from infra.ai_utils import DataIngestor
from infra.gdrive.service import GDriveService

__all__: list[str] = []  # Tests don't need to export anything


@pytest.fixture
def mock_gdrive() -> MagicMock:
    """Provides a mocked GDriveService to avoid real API calls."""
    return MagicMock(spec=GDriveService)


@pytest.fixture
def ingestor(mock_gdrive: MagicMock) -> DataIngestor:
    """Initializes DataIngestor with a mocked service."""
    return DataIngestor(gdrive_service=mock_gdrive)


def test_get_spreadsheet_data_cache_hit(ingestor: DataIngestor, tmp_path: Path) -> None:
    """
    Validates that if a valid file exists locally, GDrive is NOT called.
    """
    # 1. Setup: Create a dummy excel file (size > 10 bytes)
    test_file: Final[Path] = tmp_path / "data.xlsx"
    df_original: Final[pd.DataFrame] = pd.DataFrame({"col1": [1, 2]})

    # Ensuring file size is sufficient for the default min_file_size
    df_original.to_excel(test_file, index=False)

    # 2. Action: Call ingestor
    # Mocking read_excel to avoid dependency on excel engines during this unit test
    with patch("pandas.read_excel", return_value=df_original) as mock_read:
        df_result: pd.DataFrame = ingestor.get_spreadsheet_data(
            local_file_path=test_file,
            file_id="dummy_id",
            min_file_size=10,
        )

    # 3. Assert: GDrive download should NOT have been called, but pandas must read
    ingestor.gdrive.download_file.assert_not_called()
    mock_read.assert_called_once()
    assert len(df_result) == 2


def test_get_spreadsheet_data_force_download(
    ingestor: DataIngestor, tmp_path: Path
) -> None:
    """
    Ensures that force_download=True invalidates existing valid cache.
    """
    test_file: Final[Path] = tmp_path / "data.xlsx"
    test_file.write_text("enough content to be valid")

    with patch("pandas.read_excel", return_value=pd.DataFrame()):
        ingestor.get_spreadsheet_data(
            local_file_path=test_file, file_id="id_123", force_download=True
        )

    # Assert: Download was called even though file existed
    ingestor.gdrive.download_file.assert_called_once()


def test_get_spreadsheet_data_creates_directories(
    ingestor: DataIngestor, tmp_path: Path
) -> None:
    """
    Verifies that missing parent directories are created before download.
    """
    # Deep nested path that doesn't exist
    nested_path: Final[Path] = tmp_path / "new_folder" / "sub" / "file.xlsx"

    with patch("pandas.read_excel", return_value=pd.DataFrame()):
        ingestor.get_spreadsheet_data(local_file_path=nested_path, file_id="id_123")

    assert nested_path.parent.exists()
    ingestor.gdrive.download_file.assert_called_once()


def test_get_spreadsheet_data_engine_selection(
    ingestor: DataIngestor, tmp_path: Path
) -> None:
    """
    Checks if the correct pandas engine is selected based on file extension.
    """
    xlsx_file: Final[Path] = tmp_path / "test.xlsx"
    xls_file: Final[Path] = tmp_path / "test.xls"

    # Create dummy files
    xlsx_file.write_text("dummy content")
    xls_file.write_text("dummy content")

    with patch("pandas.read_excel") as mock_read:
        ingestor.get_spreadsheet_data(xlsx_file, "id1", min_file_size=0)
        assert mock_read.call_args[1]["engine"] == "openpyxl"

        ingestor.get_spreadsheet_data(xls_file, "id2", min_file_size=0)
        assert mock_read.call_args[1]["engine"] == "openpyxl"
