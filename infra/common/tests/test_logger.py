from pathlib import Path
from typing import Final
from unittest.mock import patch

import pytest

from infra.common.logger import Logger


@pytest.fixture
def temp_logger(tmp_path: Path) -> Logger:
    """Provides a clean Logger instance pointing to a temporary file."""
    # Patch mkdir to prevent creating real 'data/logs' during test init
    with patch("pathlib.Path.mkdir"):
        instance = Logger()

    # Override the log_file to a temporary location provided by pytest
    instance.log_file = tmp_path / "test_infrastructure.log"
    return instance


def test_logger_file_persistence(temp_logger: Logger) -> None:
    """Verifies if the logger successfully writes to a temporary persistent file."""
    test_message: Final[str] = "INTEGRATION_TEST_HEARTBEAT_001"

    # Action
    temp_logger.info(test_message)

    # Assert
    assert temp_logger.log_file.exists()
    with open(temp_logger.log_file, encoding="utf-8") as f:
        content: str = f.read()
        assert test_message in content
        assert "INFO" in content


def test_logger_ansi_stripping_in_file(temp_logger: Logger) -> None:
    """Ensures that ANSI color codes are NOT written to the log file."""
    test_message: Final[str] = "COLOR_TEST_MESSAGE"

    # success() uses GREEN in terminal
    temp_logger.success(test_message)

    with open(temp_logger.log_file, encoding="utf-8") as f:
        content: str = f.read()
        # The ANSI escape for green is \033[92m. We check it's not there.
        assert "\033[" not in content, "ANSI escape codes found in log file!"
        assert test_message in content


def test_logger_error_with_exception(temp_logger: Logger) -> None:
    """Validates that exceptions are correctly formatted in the log file."""
    msg: Final[str] = "Database failure"
    try:
        raise ValueError("Connection lost")
    except ValueError as e:
        temp_logger.error(msg, exception=e)

    with open(temp_logger.log_file, encoding="utf-8") as f:
        content: str = f.read()
        assert msg in content
        assert "Connection lost" in content
        assert "ERROR" in content
