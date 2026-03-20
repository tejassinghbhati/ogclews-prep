# Validation Framework

A standalone Python validation framework for **OG-Core** and **CLEWS** model inputs. It provides schema validation (via Pydantic), physical file-system checks, and formatted output suitable for terminals, REST APIs, and log files.

---

## Project Structure

```
Validation_framework/
├── validator/
│   ├── __init__.py          # Public re-exports
│   ├── models.py            # Pydantic models + result dataclasses
│   ├── file_validator.py    # File existence & CSV structure checks
│   ├── schema_validator.py  # Config-dict validation against Pydantic models
│   └── error_formatter.py   # Terminal / UI / log formatters
├── schemas/
│   ├── og_input_schema.yaml    # Human-readable OG-Core field docs
│   └── clews_input_schema.yaml # Human-readable CLEWS field docs
├── sample_data/
│   ├── valid_og_config.json    # Passes all validation checks
│   └── invalid_og_config.json  # Deliberate errors (maxiter, nu, missing start_year)
├── tests/
│   ├── test_file_validator.py
│   ├── test_schema_validator.py
│   └── test_error_formatter.py
├── conftest.py       # Shared pytest fixtures
├── pyproject.toml    # Build & pytest config (pythonpath = ["."])
├── requirements.txt  # Runtime + dev dependencies
├── run_validation.py # CLI entrypoint
└── README.md
```

---

## Installation

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

---

## Quick Start

### Validate an OG-Core config

```bash
# Terminal output (coloured)
python run_validation.py --model og --config sample_data/valid_og_config.json

# JSON output (for API consumers)
python run_validation.py --model og --config sample_data/invalid_og_config.json --output-format ui

# Log-friendly flat string
python run_validation.py --model og --config sample_data/invalid_og_config.json --output-format log
```

### Validate a CLEWS config and check data files

```bash
python run_validation.py \
    --model clews \
    --config my_clews_config.json \
    --data-dir ./data/clews_outputs \
    --required-files TotalCapacityAnnual.csv ProductionByTechnologyAnnual.csv
```

### Exit codes

| Code | Meaning |
|------|---------|
| `0`  | All checks passed |
| `1`  | One or more validation errors |
| `2`  | Argument / I/O error (bad path, invalid JSON) |

---

## Python API

Every public function **never raises** — it always returns a `ValidationResult`.

### File validation

```python
from validator.file_validator import check_files_exist, check_csv_columns

result = check_files_exist("./data", ["TotalCapacityAnnual.csv"])
if not result.passed:
    for err in result.errors:
        print(err.field, err.message)
```

### Schema validation

```python
from validator.schema_validator import validate_og_config

result = validate_og_config({"scenario_name": "test", ...})
print(result.passed)     # True / False
print(result.to_dict())  # JSON-serialisable
```

### Exchange parameter validation (ETL output)

```python
from validator.schema_validator import validate_exchange_params

result = validate_exchange_params({
    "delta_tau_annual": 0.05,
    "tau_c": 0.25,
    "alpha_G": [0.3, 0.7],
})
```

### Formatting output

```python
from validator.error_formatter import format_for_terminal, format_for_ui, format_for_log

print(format_for_terminal(result))  # Coloured terminal string
ui_dict = format_for_ui(result)     # JSON-serialisable dict for Flask
log_str = format_for_log(result)    # Flat string for log files
```

---

## Data Models

### `OGInputConfig`

| Field | Type | Constraints | Description |
|---|---|---|---|
| `scenario_name` | `str` | required | Unique run label |
| `country_module` | `str` | required | Python import path |
| `time_path` | `bool` | required | Compute TPI? |
| `start_year` | `int` | 2020–2100 | Simulation start |
| `og_spec.maxiter` | `int` | 1–1000 | Max solver iterations |
| `og_spec.mindist_SS` | `float` | 1e-12–1.0 | SS convergence criterion |
| `og_spec.nu` | `float` | 0.0–1.0 | TPI update coefficient |

### `CLEWSInputConfig`

| Field | Type | Constraints | Description |
|---|---|---|---|
| `data_dir` | `Path` | required | CLEWS output directory |
| `required_files` | `list[str]` | optional | Files that must exist |
| `region` | `str` | required | Region identifier |
| `start_year` | `int` | 2020–2100 | Simulation start |
| `end_year` | `int` | >= start_year | Simulation end |

---

## Running Tests

```bash
pytest -v
```

All tests use `tmp_path` fixtures (no external dependencies required) and cover:
- Missing files → correct `stage` and `field` in errors
- Out-of-range values → field name in error messages
- `format_for_ui` → fully JSON-serialisable output
- Exchange params → `tau_c`, `delta_tau_annual`, `alpha_G` business-logic checks

---

## Design Principles

1. **Never raise** — all validator functions catch exceptions and return `ValidationResult`.
2. **Stage tagging** — every `ValidationError` carries a `stage` field (`"file_check"`, `"schema"`, `"exchange"`).
3. **JSON-safe UI output** — `format_for_ui` guarantees `json.dumps` won't fail.
4. **Extensible** — add new Pydantic models + a validator function to cover new model types.
