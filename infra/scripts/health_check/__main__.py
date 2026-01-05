import importlib
import pkgutil
import sys
from collections.abc import Callable
from typing import Any

# Standard absolute imports
from infra.common.logger import logger

__all__: list[str] = ["orchestrate_health_suite"]


def orchestrate_health_suite() -> None:
    """
    Dynamically discovers and executes all health check modules
    within the infra.scripts.health_check package.
    """
    logger.section("GLOBAL INFRASTRUCTURE HEALTH CHECK")

    # 1. Define the package to scan
    package_name: str = "infra.scripts.health_check"

    # Get the actual file system path of this package
    package_module = sys.modules.get(package_name)
    if not package_module or not package_module.__path__:
        # Fallback if not already loaded (unlikely in __main__)
        spec = importlib.util.find_spec(package_name)
        if not spec or not spec.submodule_search_locations:
            logger.error(f"Could not locate package: {package_name}")
            sys.exit(1)
        search_path: list[str] = list(spec.submodule_search_locations)
    else:
        search_path = list(package_module.__path__)

    failed_components: list[str] = []
    executed_count: int = 0

    # 2. Dynamic Discovery
    # We iterate over all modules in the current directory
    for _, module_name, is_pkg in pkgutil.iter_modules(search_path):
        # Skip internal files and the orchestrator itself
        if module_name in ["__main__", "__init__"] or is_pkg:
            continue

        display_name: str = module_name.replace("_", " ").title()
        full_module_path: str = f"{package_name}.{module_name}"

        try:
            # 3. Dynamic Import & Execution
            module: Any = importlib.import_module(full_module_path)

            # We look for functions starting with 'verify_'
            # (Standardized in our previous steps)
            check_functions: list[Callable[[], bool]] = [
                func
                for name, func in vars(module).items()
                if name.startswith("verify_") and callable(func)
            ]

            if not check_functions:
                continue

            executed_count += 1

            # Execute all verification functions found in the module
            for check_func in check_functions:
                success: bool = check_func()

                if not success:
                    failed_components.append(f"{display_name} ({check_func.__name__})")

        except Exception as e:
            logger.error(f"Crash during {display_name} execution: {str(e)}")
            failed_components.append(display_name)

    # 4. Final Verdict Logic
    logger.print("-" * 50)
    if failed_components:
        logger.error(f"VERDICT: SCALED. {len(failed_components)} component(s) failed.")
        logger.error(f"Failures: {', '.join(failed_components)}")
        sys.exit(1)

    if executed_count == 0:
        logger.warning("VERDICT: NO TESTS FOUND. Check module naming conventions.")
        sys.exit(0)

    logger.success(
        f"VERDICT: ALL SYSTEMS RX. {executed_count} modules verified successfully."
    )
    sys.exit(0)


if __name__ == "__main__":
    orchestrate_health_suite()
