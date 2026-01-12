from pathlib import Path

import numpy as np
import pytest

from infra.ai_utils import ModelVisualizer


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Provides a temporary directory for saving plots."""
    return tmp_path / "reports"


def test_save_regression_plot(output_dir: Path) -> None:
    """Ensures regression plot is generated and saved correctly."""
    y_real = np.array([10, 20, 30, 40, 50])
    y_pred = np.array([12, 18, 33, 38, 55])

    file_path = ModelVisualizer.save_regression_plot(
        y_real, y_pred, output_dir, model_name="TestReg"
    )

    path = Path(file_path)
    assert path.exists()
    assert path.suffix == ".png"
    assert "testreg_regression_" in path.name
    assert path.stat().st_size > 0


def test_save_residuals_plot(output_dir: Path) -> None:
    """Ensures residuals histogram is generated and saved."""
    y_real = np.random.rand(100)
    y_pred = y_real + np.random.normal(0, 0.1, 100)

    file_path = ModelVisualizer.save_residuals_plot(
        y_real, y_pred, output_dir, model_name="TestResid"
    )

    path = Path(file_path)
    assert path.exists()
    assert "testresid_residuals_" in path.name


def test_save_confusion_matrix(output_dir: Path) -> None:
    """Ensures confusion matrix heatmap is generated and saved."""
    y_true = np.array([0, 1, 0, 1, 1, 0])
    y_pred = np.array([0, 1, 0, 0, 1, 1])

    file_path = ModelVisualizer.save_confusion_matrix(
        y_true, y_pred, output_dir, labels=["No", "Yes"], model_name="TestClf"
    )

    path = Path(file_path)
    assert path.exists()
    assert "testclf_conf_matrix_" in path.name
