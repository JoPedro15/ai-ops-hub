# AI Utilities (ai_utils)

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A specialized utility toolkit for the **ai-ops-hub** ecosystem. This package orchestrates data acquisition, local
caching, and feature engineering to provide a seamless bridge between raw data storage and AI model training.

## Features

- **Resilient Data Ingestion**: Managed downloads from GDrive with built-in file health checks and cache invalidation.
- **Smart Excel Loading**: Automatic engine detection for modern `.xlsx` (openpyxl) and legacy `.xls` (xlrd) files.
- **Standardized Preprocessing**: Robust encoding and cleaning methods using `pandas` and `numpy`.
- **Performance Visualization**: Standardized reporting for model evaluation with automated artifact versioning.
- **Type-Safe Transformations**: Fully annotated methods for high-reliability pipelines.

## Key Components

### Data Ingestor

Handles the acquisition phase, ensuring that local data is valid before loading. It reuses the `GDriveService` session for efficiency.

```python
from pathlib import Path
import pandas as pd
from infra.ai_utils.ingestor import DataIngestor
from config import RAW_DIR

ingestor: DataIngestor = DataIngestor()

# Supports Pathlib and handles legacy .xls files automatically
df: pd.DataFrame = ingestor.get_spreadsheet_data(
    local_file_path=RAW_DIR / "dataset.xls",
    file_id="gdrive_file_id_here"
)
```

### Data Processor

Specialized in feature engineering tasks like categorical encoding (with integer output) and missing value management.

```python
import pandas as pd
from infra.ai_utils.processor import DataProcessor

processor: DataProcessor = DataProcessor()

# Safely encode categorical features (returns 0/1 integers for OLS models)
clean_df: pd.DataFrame = processor.encode_categorical_features(
    df=df,
    columns=["category_column"],
    drop_first=True
)
```

### Model Visualizer

Generates production-ready performance reports. It includes automated timestamping and
standardized styling for regression analysis.

## Testing & Quality

```python
from pathlib import Path
import numpy as np
from infra.ai_utils.visualizer import save_regression_plot
from config import REPORTS_DIR

# Generate a standardized performance scatter plot
report_path: str = save_regression_plot(
    y_real=np.array([20000, 25000]),
    y_pred=np.array([19500, 26000]),
    output_dir=REPORTS_DIR,
    model_name="Car_Price_Model"
)
```

This package follows the global quality gate defined in the project root:

```Bash
    # From the ai-ops-hub root
    make quality
```

______________________________________________________________________

João Pedro | Automation Engineer <br /> [GitHub profile](https://github.com/JoPedro15)
