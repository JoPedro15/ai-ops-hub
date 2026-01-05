import numpy as np
import pandas as pd

from infra.ai_utils import DataProcessor
from infra.common import logger

__all__: list[str] = ["verify_data_processor"]


def verify_data_processor() -> bool:
    """
    Validates the Data Processor infrastructure and core transformation logic.
    Performs smoke tests on: One-Hot Encoding and Missing Value handling.
    """
    try:
        logger.info("Initializing Data Processor Smoke Test...")

        # 1. Instantiate Service
        processor: DataProcessor = DataProcessor()

        # 2. Logic Test: Categorical Encoding (One-Hot)
        # We verify if the pandas-backed engine correctly transforms data
        test_df: pd.DataFrame = pd.DataFrame(
            {"category": ["A", "B", "A"], "value": [1, 2, 3]}
        )

        encoded_df: pd.DataFrame = processor.encode_categorical_features(
            test_df, columns=["category"], drop_first=True
        )

        # Validation: check if the original column was dropped
        # (standard for drop_first=True)
        if "category" in encoded_df.columns or encoded_df.empty:
            logger.error(
                "Processor Failure: Categorical encoding did "
                "not transform the DataFrame."
            )
            return False

        logger.success("Processor Logic: Categorical encoding verified.")

        # 3. Logic Test: Missing Values (NaN Handling)
        # Ensuring numpy and pandas are correctly integrated for cleaning tasks
        df_nan: pd.DataFrame = pd.DataFrame({"val": [1, np.nan, 3]})
        df_cleaned: pd.DataFrame = processor.handle_missing_values(
            df_nan, strategy="drop"
        )

        if len(df_cleaned) != 2:
            logger.error("Processor Failure: Missing value logic failed to drop NaNs.")
            return False

        logger.success("Processor Logic: NaN handling verified.")

        logger.success("Data Processor: All engines operational (Pandas/Numpy).")
        return True

    except Exception as e:
        logger.error(f"Data Processor Health Failure: {str(e)}")
        return False
