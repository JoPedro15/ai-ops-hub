from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from dotenv import load_dotenv
from sklearn.preprocessing import StandardScaler

from config import (
    GDRIVE_DATA_PROCESSED_FOLDER_ID,
    GDRIVE_MODELS_DEV_FOLDER_ID,
    GDRIVE_MODELS_PROD_FOLDER_ID,
    GDRIVE_REPORTS_FOLDER_ID,
    MODELS_DIR,
    PROCESSED_DIR,
    RAW_DIR,
    REPORTS_DIR,
)
from infra.ai_utils import DataIngestor, DataProcessor
from infra.common.logger import logger
from infra.gdrive.service import GDriveService

load_dotenv()
GDRIVE_FILE_ID: Final[str | None] = os.getenv("CAR_DATA_FILE_ID")


def train_linear_model(
    data: pd.DataFrame, features: list[str]
) -> tuple[Any, StandardScaler]:
    """Standardizes features and fits an OLS regression model."""
    data_processor = DataProcessor()

    # Define the columns to check
    cols_to_check: list[str] = features + ["Price"]

    # Process the data to drop missing values
    processed_data: pd.DataFrame = data_processor.handle_missing_values(
        df=data[cols_to_check]
    )

    # Isolate the dependent from the independents vars
    X: pd.DataFrame = processed_data[features].copy()
    y: pd.Series = processed_data["Price"]

    # Create a StandardScaler to save our calibration
    scaler: StandardScaler = StandardScaler()
    # Uniformize the data into a comparable scale
    X_scaled: np.ndarray = scaler.fit_transform(X)

    # Create a scaled dataFrame using the normalized data plus the features
    # index allow the Dataframe lines to keep its index, in case empty line were removed
    X_scaled_df: pd.DataFrame = pd.DataFrame(X_scaled, columns=features, index=X.index)
    X_final: pd.DataFrame = sm.add_constant(X_scaled_df)

    # Ordinary Least Squares: we create a model with all the data
    model: Any = sm.OLS(y, X_final).fit()
    return model, scaler


def generate_performance_report(y_real: np.ndarray, y_pred: np.ndarray) -> str:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path: Path = REPORTS_DIR / f"performance_{timestamp}.png"

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=y_real, y=y_pred, alpha=0.6)

    line_range: np.ndarray = np.array([y_real.min(), y_real.max()])
    plt.plot(line_range, line_range, "r--", lw=2, label="Perfect Prediction")

    plt.xlabel("Real Price ($)")
    plt.ylabel("Predicted Price ($)")
    plt.title(f"Model Performance Analysis - {timestamp}")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.7)

    plt.savefig(report_path)
    plt.close()

    logger.info(f"Visual report saved locally at: {report_path}")
    return str(report_path)


def export_assets(
    model: Any,
    scaler: StandardScaler,
    df_prepared: pd.DataFrame,
    gdrive: GDriveService,
    report_path: str | None = None,
    env: str = "prod",
) -> None:
    csv_path: Path = PROCESSED_DIR / "car_df_prepared.csv"
    model_path: Path = MODELS_DIR / "car_price_model.pkl"
    scaler_path: Path = MODELS_DIR / "car_scaler.pkl"

    df_prepared.to_csv(csv_path, index=False)
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    logger.success(">>> [LOCAL] Artifacts saved.")

    # 2. GDrive Sync
    target_folder_id: str | None = (
        GDRIVE_MODELS_PROD_FOLDER_ID if env == "prod" else GDRIVE_MODELS_DEV_FOLDER_ID
    )

    if target_folder_id and GDRIVE_DATA_PROCESSED_FOLDER_ID:
        try:
            gdrive.upload_file(str(csv_path), GDRIVE_DATA_PROCESSED_FOLDER_ID)
            gdrive.upload_file(str(model_path), target_folder_id)
            gdrive.upload_file(str(scaler_path), target_folder_id)
            logger.success(">>> [GDRIVE] Assets synced successfully.")
        except Exception as e:
            logger.error(f"Failed to sync assets to GDrive: {e}")

    if report_path and GDRIVE_REPORTS_FOLDER_ID:
        try:
            gdrive.upload_file(report_path, GDRIVE_REPORTS_FOLDER_ID)
            logger.success(">>> [GDRIVE] Performance plot synced.")
        except Exception as e:
            logger.error(f"Failed to sync plot to GDrive: {e}")


def run_experiment() -> None:
    data_ingestor: DataIngestor = DataIngestor()
    data_processor: DataProcessor = DataProcessor()
    gdrive: GDriveService = GDriveService()

    if not GDRIVE_FILE_ID:
        raise ValueError("CAR_DATA_FILE_ID is missing in environment variables.")

    logger.section("STARTING OPTIMIZED PRODUCTION EXPERIMENT")

    # Ingestion
    local_raw_path: Path = RAW_DIR / "cars.xlsx"
    df_raw: pd.DataFrame = data_ingestor.get_spreadsheet_data(
        file_id=GDRIVE_FILE_ID, local_file_path=str(local_raw_path)
    )
    df_raw.columns = df_raw.columns.str.strip().str.capitalize()

    # Pre-processing
    df_prepared: pd.DataFrame = data_processor.encode_categorical_features(
        df=df_raw, columns=["Make", "Model", "Type"], drop_first=True
    )

    # Features
    encoded_features: list[str] = [
        col
        for col in df_prepared.columns
        if col.startswith(("Make_", "Model_", "Type_"))
    ]

    active_features: list[str] = ["Mileage", "Doors", "Leather"] + encoded_features

    model, scaler = train_linear_model(df_prepared, active_features)

    # Eval
    X_scaled: np.ndarray = scaler.transform(df_prepared[active_features])
    X_final: pd.DataFrame = sm.add_constant(
        pd.DataFrame(X_scaled, columns=active_features, index=df_prepared.index)
    )
    y_pred: np.ndarray = model.predict(X_final)
    y_real: np.ndarray = df_prepared["Price"].values

    # Reports & Export (Removida a importação circular)
    report_file: str = generate_performance_report(y_real, y_pred)

    logger.section("PRODUCTION REGRESSION SUMMARY")
    logger.print(str(model.summary()))

    export_assets(model, scaler, df_prepared, gdrive=gdrive, report_path=report_file)
    logger.success("EXPERIMENT COMPLETED AND ARCHIVED")


if __name__ == "__main__":
    run_experiment()
