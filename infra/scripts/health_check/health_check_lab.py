# infra/scripts/health_check/lab_health.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

import nbformat

from infra.common.logger import logger

# Ensure root is in path to access config and infra
ROOT_DIR: Final[Path] = Path(__file__).parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))


def verify_ai_lab_health() -> bool:
    """
    Validates the integrity and structure of all notebooks in the AI Lab.
    Returns True if all checks pass, False otherwise.
    """
    notebooks_dir: Final[Path] = ROOT_DIR / "lab" / "notebooks"
    logger.subsection("AI Lab Readiness Check")

    if not notebooks_dir.exists():
        logger.error(f"Notebooks directory not found: {notebooks_dir}")
        return False

    # Find notebooks, excluding checkpoints
    notebook_files: list[Path] = list(notebooks_dir.glob("**/*.ipynb"))
    notebook_files = [
        nb for nb in notebook_files if ".ipynb_checkpoints" not in str(nb)
    ]

    if not notebook_files:
        logger.warning(
            f"No notebooks found in {notebooks_dir}. Research area is empty."
        )
        return True  # Empty lab is not a failure, but a warning

    failed_notebooks: list[str] = []

    for nb_path in notebook_files:
        try:
            with open(nb_path, encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)

                # Structural validation
                has_cells: bool = "cells" in nb and len(nb.cells) > 0
                has_kernel: bool = "kernelspec" in nb.metadata

                if not has_cells or not has_kernel:
                    failed_notebooks.append(nb_path.name)
                    logger.warning(
                        f"Integrity issue in {nb_path.name}: "
                        "Empty cells or missing kernel metadata."
                    )
                else:
                    logger.info(f"Verified: {nb_path.name}")

        except Exception as e:
            failed_notebooks.append(nb_path.name)
            logger.error(f"Critical failure parsing {nb_path.name}: {e}")

    # Final Report
    if failed_notebooks:
        logger.error(f"Lab Health Check failed for: {', '.join(failed_notebooks)}")
        return False

    logger.success(f"Successfully validated {len(notebook_files)} notebooks.")
    return True


if __name__ == "__main__":
    if not verify_ai_lab_health():
        sys.exit(1)
