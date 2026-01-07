from __future__ import annotations

from typing import Final, Literal

import pandas as pd

from infra.common.logger import logger
from infra.gdrive.service import GDriveService

__all__: list[str] = ["DataProcessor"]


class DataProcessor:
    """
    Service specialized in feature engineering and data transformation.
    Ensures DataFrames are formatted correctly for Machine Learning pipelines.
    """

    def __init__(self, gdrive_service: GDriveService | None = None) -> None:
        """
        Initializes the DataProcessor with an optional GDrive session.
        """
        self.gdrive: GDriveService | None = gdrive_service

    def encode_categorical_features(
        self, df: pd.DataFrame, columns: list[str], drop_first: bool = True
    ) -> pd.DataFrame:
        """
        Performs One-Hot Encoding on categorical features.

        Args:
            df: Input DataFrame.
            columns: Categorical columns to transform.
            drop_first: If True, uses k-1 dummies to prevent multi-collinearity.

        Returns:
            pd.DataFrame: Transformed DataFrame with numeric dummy columns.
        """
        if df.empty:
            logger.warning("Encoding skipped: Provided DataFrame is empty.")
            return df

        # SSoT: Create a deep copy to prevent side effects on the original DF
        # Using Final to ensure the reference to this workspace is constant
        work_df: Final[pd.DataFrame] = df.copy()

        # Filter existing columns to avoid KeyError
        valid_cols: Final[list[str]] = [
            col for col in columns if col in work_df.columns
        ]

        if not valid_cols:
            logger.warning("No valid categorical columns found for encoding.")
            return work_df

        logger.info(f"Applying One-Hot Encoding to: {valid_cols}")

        # dtype=int ensures 0/1 instead of True/False, better for OLS/Linear models
        return pd.get_dummies(
            work_df, columns=valid_cols, drop_first=drop_first, dtype=int
        )

    def handle_missing_values(
        self,
        df: pd.DataFrame,
        strategy: Literal["drop", "fill"] = "drop",
        fill_value: float | int | str | None = None,
    ) -> pd.DataFrame:
        """
        Cleans the dataset by removing or populating missing (NaN) values.

        Args:
            df: Input DataFrame.
            strategy: 'drop' to remove rows, 'fill' to replace with fill_value.
            fill_value: Scalar used for replacement if strategy is 'fill'.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        if df.empty:
            logger.warning(
                "Missing values handling skipped: Provided DataFrame is empty."
            )
            return df

        logger.info(f"Executing missing values strategy: {strategy}")
        work_df: Final[pd.DataFrame] = df.copy()

        if strategy == "drop":
            cleaned_df: pd.DataFrame = work_df.dropna()
            rows_removed: Final[int] = len(work_df) - len(cleaned_df)

            if rows_removed > 0:
                logger.info(
                    f"Integrity Check: Dropped {rows_removed} rows containing NaNs."
                )
            return cleaned_df

        if strategy == "fill":
            if fill_value is None:
                logger.error(
                    "Strategy 'fill' requires a valid 'fill_value'. "
                    "Returning original DF."
                )
                return work_df

            return work_df.fillna(value=fill_value)

        return work_df

    def __repr__(self) -> str:
        """String representation for better audit logs."""
        status: str = "connected" if self.gdrive else "local-only"
        return f"<DataProcessor(mode={status})>"
