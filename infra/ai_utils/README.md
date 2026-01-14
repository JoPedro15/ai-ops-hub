# AI Utilities (ai_utils)

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A specialized utility toolkit for the **ai-ops-hub** ecosystem. This package orchestrates data acquisition, local
caching, feature engineering, and visualization to provide a seamless bridge between raw data storage and AI model training.

## Features

- **Resilient Data Ingestion**: Managed downloads from GDrive with built-in file health checks and cache invalidation.
- **Smart Data Loading**: Automatic engine detection for `.csv`, `.parquet`, modern `.xlsx` (openpyxl), and legacy `.xls` (xlrd).
- **Advanced Preprocessing**:
  - Robust encoding (One-Hot) and missing value management.
  - **New**: Scikit-learn integration for data splitting and feature scaling.
- **Performance Visualization**: Standardized reporting for Regression and Classification models.
- **Type-Safe Transformations**: Fully annotated methods for high-reliability pipelines.

## Key Components

### 1. Data Ingestor (`ingestor.py`)

Handles the acquisition phase, ensuring that local data is valid before loading.

```python
from infra.ai_utils.ingestor import DataIngestor
from infra.common.config import RAW_DIR

ingestor = DataIngestor()

# Supports Pathlib and handles CSV, Parquet, and Excel automatically
df = ingestor.get_data(
    local_file_path=RAW_DIR / "dataset.csv",
    file_id="gdrive_file_id_here"
)
```

### 2. Data Processor (`processor.py`)

Centralizes feature engineering and data preparation logic. Now powered by `scikit-learn`.

| Method                        | Description                                                                |
| :---------------------------- | :------------------------------------------------------------------------- |
| `encode_categorical_features` | Performs One-Hot Encoding (returns 0/1 integers).                          |
| `handle_missing_values`       | Drops rows or fills NaNs with specified values.                            |
| `scale_features`              | Applies Standard Scaling (Z-score normalization).                          |
| `split_data`                  | **Static**. Splits data into Train/Test sets with optional stratification. |

**Example Usage:**

```python
from infra.ai_utils.processor import DataProcessor

processor = DataProcessor()

# 1. Clean and Encode
df = processor.handle_missing_values(df, strategy="drop")
df = processor.encode_categorical_features(df, columns=["category_col"])

# 2. Scale Numerical Features
df = processor.scale_features(df, columns=["salary", "age"])

# 3. Split Data (Static Method)
train_x, test_x, train_y, test_y = DataProcessor.split_data(
    x=df.drop("target", axis=1),
    y=df["target"],
    train_size=0.8,
    stratify=df["target"] # Maintains class balance
)
```

### 3. Model Visualizer (`visualizer.py`)

Generates production-ready performance reports with automated timestamping.

| Method                  | Description                                |
| :---------------------- | :----------------------------------------- |
| `save_regression_plot`  | Scatter plot of Real vs. Predicted values. |
| `save_residuals_plot`   | Histogram of errors to check normality.    |
| `save_confusion_matrix` | Heatmap for classification accuracy.       |

```python
import numpy as np
from infra.ai_utils.visualizer import ModelVisualizer
from infra.common.config import REPORTS_DIR

# 1. Regression Analysis
ModelVisualizer.save_regression_plot(
    y_real=y_test,
    y_pred=y_pred,
    output_dir=REPORTS_DIR,
    model_name="Price_Predictor"
)

# 2. Classification Analysis
ModelVisualizer.save_confusion_matrix(
    y_true=y_test_class,
    y_pred=y_pred_class,
    output_dir=REPORTS_DIR,
    labels=["Spam", "Ham"]
)
```

## Testing & Quality

This package follows the global quality gate defined in the project root. To run tests and linting:

```Bash
# From the ai-ops-hub root
make quality
```

______________________________________________________________________

João Pedro | Automation Engineer <br /> [GitHub profile](https://github.com/JoPedro15)
