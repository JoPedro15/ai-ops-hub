import os
from pathlib import Path
from typing import Any, Final

import joblib
import numpy as np
import pandas as pd
import statsmodels.api as sm
from dotenv import load_dotenv
from sklearn.preprocessing import StandardScaler

# --- Configuration from SSoT (.env / config.py) ---
from config import DATA_DIR, MODELS_DIR, PROCESSED_DIR, REPORTS_DIR
from infra.ai_utils import DataIngestor, DataProcessor, ModelVisualizer
from infra.common.logger import logger
from infra.gdrive.service import GDriveService

# 1. Environment Orchestration
load_dotenv()


# GDrive IDs
GDRIVE_FILE_ID: Final[str | None] = os.getenv("CAR_DATA_FILE_ID")
GDRIVE_PROC_DATA_ID: Final[str | None] = os.getenv("GDRIVE_DATA_PROCESSED_FOLDER_ID")
GDRIVE_MODELS_PROD_ID: Final[str | None] = os.getenv("GDRIVE_MODELS_PROD_FOLDER_ID")
GDRIVE_MODELS_DEV_ID: Final[str | None] = os.getenv("GDRIVE_MODELS_DEV_FOLDER_ID")


def train_linear_model(
    data: pd.DataFrame, features: list[str]
) -> tuple[Any, StandardScaler]:
    """Standardizes features and fits an OLS regression model."""
    X: pd.DataFrame = data[features].copy()
    y: pd.Series = data["Price"]

    scaler: StandardScaler = StandardScaler()
    X_scaled: np.ndarray = scaler.fit_transform(X)

    X_scaled_df: pd.DataFrame = pd.DataFrame(X_scaled, columns=features, index=X.index)
    X_final: pd.DataFrame = sm.add_constant(X_scaled_df)

    model: Any = sm.OLS(y, X_final).fit()
    return model, scaler


def export_assets(
    model: Any,
    scaler: StandardScaler,
    df_prepared: pd.DataFrame,
    gdrive: Any,
    report_path: str | None = None,
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
    scaler_path: Path = MODELS_DIR / "car_scaler.pkl"

    # --- LOCAL PERSISTENCE ---
    df_prepared.to_csv(csv_path, index=False)
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    logger.success(">>> [LOCAL] Artifacts (CSV/PKL) saved to disk.")

    # --- GDRIVE SYNCHRONIZATION ---
    target_folder: str | None = (
        GDRIVE_MODELS_PROD_ID if env == "prod" else GDRIVE_MODELS_DEV_ID
    )

    if target_folder:
        try:
            # Sync Processed Data, Models and Scaler
            gdrive.upload_file(str(csv_path), GDRIVE_PROC_DATA_ID or target_folder)
            gdrive.upload_file(str(model_path), target_folder)
            gdrive.upload_file(str(scaler_path), target_folder)
            logger.success(f">>> [GDRIVE] Assets synced to folder: {target_folder}")
        except Exception as e:
            logger.error(f"Failed to sync assets to GDrive: {e}")

    # Cloud Sync for Performance Plot
    if report_path and os.path.exists(report_path) and GDRIVE_PROC_DATA_ID:
        try:
            gdrive.upload_file(report_path, GDRIVE_PROC_DATA_ID)
            logger.success(">>> [GDRIVE] Performance plot synced to GDrive.")
        except Exception as e:
            logger.error(f"Failed to sync plot to GDrive: {e}")


def run_experiment() -> None:
    """
    Orchestrates the optimized experiment using direct imports.
    """
    # DIRECT IMPORTS: No more factories, no more unresolved references

    # 1. Initialize Objects Directly
    data_ingestor: DataIngestor = DataIngestor()
    data_processor: DataProcessor = DataProcessor()
    gdrive: GDriveService = GDriveService()

    if not GDRIVE_FILE_ID:
        raise ValueError("CAR_DATA_FILE_ID is missing in environment variables.")

    logger.section("STARTING OPTIMIZED PRODUCTION EXPERIMENT")

    # 2. Ingestion Phase
    local_raw_path: Path = DATA_DIR / "raw" / "cars.xlsx"
    df_raw: pd.DataFrame = data_ingestor.get_spreadsheet_data(
        file_id=GDRIVE_FILE_ID, local_file_path=str(local_raw_path)
    )
    df_raw.columns = df_raw.columns.str.strip().str.capitalize()

    # 3. Categorical Encoding
    logger.info("Encoding categorical variables (Make, Model, Type)...")
    df_prepared: pd.DataFrame = data_processor.encode_categorical_features(
        df=df_raw, columns=["Make", "Model", "Type"], drop_first=True
    )

    # 4. Feature Selection & Training
    encoded_features: list[str] = [
        col
        for col in df_prepared.columns
        if col.startswith(("Make_", "Model_", "Type_"))
    ]
    active_features: list[str] = ["Mileage", "Doors", "Leather"] + encoded_features

    model, scaler = train_linear_model(df_prepared, active_features)

    # 5. Performance Evaluation
    X_scaled: np.ndarray = scaler.transform(df_prepared[active_features])
    X_scaled_df: pd.DataFrame = pd.DataFrame(
        X_scaled, columns=active_features, index=df_prepared.index
    )
    X_final: pd.DataFrame = sm.add_constant(X_scaled_df)

    y_pred: np.ndarray = model.predict(X_final)
    y_real: np.ndarray = df_prepared["Price"].values

    # 6. Report Generation & Artifact Export
    report_file: str = ModelVisualizer.save_regression_plot(
        y_real, y_pred, output_dir=REPORTS_DIR, model_name="car_price_model"
    )

    logger.section("PRODUCTION REGRESSION SUMMARY")
    logger.print(str(model.summary()))

    logger.section("EXPORT ASSETS")
    export_assets(model, scaler, df_prepared, gdrive=gdrive, report_path=report_file)

    logger.success("EXPERIMENT COMPLETED AND ARCHIVED")


if __name__ == "__main__":
    run_experiment()
