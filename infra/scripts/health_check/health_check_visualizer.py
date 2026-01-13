import tempfile
from pathlib import Path

import numpy as np

from infra.ai_utils import ModelVisualizer
from infra.common.logger import logger

__all__: list[str] = ["verify_visualizer"]


def verify_visualizer() -> bool:
    """
    Validates the Model Visualizer infrastructure.
    Checks for graphical dependencies and performs smoke tests on plot generation.
    """
    logger.subsection("Checking Model Visualizer Engines...")
    all_ok = True

    # 1. Verify Graphical Dependencies
    try:
        import matplotlib.pyplot as plt  # noqa: F401
        import seaborn as sns  # noqa: F401

        logger.success("Engine Check: 'matplotlib' and 'seaborn' are available.")
    except ImportError as e:
        logger.error(f"Engine Missing: Visualization libraries not found: {e}")
        return False

    # 2. Perform Plot Generation Tests
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        try:
            # Test A: Regression Plot
            y_real = np.array([10, 20, 30])
            y_pred = np.array([12, 18, 33])

            reg_path = ModelVisualizer.save_regression_plot(
                y_real, y_pred, output_dir, model_name="HealthCheckReg"
            )

            if Path(reg_path).exists() and Path(reg_path).stat().st_size > 0:
                logger.success("Visualizer Logic: Regression plot generated.")
            else:
                logger.error("Visualizer Failure: Regression plot not created.")
                all_ok = False

            # Test B: Confusion Matrix
            y_true = np.array([0, 1, 0])
            y_p_clf = np.array([0, 1, 1])

            cm_path = ModelVisualizer.save_confusion_matrix(
                y_true,
                y_p_clf,
                output_dir,
                labels=["No", "Yes"],
                model_name="HealthCheckClf",
            )

            if Path(cm_path).exists() and Path(cm_path).stat().st_size > 0:
                logger.success("Visualizer Logic: Confusion matrix generated.")
            else:
                logger.error("Visualizer Failure: Confusion matrix not created.")
                all_ok = False

        except Exception as e:
            logger.error(f"Visualizer Health Failure: {str(e)}")
            return False

    if all_ok:
        logger.success("Model Visualizer: All plotting engines operational.")

    return all_ok
