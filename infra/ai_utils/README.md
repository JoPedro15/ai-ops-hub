# 🧠 AI Utilities (ai_utils)

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A specialized utility toolkit for the **Automation Hub** ecosystem. This package orchestrates data acquisition, local
caching, and feature engineering to provide a seamless bridge between raw data storage and AI model training.

## ⚙️ Features

- **Resilient Data Ingestion**: Managed downloads from GDrive with built-in file health checks and cache invalidation.
- **Standardized Preprocessing**: Robust encoding and cleaning methods using `pandas` and `numpy`.
- **Excel Optimized**: Native support for `.xlsx` processing via `openpyxl` engine.
- **Type-Safe Transformations**: Fully annotated methods for high-reliability pipelines.
-

## 🏗 Key Components

### 📥 Data Ingestor

Handles the acquisition phase, ensuring that local data is valid before loading.
It reuses the `GDriveService` session for efficiency.

```python
import pandas as pd
from infra.ai_utils import DataIngestor

ingestor: DataIngestor = DataIngestor()

# Downloads only if cache is missing or corrupted (< 500 bytes)
df: pd.DataFrame = ingestor.get_spreadsheet_data(
    local_file_path="data/raw/dataset.xlsx",
    file_id="gdrive_file_id_here",
    force_download=False
)
```

### 🛠 Data Processor

Specialized in feature engineering tasks like categorical encoding and missing value management.

```python
import pandas as pd
from infra.ai_utils import DataIngestor, DataProcessor

# Initialize both services
ingestor: DataIngestor = DataIngestor()
processor: DataProcessor = DataProcessor()

# Ingest data
df: pd.DataFrame = ingestor.get_spreadsheet_data(
    local_file_path="data/raw/dataset.xlsx",
    file_id="your_gdrive_file_id"
)

# Safely encode categorical features
clean_df: pd.DataFrame = processor.encode_categorical_features(
    df=df,
    columns=["category_column"],
    drop_first=True
)
```

## 📋 API Reference

| Class                 | Method                        | Description                                                     |
| :-------------------- | :---------------------------- | :-------------------------------------------------------------- |
| `DataIngestorClient`  | `get_spreadsheet_data`        | Manages local cache and GDrive downloads with integrity checks. |
| `DataProcessorClient` | `encode_categorical_features` | Performs One-Hot Encoding on specified columns.                 |
| `DataProcessorClient` | `handle_missing_values`       | Provides strategies (drop/fill) for handling NaNs.              |

## 🧪 Testing & Quality

This package follows the global quality gate defined in the project root:

```Bash
    # From the ai-ops-hub root
    make quality
```

______________________________________________________________________

**João Pedro** | Automation Engineer
<br />
[GitHub](https://github.com/JoPedro15) • [Automation Hub](https://github.com/JoPedro15/automation-hub) • [AI Lab](https://github.com/JoPedro15/ai-lab)
<br />
