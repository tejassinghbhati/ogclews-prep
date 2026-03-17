# OG-Core Runner

A standalone Python runner for the [OG-Core](https://github.com/PSLmodels/OG-Core) overlapping-generations macroeconomic model. Built as part of the **OG–CLEWS** integration project — a Google Summer of Code 2026 initiative under the United Nations Department of Economic and Social Affairs (UN DESA) to link OG-Core with the CLEWS (Climate, Land, Energy, Water Systems) framework into a unified policy modelling tool.

This runner is the first component of the broader [MUIOGO](https://github.com/EAPD-DRB/MUIOGO) platform.

---

## What this does

- Takes a YAML config file as input
- Runs OG-Core programmatically (no CLI required)
- Captures all solver output (stdout + stderr) to a structured log file
- Writes outputs to a standardized directory tree with a run ID
- Extracts key macro aggregates from OG-Core's `.pkl` outputs into a clean `summary.csv` — ready for ETL into CLEWS

---

## Output structure

Every run produces a self-contained folder under `outputs/`:

```
outputs/
└── {run_id}/
    ├── metadata.json          # run config, status, timestamps
    ├── results/
    │   ├── OUTPUT_BASELINE/
    │   │   └── SS/
    │   │       └── SS_vars.pkl    # OG-Core steady-state solution
    │   └── summary.csv            # ETL-ready macro aggregates
    └── logs/
        └── run.log                # full solver output
```

---

## Project structure

```
og_runner/
├── configs/
│   └── example_config.yaml    # example run configuration
├── outputs/                   # generated outputs (gitignored)
├── runner/
│   ├── __init__.py
│   ├── config_loader.py       # YAML → RunConfig dataclass
│   ├── og_runner.py           # core runner: builds params, calls execute.runner()
│   ├── log_capture.py         # tee stdout/stderr to log file
│   ├── output_writer.py       # directory scaffold + metadata.json management
│   └── summary_extractor.py   # unpickles SS/TPI vars → summary.csv
├── tests/
│   ├── test_config_loader.py
│   ├── test_output_writer.py
│   └── test_summary_extractor.py
├── conftest.py
├── pyproject.toml
├── requirements.txt
└── run.py                     # CLI entrypoint
```

---

## Quickstart

### 1. Create and activate environment

```bash
conda create -n ogclews python=3.11
conda activate ogclews
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your run

Edit `configs/example_config.yaml`:

```yaml
run:
  scenario_name: "baseline_phl"
  country_module: ""        # leave empty for OG-Core defaults, or e.g. "ogphl"
  time_path: false          # false = steady-state only (faster)
  start_year: 2026

og_spec:                    # passed directly to p.update_specifications()
  maxiter: 100
  mindist_SS: 1.0e-3
  nu: 0.4

output:
  base_dir: "outputs"
```

### 4. Run

```bash
# Steady-state only (fast, ~60 seconds)
python run.py configs/example_config.yaml --no-tpi

# Full run including transition path
python run.py configs/example_config.yaml
```

### 5. Check outputs

```bash
# View extracted macro aggregates
type outputs\{run_id}\results\summary.csv

# View run metadata
type outputs\{run_id}\metadata.json
```

---

## Configuration reference

### `run` block

| Field | Type | Description |
|---|---|---|
| `scenario_name` | string | Human-readable label for this run |
| `country_module` | string | Pip-installed country calibration package (e.g. `ogphl`, `ogzaf`). Leave empty for OG-Core defaults. |
| `time_path` | bool | If `true`, solves the full transition path (TPI) in addition to steady state |
| `start_year` | int | Base year for the simulation |

### `og_spec` block

Any valid OG-Core `Specifications` parameter. Passed directly to `p.update_specifications()`. Key parameters for solver tuning:

| Field | Default | Description |
|---|---|---|
| `maxiter` | 400 | Max outer GE loop iterations |
| `mindist_SS` | 1e-9 | Steady-state convergence tolerance |
| `nu` | 0.4 | Dampening parameter (lower = more stable, slower) |

For the full parameter reference see the [OG-Core parameter docs](https://pslmodels.github.io/OG-Core/content/intro/parameters.html).

---

## Running tests

```bash
pytest tests/ -v
```

All three tests should pass without a full OG-Core solve — they test config loading, directory scaffolding, and the numpy serialization logic independently.

```
tests/test_config_loader.py::test_load_config_returns_run_id   PASSED
tests/test_output_writer.py::test_metadata_written              PASSED
tests/test_summary_extractor.py::test_to_scalar_numpy           PASSED
```

---

## How it works

### Config loading (`config_loader.py`)

Reads the YAML file and returns a `RunConfig` dataclass. Each run gets a unique `run_id` generated from the current timestamp + a random hex suffix (e.g. `20260314_112911_7f32eb`), ensuring outputs never collide.

### Parameter building (`og_runner.py`)

Instantiates `ogcore.parameters.Specifications` with the output path, optionally loads a country calibration via `importlib`, then applies `og_spec` overrides via `p.update_specifications()`. The country calibration (if provided) is applied first so that scenario overrides always win.

### Log capture (`log_capture.py`)

A context manager that replaces `sys.stdout` and `sys.stderr` with `TeeStream` objects. All OG-Core solver output is written to `logs/run.log` while simultaneously printing to the terminal — so you see progress live and have a permanent record.

### Output writing (`output_writer.py`)

Creates the `outputs/{run_id}/` directory tree before the run starts and writes `metadata.json` with status `"running"`. On completion (or failure), updates the metadata with final status, results path, and any error traceback.

### Summary extraction (`summary_extractor.py`)

Unpickles `SS_vars.pkl` (and `TPI_vars.pkl` if present) and extracts key macro aggregates — GDP, capital, labour, consumption, interest rate, wages, transfers — into `summary.csv`. TPI variables are stored as 10-year paths. This CSV is the intended input for the ETL pipeline that feeds CLEWS in the coupled OG–CLEWS workflow.

---

## Macro variables extracted to `summary.csv`

| Variable | Source | Description |
|---|---|---|
| `Y_ss` | SS | Steady-state GDP |
| `K_ss` | SS | Steady-state capital stock |
| `L_ss` | SS | Steady-state labour |
| `C_ss` | SS | Steady-state consumption |
| `r_ss` | SS | Steady-state interest rate |
| `w_ss` | SS | Steady-state wage |
| `T_H_ss` | SS | Steady-state household transfers |
| `TR_ss` | SS | Steady-state total transfers |
| `Y_path` | TPI | GDP transition path (first 10 years) |
| `w_path` | TPI | Wage transition path (first 10 years) |
| `r_path` | TPI | Interest rate path (first 10 years) |

---

## Context: OG–CLEWS integration

This runner is **Step 1** of a four-component integration plan:

```
[1] OG-Core Runner       ← this repo
[2] ETL Pipeline         (CLEWS outputs → OG-Core inputs, and vice versa)
[3] Coupled Orchestrator (run CLEWS → ETL → OG-Core in one workflow)
[4] Converging Module    (iterate until macro + resource outputs stabilize)
```

The `summary.csv` produced here feeds directly into Step 2 — the ETL pipeline that transforms OG-Core macro outputs into CLEWS demand and investment scenario parameters.

---

## Requirements

```
ogcore
pyyaml
numpy
pytest
```

Install with:

```bash
pip install -r requirements.txt
```

---

## License

Apache License 2.0 — consistent with the MUIOGO and OG-Core projects.

---

## Acknowledgements

Built as part of the [MUIOGO](https://github.com/EAPD-DRB/MUIOGO) project under the Economic Analysis and Policy Division (EAPD), United Nations Department of Economic and Social Affairs (UN DESA). OG-Core is developed and maintained by [PSLmodels](https://github.com/PSLmodels/OG-Core).