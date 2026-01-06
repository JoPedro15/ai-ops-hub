import logging
import sys
from pathlib import Path
from typing import Final

# Ensure the project root is in the python path for CI/CD consistency
ROOT_PATH: Final[str] = str(Path(__file__).parent.parent.parent)
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

# Configure logging to avoid using print() as per project guidelines
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger: logging.Logger = logging.getLogger(__name__)


def verify_modules() -> None:
    """
    Verify if core infrastructure modules are importable and paths resolve.

    This acts as a pre-flight check for the automation hub.
    """
    # testing 'config' is crucial to detect the circular imports we fixed
    modules_to_test: Final[list[str]] = [
        "config",
        "pandas",
        "infra.common.logger",
        "infra.gdrive.service",
    ]

    try:
        for module_name in modules_to_test:
            # Dynamically import the module to verify integrity
            __import__(module_name)
            logger.info(f"Successfully imported {module_name}")

    except (ImportError, AttributeError) as e:
        # AttributeError is caught here because circular imports often
        # manifest as 'module X has no attribute Y' during partial init.
        logger.error(f"Integrity Check Failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during integrity check: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    verify_modules()
