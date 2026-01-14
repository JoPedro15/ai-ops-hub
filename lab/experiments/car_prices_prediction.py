import os
from pathlib import Path
from typing import Any, Final

import joblib
import numpy as np
import pandas as pd
import statsmodels.api as sm

from infra.ai_utils import DataIngestor, DataProcessor, ModelVisualizer
from infra.common import logger

# --- Configuration from SSoT (.env / config.py) ---
from infra.common.config import (
    DATA_DIR,
    GDRIVE_DATA_PROCESSED_FOLDER_ID,
    GDRIVE_MODELS_DEV_FOLDER_ID,
    GDRIVE_MODELS_PROD_FOLDER_ID,
    MODELS_DIR,
    PROCESSED_DIR,
    REPORTS_DIR,
)
from infra.gdrive.service import GDriveService

# GDrive IDs
GDRIVE_FILE_ID: Final[str | None] = os.getenv("CAR_DATA_FILE_ID")
GDRIVE_PROC_DATA_ID: Final[str | None] = GDRIVE_DATA_PROCESSED_FOLDER_ID
GDRIVE_MODELS_PROD_ID: Final[str | None] = GDRIVE_MODELS_PROD_FOLDER_ID
GDRIVE_MODELS_DEV_ID: Final[str | None] = GDRIVE_MODELS_DEV_FOLDER_ID


def train_linear_model(X: pd.DataFrame, y: pd.Series) -> Any:
    """Fits an OLS regression model on pre-scaled data."""
    # Add constant for the intercept term in OLS
    X_final: pd.DataFrame = sm.add_constant(X)
    model: Any = sm.OLS(y, X_final).fit()
    return model


def export_assets(
    model: Any,
    df_prepared: pd.DataFrame,
    gdrive: Any,
    report_paths: list[str],
    env: str = "prod",
) -> None:
    """
    Orchestrates the dual-storage strategy: Local Disk and GDrive Synchronization.
    """
    # Ensure directories exist
    for folder in [PROCESSED_DIR, MODELS_DIR, REPORTS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)

    csv_path: Path = PROCESSED_DIR / "car_df_prepared.csv"
    model_path: Path = MODELS_DIR / "car_price_model.pkl"

    # --- LOCAL PERSISTENCE ---
    df_prepared.to_csv(csv_path, index=False)
    joblib.dump(model, model_path)
    logger.success(">>> [LOCAL] Artifacts (CSV/PKL) saved to disk.")

    # --- GDRIVE SYNCHRONIZATION ---
    target_folder: str | None = (
        GDRIVE_MODELS_PROD_ID if env == "prod" else GDRIVE_MODELS_DEV_ID
    )

    if target_folder:
        try:
            # Sync Processed Data and Model
            gdrive.upload_file(str(csv_path), GDRIVE_PROC_DATA_ID or target_folder)
            gdrive.upload_file(str(model_path), target_folder)
            logger.success(f">>> [GDRIVE] Assets synced to folder: {target_folder}")
        except Exception as e:
            logger.error(f"Failed to sync assets to GDrive: {e}")

    # Cloud Sync for Performance Plots
    if GDRIVE_PROC_DATA_ID:
        for report in report_paths:
            if os.path.exists(report):
                try:
                    gdrive.upload_file(report, GDRIVE_PROC_DATA_ID)
                    logger.success(f">>> [GDRIVE] Synced plot: {Path(report).name}")
                except Exception as e:
                    logger.error(f"Failed to sync plot {report}: {e}")


def run_experiment() -> None:
    """
    Orchestrates the optimized experiment using direct imports.
    """
    # 1. Initialize Objects
    data_ingestor: DataIngestor = DataIngestor()
    data_processor: DataProcessor = DataProcessor()
    gdrive: GDriveService = GDriveService()

    if not GDRIVE_FILE_ID:
        raise ValueError("CAR_DATA_FILE_ID is missing in environment variables.")

    logger.section("STARTING OPTIMIZED PRODUCTION EXPERIMENT")

    # 2. Ingestion Phase
    local_raw_path: Path = DATA_DIR / "raw" / "cars.xlsx"
    # Updated: Using the new generic get_data method
    df_raw: pd.DataFrame = data_ingestor.get_data(
        file_id=GDRIVE_FILE_ID, local_file_path=str(local_raw_path)
    )
    df_raw.columns = df_raw.columns.str.strip().str.capitalize()

    # 3. Categorical Encoding
    logger.info("Encoding categorical variables (Make, Model, Type)...")
    df_encoded: pd.DataFrame = data_processor.encode_categorical_features(
        df=df_raw, columns=["Make", "Model", "Type"], drop_first=True
    )

    # 4. Feature Selection & Scaling
    encoded_features: list[str] = [
        col
        for col in df_encoded.columns
        if col.startswith(("Make_", "Model_", "Type_"))
    ]
    numerical_features: list[str] = ["Mileage", "Doors", "Leather"]
    active_features: list[str] = numerical_features + encoded_features

    # Updated: Using DataProcessor for scaling
    logger.info("Scaling numerical features...")
    df_prepared: pd.DataFrame = data_processor.scale_features(
        df_encoded, columns=numerical_features
    )

    # 5. Training (Full Dataset)
    X = df_prepared[active_features]
    y = df_prepared["Price"]

    model = train_linear_model(X, y)

    # 6. Performance Evaluation
    X_final = sm.add_constant(X)
    y_pred: np.ndarray = model.predict(X_final)
    y_real: np.ndarray = y.values

    # 7. Report Generation & Artifact Export
    reports = []

    # Regression Plot
    reg_plot = ModelVisualizer.save_regression_plot(
        y_real, y_pred, output_dir=REPORTS_DIR, model_name="car_price_model"
    )
    reports.append(reg_plot)

    # Residuals Plot (New!)
    res_plot = ModelVisualizer.save_residuals_plot(
        y_real, y_pred, output_dir=REPORTS_DIR, model_name="car_price_model"
    )
    reports.append(res_plot)

    logger.section("PRODUCTION REGRESSION SUMMARY")
    logger.print(str(model.summary()))

    logger.section("EXPORT ASSETS")
    export_assets(model, df_prepared, gdrive=gdrive, report_paths=reports)

    logger.success("EXPERIMENT COMPLETED AND ARCHIVED")


if __name__ == "__main__":
    run_experiment()
