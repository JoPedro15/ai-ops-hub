from pathlib import Path
from typing import Final
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from infra.ai_utils import DataIngestor
from infra.gdrive.service import GDriveService

__all__: list[str] = []


@pytest.fixture
def mock_gdrive() -> MagicMock:
    """Provides a mocked GDriveService to avoid real API calls."""
    return MagicMock(spec=GDriveService)


@pytest.fixture
def ingestor(mock_gdrive: MagicMock) -> DataIngestor:
    """Initializes DataIngestor with a mocked service."""
    return DataIngestor(gdrive_service=mock_gdrive)


def test_get_data_cache_hit(ingestor: DataIngestor, tmp_path: Path) -> None:
    """
    Validates that if a valid file exists locally, GDrive is NOT called.
    """
    # 1. Setup: Create a dummy excel file
    test_file: Final[Path] = tmp_path / "data.xlsx"
    df_original: Final[pd.DataFrame] = pd.DataFrame({"col1": [1, 2]})

    # We actually write a valid excel file so pandas can read it if not mocked
    # But here we mock read_excel to isolate logic
    test_file.touch()  # Create empty file but we will mock size check if needed

    # Mock stat().st_size to be > min_file_size (default 500)
    with patch.object(Path, "stat") as mock_stat:
        mock_stat.return_value.st_size = 1000

        with patch("pandas.read_excel", return_value=df_original) as mock_read:
            df_result: pd.DataFrame = ingestor.get_data(
                local_file_path=test_file,
                file_id="dummy_id",
            )

    # 3. Assert
    ingestor.gdrive.download_file.assert_not_called()
    mock_read.assert_called_once()
    assert len(df_result) == 2


def test_get_data_force_download(ingestor: DataIngestor, tmp_path: Path) -> None:
    """
    Ensures that force_download=True invalidates existing valid cache.
    """
    test_file: Final[Path] = tmp_path / "data.xlsx"
    test_file.write_text("dummy content")  # File exists

    with patch("pandas.read_excel", return_value=pd.DataFrame()):
        ingestor.get_data(
            local_file_path=test_file, file_id="id_123", force_download=True
        )

    # Assert: Download was called even though file existed
    ingestor.gdrive.download_file.assert_called_once()


def test_get_data_engine_selection(ingestor: DataIngestor, tmp_path: Path) -> None:
    """
    Checks if the correct pandas engine is selected based on file extension.
    """
    xlsx_file: Final[Path] = tmp_path / "test.xlsx"
    xls_file: Final[Path] = tmp_path / "test.xls"
    csv_file: Final[Path] = tmp_path / "test.csv"

    # Create dummy files so exists() returns True
    for f in [xlsx_file, xls_file, csv_file]:
        f.touch()

    # Mock size to avoid "corrupted" check
    with patch.object(Path, "stat") as mock_stat:
        mock_stat.return_value.st_size = 1000

        # Test XLSX -> openpyxl
        with patch("pandas.read_excel") as mock_read_excel:
            ingestor.get_data(xlsx_file, "id1")
            assert mock_read_excel.call_args[1]["engine"] == "openpyxl"

        # Test XLS -> xlrd
        with patch("pandas.read_excel") as mock_read_excel:
            ingestor.get_data(xls_file, "id2")
            assert mock_read_excel.call_args[1]["engine"] == "xlrd"

        # Test CSV -> read_csv
        with patch("pandas.read_csv") as mock_read_csv:
            ingestor.get_data(csv_file, "id3")
            mock_read_csv.assert_called_once()
