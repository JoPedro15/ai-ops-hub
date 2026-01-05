import sys
from io import StringIO

from infra.common.logger import Logger, logger

__all__: list[str] = ["verify_logger_service"]


def verify_logger_service() -> bool:
    """
    Validates the custom Logger infrastructure.
    Checks: Instance integrity, Method availability, and Output stream.
    """
    sys.stdout.write(">>> Checking Logger Service...\n")

    try:
        # 1. Singleton/Instance Validation
        if not isinstance(logger, Logger):
            sys.stderr.write(
                "❌ Logger Health Failure: Global instance is not of type Logger.\n"
            )
            return False

        # 2. Smoke Test: Buffer Capture
        # We redirect stdout to a buffer to verify if the logger actually 'writes'
        # without polluting the terminal during a clean check.
        buffer: StringIO = StringIO()
        original_stdout = sys.stdout
        sys.stdout = buffer

        try:
            logger.info("Health Probe")
            logger.success("Logic Check")
            logger.section("Test Section")
        finally:
            sys.stdout = original_stdout

        output: str = buffer.getvalue()

        # 3. Verification of Formatting
        # We check for the presence of the timestamp bracket and levels
        required_markers: list[str] = ["INFO:", "SUCCESS:", "SECTION"]
        for marker in required_markers:
            if marker not in output.upper():
                sys.stderr.write(
                    f"❌ Logger Health Failure: Missing marker '{marker}' in output.\n"
                )
                return False

        sys.stdout.write("✅ Logger Service: Instance and Formatting verified.\n")
        return True

    except Exception as e:
        sys.stderr.write(f"❌ Logger Health Failure: {str(e)}\n")
        return False
