# Infrastructure Health System

The ai-ops-hub Health System is a dynamic diagnostic suite designed to validate the integrity of the entire
infrastructure—from GDrive connectivity to AI Lab notebook structure—before any production workload begins.

## System Architecture

The system follows a Dynamic Discovery Pattern, where a central orchestrator scans the \`infra.scripts.health_check?
package and executes all modules that adhere to our engineering contract.

| Component        | Path                        | Description                                                           |
| :--------------- | :-------------------------- | --------------------------------------------------------------------- |
| Orchestrator     | `__main__.py`               | Dynamically discovers and runs all `health_check_*.py` modules.       |
| Logger Health    | `health_check_logger.py`    | Validates singleton integrity and ANSI formatting output.             |
| GDrive Health    | `health_check_gdrive.py`    | Checks credentials existence and performs API smoke tests.            |
| Ingestor Health  | `health_check_ingestor.py`  | Verifies cache IO permissions and engine dependencies (openpyxl).     |
| Processor Health | `health_check_processor.py` | Executes smoke tests for One-Hot Encoding and NaN handling.           |
| Lab Health       | `health_check_lab.py`       | Inspects \`.ipynb files for structural integrity and kernel metadata. |

## How It Works

### 1. The Discovery Contract

The orchestrator specifically looks for functions within the modules that follow the **Rigor Protocol**:

- **Module Naming**: Must start with `health_check_`.
- **Function Naming**: Must start with `verify_`.
- **Return Type**: Must return a `bool` (or `tuple[bool, str]` for enhanced reporting).

### 2. Execution Flow

When triggered, the system performs a sequential validation. If any critical component fails
(e.g., GDrive credentials missing), the orchestrator exits with `sys.exit(1)`, preventing unstable
pipelines from running.

## Usage

The Health System is typically invoked via the root Makefile to ensure environment parity.

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

To monitor a new infrastructure component (e.g., a Database or API):

1. Create a new file: `infra/scripts/health_check/health_check_db.py`.
1. Implement the verification logic:

```Python

from infra.common.logger import logger

def verify_database_connectivity() -> bool:
    """
    Check if the production DB is reachable.
    """
    try:
        # Your connection logic here
        logger.success("Database: Connection verified.")
        return True
    except Exception as e:
        logger.error(f"Database: Connection failed | {e}")
        return False
```

## Governance Standards

- **Zero-Print Policy**: Raw `print()` is forbidden during checks. All output must use the Logger service.
- **Type Annotations**: Mandatory for all verification functions to ensure linter compliance.
- **Isolation**: Health checks should not modify production data; only smoke tests or IO permissions should be performed.

______________________________________________________________________

João Pedro | Automation Eng
