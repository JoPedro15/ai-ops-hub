# Infrastructure Health System

The ai-ops-hub Health System is a high-resiliency diagnostic suite designed to validate the entire infrastructure
stack—from Cloud connectivity to AI Lab structural integrity—before any production workload or model training begins.

## System Architecture

The system implements a **Dynamic Discovery Pattern**. A central orchestrator scans the `infra.scripts.health_check`
package, identifying and executing modules that adhere to our strict engineering contract.

| Component        | Target                      | Integrity Guarantee                                              |
| :--------------- | :-------------------------- | :--------------------------------------------------------------- |
| **Orchestrator** | `__main__.py`               | Zero-configuration discovery & fail-fast execution logic.        |
| **Logger**       | `health_check_logger.py`    | Reliable audit trail, singleton integrity, and ANSI compliance.  |
| **GDrive**       | `health_check_gdrive.py`    | OAuth2 handshake, credential validity, and API reachability.     |
| **Ingestor**     | `health_check_ingestor.py`  | Local Cache I/O permissions and engine stability (`openpyxl`).   |
| **Processor**    | `health_check_processor.py` | Mathematical logic validation (NaN handling & One-Hot Encoding). |
| **Lab**          | `health_check_lab.py`       | Notebook JSON integrity and Jupyter Kernel metadata alignment.   |

## How It Works

### 1. The Discovery Contract

The orchestrator filters modules and functions based on the **Rigor Protocol**:

- **Module Naming**: Must follow the `health_check_*.py` convention.
- **Function Naming**: Must start with `verify_` (e.g., `verify_service_status`).
- **Return Type**: Mandatory `bool` return for binary pass/fail state.
- **Interface**: Exposed via `__all__` for clean namespace management.

### 2. Execution Flow & Fail-Fast

The system performs a sequential validation. If a critical failure is detected, the orchestrator triggers an
immediate shutdown of the pipeline to prevent data corruption or unstable training sessions.

### 🚦 Diagnostic Exit Codes

- **`0`**: All checks passed. System is nominal and ready for production.
- **`1`**: Critical failure detected. Pipeline execution is blocked.

## Usage

The Health System is integrated into the root **Makefile** to ensure parity between local development
and CI/CD environments.

```Bash
# Run the full suite of diagnostics
make health
```

### Manual Execution

If you need to run the orchestrator directly for debugging:

```Bash

python3 -m infra.scripts.health_check
```

## Adding New Checks

To monitor a new component (e.g., Database or External API), follow the established **Automation Standard**:

1. Create \`infra/scripts/health_check/health_check_db.py.

1. Implement the logic with full type safety:

```Python

from infra.common.logger import logger

__all__: list[str] = ["verify_database_connectivity"]

def verify_database_connectivity() -> bool:
    """
    Check if the production database is reachable and authenticated.
    """
    try:
        # Connection logic here
        logger.success("Database: Connection verified.")
        return True
    except Exception as e:
        logger.error(f"Database: Connection failed | {str(e)}")
        return False
```

## Governance Standards

- **Zero-Print Policy**: Raw `print()` is strictly forbidden. All diagnostics must use the `infra.common.logger service`.
- **Type Annotations**: Mandatory for all verification functions to ensure linter (Ruff) compliance.
- **Isolation**: Health checks must be non-destructive. They perform smoke tests or I/O permission checks without modifying production data.

______________________________________________________________________

João Pedro | Automation Engineer <br /> [GitHub profile](https://github.com/JoPedro15)
