from __future__ import annotations

import sys
from datetime import datetime
from typing import Final


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

    @staticmethod
    def _get_timestamp() -> str:
        """Returns current timestamp in YYYY-MM-DD HH:MM:SS format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
