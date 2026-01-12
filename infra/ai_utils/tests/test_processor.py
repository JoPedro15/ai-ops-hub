from typing import Final

import numpy as np
import pandas as pd
import pytest

from infra.ai_utils import DataProcessor


@pytest.fixture
def processor() -> DataProcessor:
    """Initializes the DataProcessor service."""
    return DataProcessor()


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Provides a DataFrame with mixed data for testing."""
    return pd.DataFrame(
        {"category": ["A", "B", "A"], "values": [10.0, None, 30.0], "target": [1, 0, 1]}
    )


def test_encode_categorical_features_success(
    processor: DataProcessor, sample_df: pd.DataFrame
) -> None:
    """Ensures categorical columns are transformed into numeric dummies."""
    processed_df: pd.DataFrame = processor.encode_categorical_features(
        sample_df, columns=["category"]
    )

    assert "category" not in processed_df.columns
    # Check if we have the dummy column (category_B because drop_first=True)
    assert "category_B" in processed_df.columns
    assert processed_df["category_B"].dtype == int


def test_encode_categorical_features_missing_col(
    processor: DataProcessor, sample_df: pd.DataFrame
) -> None:
    """Ensures that passing a non-existent column doesn't break the processor."""
    processed_df: pd.DataFrame = processor.encode_categorical_features(
        sample_df, columns=["non_existent"]
    )

    # Should return a copy of the original DF since no valid columns were found
    pd.testing.assert_frame_equal(processed_df, sample_df)


def test_handle_missing_values_fill(
    processor: DataProcessor, sample_df: pd.DataFrame
) -> None:
    """Validates the 'fill' strategy replaces NaNs with the provided value."""
    fill_val: Final[float] = 0.0
    cleaned_df: pd.DataFrame = processor.handle_missing_values(
        sample_df, strategy="fill", fill_value=fill_val
    )

    assert len(cleaned_df) == 3
    assert cleaned_df["values"].iloc[1] == fill_val
    assert cleaned_df["values"].isna().sum() == 0


def test_processor_immutability(
    processor: DataProcessor, sample_df: pd.DataFrame
) -> None:
    """Verifies that the original DataFrame remains untouched (SSoT)."""
    original_copy: Final[pd.DataFrame] = sample_df.copy()

    processor.handle_missing_values(sample_df, strategy="drop")
    processor.encode_categorical_features(sample_df, columns=["category"])

    # If copy() works, sample_df must be identical to its state before processing
    pd.testing.assert_frame_equal(sample_df, original_copy)


def test_handle_empty_dataframe(processor: DataProcessor) -> None:
    """Ensures the processor handles empty inputs gracefully."""
    empty_df: Final[pd.DataFrame] = pd.DataFrame()

    result: pd.DataFrame = processor.handle_missing_values(empty_df)
    assert result.empty


# --- NEW TESTS FOR SCALING & SPLITTING ---


def test_scale_features_success(processor: DataProcessor) -> None:
    """Validates that numerical features are scaled (mean~0, std~1)."""
    df = pd.DataFrame({"a": [10, 20, 30, 40, 50], "b": ["x", "y", "z", "w", "k"]})

    scaled_df = processor.scale_features(df, columns=["a"])

    # Check if mean is close to 0
    assert np.isclose(scaled_df["a"].mean(), 0, atol=1e-1)

    # Check if std is close to 1.
    # Important: StandardScaler uses population std (ddof=0),
    # while pandas default is sample std (ddof=1).
    assert np.isclose(scaled_df["a"].std(ddof=0), 1, atol=1e-1)

    # Ensure other columns are untouched
    assert scaled_df["b"].equals(df["b"])


def test_scale_features_invalid_col(
    processor: DataProcessor, sample_df: pd.DataFrame
) -> None:
    """Ensures invalid columns are ignored during scaling."""
    original_copy = sample_df.copy()
    result = processor.scale_features(sample_df, columns=["non_existent"])
    pd.testing.assert_frame_equal(result, original_copy)


def test_split_data_dimensions() -> None:
    """Validates that split_data returns correct array shapes."""
    X = np.arange(100).reshape(100, 1)
    y = np.arange(100)

    train_x, test_x, train_y, test_y = DataProcessor.split_data(
        X, y, train_size=0.8, shuffle=False
    )

    assert len(train_x) == 80
    assert len(test_x) == 20
    assert len(train_y) == 80
    assert len(test_y) == 20


def test_split_data_stratify() -> None:
    """Validates that stratification maintains class proportions."""
    # Create imbalanced dataset: 90% class 0, 10% class 1
    X = np.zeros((100, 2))
    y = np.array([0] * 90 + [1] * 10)

    train_x, test_x, train_y, test_y = DataProcessor.split_data(
        X, y, train_size=0.8, stratify=y, seed=42
    )

    # Check if test set has roughly 10% of class 1 (2 samples out of 20)
    assert sum(test_y) == 2
    assert len(test_y) == 20


def test_split_data_pandas_support() -> None:
    """Ensures split_data works with Pandas objects."""
    # Create a larger dataset to avoid rounding issues with small splits
    df = pd.DataFrame(
        {"category": ["A"] * 10, "values": range(10), "target": [0, 1] * 5}
    )

    X = df[["category", "values"]]
    y = df["target"]

    train_x, test_x, train_y, test_y = DataProcessor.split_data(
        X, y, train_size=0.8, seed=42
    )

    assert isinstance(train_x, pd.DataFrame)
    assert isinstance(train_y, pd.Series)
    assert len(train_x) == 8  # 80% of 10
    assert len(test_x) == 2  # 20% of 10
