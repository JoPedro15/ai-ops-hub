from typing import Literal

import pandas as pd

# Direct import to avoid circular dependencies within infra
from infra.common.logger import logger
from infra.gdrive.service import GDriveService

__all__: list[str] = ["DataProcessor"]


class DataProcessor:
    """
    Client specialized in data processing and feature engineering tasks.
    Provides standardized methods to transform DataFrames for AI pipelines.
    """

    def __init__(self, gdrive_service: GDriveService | None = None) -> None:
        """
        Initializes the DataProcessor.

        Args:
            gdrive_service: Optional GDriveService instance for data-dependent tasks.
        """
        self.gdrive: GDriveService | None = gdrive_service

    def encode_categorical_features(
        self, df: pd.DataFrame, columns: list[str], drop_first: bool = True
    ) -> pd.DataFrame:
        """
        Encodes categorical features using One-Hot Encoding (Dummy Encoding).

        Args:
            df: The input pandas DataFrame.
            columns: A list of column names to be encoded.
            drop_first: Whether to get k-1 dummies out of k categorical levels.

        Returns:
            pd.DataFrame: A new DataFrame with transformed categorical features.
        """
        # Filter columns that actually exist in the DataFrame
        existing_cols: list[str] = [col for col in columns if col in df.columns]

        if not existing_cols:
            logger.warning("No matching columns found for encoding.")
            return df

        logger.info(f"Encoding categorical columns: {existing_cols}")
        return pd.get_dummies(df, columns=existing_cols, drop_first=drop_first)

    def handle_missing_values(
        self,
        df: pd.DataFrame,
        strategy: Literal["drop", "fill"] = "drop",
        fill_value: float | int | str | None = None,
    ) -> pd.DataFrame:
        """
        Handles missing values in the dataset based on the chosen strategy.

        Args:
            df: Input DataFrame.
            strategy: Method to handle NaNs ('drop' or 'fill').
            fill_value: The value to use if strategy is 'fill'.
        """
        logger.info(f"Handling missing values with strategy: {strategy}")

        if strategy == "drop":
            return df.dropna()

        if strategy == "fill":
            return df.fillna(value=fill_value) if fill_value is not None else df

        return df
