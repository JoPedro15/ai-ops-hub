from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Final

from config import DATA_DIR

LOG_FILE: Path = DATA_DIR / "logs" / "infrastructure.log"


class Logger:
    """
    Standardized ANSI-colored logger for automation pipelines.
    Provides clean, professional terminal output without icons or emojis.
    """

    _HEADER: Final[str] = "\033[95m"
    _BLUE: Final[str] = "\033[94m"
    _GREEN: Final[str] = "\033[92m"
    _WARNING: Final[str] = "\033[93m"
    _FAIL: Final[str] = "\033[91m"
    _ENDC: Final[str] = "\033[0m"
    _BOLD: Final[str] = "\033[1m"

    def __init__(self) -> None:
        """Initializes the logger and ensures the log directory exists."""
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            # Fallback for environments with restricted write permissions
            print(f"WARNING: Could not create log directory: {e}")

    @staticmethod
    def _get_timestamp() -> str:
        """Returns current timestamp in YYYY-MM-DD HH:MM:SS format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _write_to_file(self, level: str, message: str) -> None:
        """Writes a plain-text entry to the log file (no ANSI colors)."""
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{self._get_timestamp()}] {level.upper()}: {message}\n")
        except Exception:  # noqa: S110
            # Silently fail file logging to avoid crashing the main process
            pass

    def info(self, message: str) -> None:
        """Prints an information message."""
        print(f"[{self._get_timestamp()}] INFO: {message}")

    def success(self, message: str) -> None:
        """Prints a success message in green."""
        print(f"[{self._get_timestamp()}] {self._GREEN}SUCCESS:{self._ENDC} {message}")

    def warning(self, message: str) -> None:
        """Prints a warning message in yellow."""
        print(
            f"[{self._get_timestamp()}] {self._WARNING}WARNING:{self._ENDC} {message}"
        )

    def error(self, message: str) -> None:
        """Prints an error message in red to stderr."""
        print(
            f"[{self._get_timestamp()}] {self._FAIL}ERROR:{self._ENDC} {message}",
            file=sys.stderr,
        )

    def section(self, title: str) -> None:
        """Prints a bold header section."""
        print(
            f"\n[{self._get_timestamp()}] "
            f"{self._BOLD}{self._HEADER}{title.upper()}{self._ENDC}"
        )

    def print(self, message: str, color: str | None = None) -> None:
        """
        Raw print replacement. No timestamp, no prefix.
        Optional ANSI color.
        """
        c: str = color if color else ""
        end: str = self._ENDC if color else ""
        print(f"{c}{message}{end}")


# Global instance for project-wide use
logger: Logger = Logger()
