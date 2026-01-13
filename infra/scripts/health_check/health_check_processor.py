import numpy as np
import pandas as pd

from infra.ai_utils import DataProcessor
from infra.common.logger import logger

__all__: list[str] = ["verify_data_processor"]


def verify_data_processor() -> bool:
    """
    Validates the Data Processor's core transformation logic.
    Performs smoke tests on all major functionalities.
    """
    try:
        logger.subsection("Initializing Data Processor Smoke Test...")
        processor = DataProcessor()

        # 1. Test: Categorical Encoding (One-Hot)
        df_cat = pd.DataFrame({"category": ["A", "B", "A"], "value": [1, 2, 3]})
        encoded_df = processor.encode_categorical_features(df_cat, columns=["category"])
        if "category_B" not in encoded_df.columns or "category" in encoded_df.columns:
            logger.error("Processor Failure: Categorical encoding failed.")
            return False
        logger.success("Processor Logic: Categorical encoding verified.")

        # 2. Test: Missing Values (NaN Handling)
        df_nan = pd.DataFrame({"val": [1, np.nan, 3]})
        df_cleaned = processor.handle_missing_values(df_nan, strategy="drop")
        if len(df_cleaned) != 2:
            logger.error("Processor Failure: NaN handling failed.")
            return False
        logger.success("Processor Logic: NaN handling verified.")

        # 3. Test: Feature Scaling
        df_scale = pd.DataFrame({"feature": [10, 20, 30, 40, 50]})
        scaled_df = processor.scale_features(df_scale, columns=["feature"])
        # The mean of a scaled feature should be close to 0
        if not np.isclose(scaled_df["feature"].mean(), 0):
            logger.error("Processor Failure: Feature scaling failed.")
            return False
        logger.success("Processor Logic: Feature scaling verified.")

        # 4. Test: Data Splitting
        X = np.arange(100).reshape(50, 2)
        y = np.arange(50)
        train_x, test_x, _, _ = DataProcessor.split_data(X, y, train_size=0.8)
        if train_x.shape[0] != 40 or test_x.shape[0] != 10:
            logger.error("Processor Failure: Split returned incorrect dimensions.")
            return False
        logger.success("Processor Logic: Data splitting verified.")

        logger.success("Data Processor: All engines operational.")
        return True

    except Exception as e:
        logger.error(f"Data Processor Health Failure: {str(e)}")
        return False
