import logging
import sys
from pathlib import Path
from typing import Final

# 1. Path Setup (Ensure monorepo visibility)
ROOT_PATH: Final[Path] = Path(__file__).resolve().parent.parent.parent
if str(ROOT_PATH) not in sys.path:
    sys.path.append(str(ROOT_PATH))

# 2. Bootstrap Logger Setup
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout
)
logger: logging.Logger = logging.getLogger(__name__)


def verify_infrastructure_paths() -> None:
    # Local imports to satisfy Ruff F401
    from config import CRED_DIR_GDRIVE, CREDS_PATH_GDRIVE, RAW_DIR

    logger.info("Checking physical infrastructure paths...")
    essential_assets: list[tuple[Path, str, bool]] = [
        (CRED_DIR_GDRIVE, "GDrive Credentials Folder", True),
        (CREDS_PATH_GDRIVE, "GDrive JSON Key", True),
        (RAW_DIR, "Local Raw Data Storage", True),
    ]

    for path, description, critical in essential_assets:
        if not path.exists():
            msg: str = f"Missing {description} at {path}"
            if critical:
                logger.error(f"CRITICAL FAILURE: {msg}")
                sys.exit(1)
            logger.warning(f"ADVISORY: {msg}")
        else:
            logger.info(f"Verified: {description}")


def verify_environment_variables() -> None:
    # Local imports to verify .env loading via config.py
    from config import (
        CAR_DATA_FILE_ID,
        GDRIVE_DATA_PROCESSED_FOLDER_ID,
        GDRIVE_DATA_RAW_FOLDER_ID,
        OUTPUT_FOLDER_ID,
    )

    logger.info("Checking critical environment variables (.env)...")
    critical_vars: dict[str, str | None] = {
        "OUTPUT_FOLDER_ID": OUTPUT_FOLDER_ID,
        "GDRIVE_DATA_RAW_FOLDER_ID": GDRIVE_DATA_RAW_FOLDER_ID,
        "GDRIVE_DATA_PROCESSED_FOLDER_ID": GDRIVE_DATA_PROCESSED_FOLDER_ID,
        "CAR_DATA_FILE_ID": CAR_DATA_FILE_ID,
    }

    missing_vars: list[str] = [name for name, val in critical_vars.items() if not val]

    if missing_vars:
        logger.error(
            "Environment Breach: Missing variables in .env -> "
            f"{', '.join(missing_vars)}"
        )
        sys.exit(1)
    logger.info("All critical environment variables are loaded.")


def verify_modules() -> None:
    logger.info("Checking module import integrity...")
    modules_to_test: Final[list[str]] = [
        "pandas",
        "infra.common.logger",
        "infra.gdrive.service",
    ]

    for module_name in modules_to_test:
        try:
            __import__(module_name)
            logger.info(f"Module Verified: {module_name}")
        except ImportError as e:
            logger.error(f"Import Integrity Failed: {module_name} -> {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    logger.info(">>> Starting Full Infrastructure Integrity Check")
    verify_infrastructure_paths()
    verify_environment_variables()
    verify_modules()
    logger.info("✅ System integrity confirmed. Ready for execution.")
    sys.exit(0)
