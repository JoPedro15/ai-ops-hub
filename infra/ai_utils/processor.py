from __future__ import annotations

from typing import Final, Literal

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from infra.common.logger import logger

__all__: list[str] = ["DataProcessor"]


class DataProcessor:
    """
    Service specialized in feature engineering and data transformation.
    Ensures DataFrames are formatted correctly for Machine Learning pipelines.
    """

    def __init__(self) -> None:
        """
        Initializes the DataProcessor.
        """
        pass

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

    def scale_features(self, df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """
        Applies Standard Scaling (z-score) to specified numerical columns.

        Args:
            df: Input DataFrame.
            columns: List of numerical columns to scale.

        Returns:
            pd.DataFrame: DataFrame with scaled columns.
        """
        if df.empty or not columns:
            return df

        work_df: Final[pd.DataFrame] = df.copy()
        valid_cols = [c for c in columns if c in work_df.columns]

        if not valid_cols:
            logger.warning("No valid columns found for scaling.")
            return work_df

        logger.info(f"Scaling features: {valid_cols}")
        scaler = StandardScaler()
        work_df[valid_cols] = scaler.fit_transform(work_df[valid_cols])
        return work_df

    @staticmethod
    def split_data(
        x: np.ndarray | pd.DataFrame,
        y: np.ndarray | pd.Series,
        train_size: float = 0.8,
        shuffle: bool = True,
        seed: int = 42,
        stratify: np.ndarray | pd.Series | None = None,
    ) -> tuple:
        """
        Splits the dataset into training and testing sets using scikit-learn.

        Args:
            x: The feature matrix (input data).
            y: The labels or target values.
            train_size: The proportion of the dataset to include in the train split.
            shuffle: Whether or not to shuffle the data before splitting.
            seed: Random seed for reproducibility.
            stratify: If not None, data is split in a stratified fashion, using
                this as the class labels.

        Returns:
            tuple: (train_x, test_x, train_y, test_y)
        """
        return train_test_split(
            x,
            y,
            train_size=train_size,
            shuffle=shuffle,
            random_state=seed,
            stratify=stratify,
        )

    def __repr__(self) -> str:
        """String representation for better audit logs."""
        return "<DataProcessor(mode=local)>"
