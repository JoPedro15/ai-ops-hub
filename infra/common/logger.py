from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Final


class Logger:
    """
    Standardized ANSI-colored logger for automation pipelines.
    Provides clean, professional terminal output without icons or emojis.
    Integrated with local file persistence for CI/CD audit trails.
    """

    # ANSI Escape Sequences for Terminal Formatting
    _HEADER: Final[str] = "\033[95m"
    _BLUE: Final[str] = "\033[94m"
    _GREEN: Final[str] = "\033[92m"
    _WARNING: Final[str] = "\033[93m"
    _FAIL: Final[str] = "\033[91m"
    _ENDC: Final[str] = "\033[0m"
    _BOLD: Final[str] = "\033[1m"

    def __init__(self) -> None:
        """
        Initializes the logger instance.
        Dynamically resolves project root to avoid circular dependencies with config.
        """
        # Resolve project root relative to: infra/common/logger.py -> ../../../
        self.project_root: Path = Path(__file__).resolve().parents[2]
        self.log_file: Path = self.project_root / "data" / "logs" / "infrastructure.log"

        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Fallback for read-only environments or permission issues
            msg = (
                f"{self._WARNING}WARNING: Could not create log file at "
                f"{self.log_file}{self._ENDC}"
            )
            print(msg, file=sys.stderr)

    @staticmethod
    def _get_timestamp() -> str:
        """Returns current timestamp in YYYY-MM-DD HH:MM:SS format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _write_to_file(self, level: str, message: str) -> None:
        """
        Internal helper to persist log entries to disk.
        Strips ANSI colors to keep the plain text log file readable.
        """
        ts: str = self._get_timestamp()
        entry: str = f"[{ts}] {level.upper()}: {message}\n"

        try:
            # Using append mode to maintain history during the execution session
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:  # noqa: S110
            # Silently fail file logging to prevent crashing the main automation
            pass

    def info(self, message: str) -> None:
        """Standard informational message."""
        self._write_to_file("INFO", message)
        print(f"[{self._get_timestamp()}] INFO: {message}")

    def success(self, message: str) -> None:
        """Success message highlighted in green."""
        self._write_to_file("SUCCESS", message)
        print(f"[{self._get_timestamp()}] {self._GREEN}SUCCESS:{self._ENDC} {message}")

    def warning(self, message: str) -> None:
        """Warning alert highlighted in yellow."""
        self._write_to_file("WARNING", message)
        print(
            f"[{self._get_timestamp()}] {self._WARNING}WARNING:{self._ENDC} {message}"
        )

    def error(self, message: str, exception: Exception | None = None) -> None:
        """
        Error message in red to stderr.
        Optionally logs the exception details for debugging.
        """
        error_msg: str = f"{message} | Error: {exception}" if exception else message
        self._write_to_file("ERROR", error_msg)
        print(
            f"[{self._get_timestamp()}] {self._FAIL}ERROR:{self._ENDC} {error_msg}",
            file=sys.stderr,
        )

    def section(self, title: str) -> None:
        """Major structural header for the log output."""
        self._write_to_file("SECTION", f"--- {title.upper()} ---")
        print(
            f"\n[{self._get_timestamp()}] "
            f"{self._BOLD}{self._HEADER}{title.upper()}{self._ENDC}"
        )

    def subsection(self, message: str) -> None:
        """Bold informational message to distinguish sub-tasks within a section."""
        self._write_to_file("SUBSECTION", message)
        print(f"[{self._get_timestamp()}] {self._BOLD}INFO: {message}{self._ENDC}")

    def print(self, message: str, color: str | None = None) -> None:
        """
        Direct replacement for the built-in print command.
        Bypasses timestamp and prefixes for raw data output.
        """
        self._write_to_file("PRINT", message)
        c: str = color if color else ""
        end: str = self._ENDC if color else ""
        print(f"{c}{message}{end}")


# Global instance for project-wide use
logger: Logger = Logger()
