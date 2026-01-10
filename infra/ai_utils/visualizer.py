from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from infra.common.logger import logger


def save_regression_plot(
    y_real: np.ndarray, y_pred: np.ndarray, output_dir: Path, model_name: str = "Model"
) -> str:
    """Generates and saves a standardized performance scatter plot.

    Creates a visualization comparing real vs. predicted values with a 45-degree
    reference line (perfect prediction). The file is saved with a timestamp
    to prevent overwriting.

    Args:
        y_real (np.ndarray): Array containing the ground truth values.
        y_pred (np.ndarray): Array containing the values predicted by the model.
        output_dir (Path): Local directory where the image file will be stored.
        model_name (str): Name of the model to include in the title and filename.
            Defaults to "Model".

    Returns:
        str: The absolute local path to the generated PNG file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path: Path = output_dir / f"{model_name.lower()}_{timestamp}.png"

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=y_real, y=y_pred, alpha=0.6)

    line_range: np.ndarray = np.array([y_real.min(), y_real.max()])
    plt.plot(line_range, line_range, "r--", lw=2, label="Perfect Prediction")

    plt.xlabel("Real Values")
    plt.ylabel("Predictions")
    plt.title(f"{model_name} Performance Analysis - {timestamp}")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.7)

    plt.savefig(report_path)
    plt.close()

    logger.info(f"Report saved at: {report_path}")
    return str(report_path)
