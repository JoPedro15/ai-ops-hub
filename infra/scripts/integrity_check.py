# infra/scripts/integrity_check.py
import logging
import sys
from typing import Final

# Configure logging to avoid using print()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger: logging.Logger = logging.getLogger(__name__)


def verify_modules() -> None:
    """
    Verify if core infrastructure modules are importable.

    Raises:
        ImportError: If a mandatory module cannot be loaded.
    """
    modules_to_test: Final[list[str]] = [
        "pandas",
        "infra.gdrive.service",
        "infra.common.logger",
    ]

    try:
        for module_name in modules_to_test:
            __import__(module_name)
            logger.info(f"Successfully imported {module_name}")
    except ImportError as e:
        logger.error(f"Integrity Check Failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    verify_modules()
