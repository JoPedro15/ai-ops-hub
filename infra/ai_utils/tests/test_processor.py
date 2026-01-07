from typing import Final

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
