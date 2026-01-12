from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Final

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix

from infra.common.logger import logger

__all__: list[str] = ["ModelVisualizer"]


class ModelVisualizer:
    """
    Utility class for generating standardized model performance visualizations.
    Supports both Regression and Classification metrics.
    """

    @staticmethod
    def _get_timestamp() -> str:
        """Returns current timestamp for file versioning."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def save_regression_plot(
        y_real: np.ndarray,
        y_pred: np.ndarray,
        output_dir: Path,
        model_name: str = "Model",
    ) -> str:
        """
        Generates and saves a scatter plot comparing Real vs. Predicted values.
        Useful for regression tasks.

        Args:
            y_real: Ground truth values.
            y_pred: Predicted values.
            output_dir: Directory to save the plot.
            model_name: Name of the model for labeling.

        Returns:
            str: Absolute path to the saved file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp: Final[str] = ModelVisualizer._get_timestamp()
        filename: str = f"{model_name.lower()}_regression_{timestamp}.png"
        file_path: Path = output_dir / filename

        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=y_real, y=y_pred, alpha=0.6, edgecolor="k")

        # Perfect prediction line (45 degrees)
        min_val = min(y_real.min(), y_pred.min())
        max_val = max(y_real.max(), y_pred.max())
        plt.plot(
            [min_val, max_val],
            [min_val, max_val],
            "r--",
            lw=2,
            label="Perfect Prediction",
        )

        plt.xlabel("Real Values")
        plt.ylabel("Predictions")
        plt.title(f"{model_name} - Regression Analysis")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.7)

        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()

        logger.info(f"Regression plot saved: {file_path}")
        return str(file_path)

    @staticmethod
    def save_residuals_plot(
        y_real: np.ndarray,
        y_pred: np.ndarray,
        output_dir: Path,
        model_name: str = "Model",
    ) -> str:
        """
        Generates a histogram of residuals (errors) to check for normality.
        Residual = y_real - y_pred.

        Args:
            y_real: Ground truth values.
            y_pred: Predicted values.
            output_dir: Directory to save the plot.
            model_name: Name of the model.

        Returns:
            str: Path to the saved file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp: Final[str] = ModelVisualizer._get_timestamp()
        filename: str = f"{model_name.lower()}_residuals_{timestamp}.png"
        file_path: Path = output_dir / filename

        residuals = y_real - y_pred

        plt.figure(figsize=(10, 6))
        sns.histplot(residuals, kde=True, bins=30, color="purple")
        plt.axvline(x=0, color="r", linestyle="--", lw=2)

        plt.xlabel("Residuals (Error)")
        plt.title(f"{model_name} - Residuals Distribution")
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()

        logger.info(f"Residuals plot saved: {file_path}")
        return str(file_path)

    @staticmethod
    def save_confusion_matrix(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        output_dir: Path,
        labels: list[str] | None = None,
        model_name: str = "Model",
    ) -> str:
        """
        Generates and saves a Confusion Matrix heatmap.
        Useful for classification tasks.

        Args:
            y_true: Ground truth class labels.
            y_pred: Predicted class labels.
            output_dir: Directory to save the plot.
            labels: List of class names for the axis.
            model_name: Name of the model.

        Returns:
            str: Path to the saved file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp: Final[str] = ModelVisualizer._get_timestamp()
        filename: str = f"{model_name.lower()}_conf_matrix_{timestamp}.png"
        file_path: Path = output_dir / filename

        cm = confusion_matrix(y_true, y_pred)

        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=labels if labels else "auto",
            yticklabels=labels if labels else "auto",
        )

        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.title(f"{model_name} - Confusion Matrix")

        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()

        logger.info(f"Confusion Matrix saved: {file_path}")
        return str(file_path)

    def __repr__(self) -> str:
        return "<ModelVisualizer>"
