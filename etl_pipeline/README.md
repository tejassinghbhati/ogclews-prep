# ETL Pipeline — CLEWS ↔ OG-Core

A declarative, schema-driven data exchange pipeline that transforms outputs from the CLEWS/OSeMOSYS resource systems model into inputs for the OG-Core macroeconomic model, and vice versa. Built as the second component of the **OG–CLEWS** integration project — a Google Summer of Code 2026 initiative under the United Nations Department of Economic and Social Affairs (UN DESA).

This pipeline is the intellectual bridge between two models that currently have no data connection. It is designed to be extended: adding a new variable mapping requires editing a YAML file, not touching Python code.

---

## What this does

- Reads CLEWS output CSVs (capacity, emissions, system costs) organized by region, technology, and year
- Applies filters, aggregations, unit conversions, and scaling transforms defined in a declarative YAML schema
- Validates inputs before transformation and outputs after, using pydantic models
- Writes a clean, JSON-serializable `og_exchange.json` file ready to be passed to the OG-Core runner
- Every step produces structured errors — not raw tracebacks — so failures are actionable

---

## Output

Running the pipeline produces:

```
outputs/
└── og_exchange.json        ← validated OG-Core parameters, ready for update_specifications()
```

The exchange file looks like:

```json
{
  "generated_at": "2026-03-14T11:29:11",
  "source_model": "CLEWS/OSeMOSYS",
  "target_model": "OG-Core",
  "metadata": {
    "data_dir": "data/sample_clews_outputs",
    "schema": "exchange/schema_clews_to_og.yaml"
  },
  "og_parameters": {
    "delta_tau_annual": 0.042,
    "tau_c": 0.019,
    "alpha_G": [0.035]
  }
}
```

---

## Project structure

```
02_etl_pipeline/
├── data/
│   └── sample_clews_outputs/          ← fixture CSVs simulating real CLEWS output
│       ├── TotalCapacityAnnual.csv
│       ├── ProductionByTechnologyAnnual.csv
│       ├── AnnualTechnologyEmission.csv
│       └── TotalDiscountedCost.csv
├── exchange/
│   ├── __init__.py
│   ├── schema_clews_to_og.yaml        ← all variable mappings defined here
│   ├── transformer.py                 ← reads schema, executes transformations
│   ├── validator.py                   ← pydantic validation pre and post transform
│   └── writer.py                      ← writes og_exchange.json
├── tests/
│   ├── test_transformer.py
│   ├── test_validator.py
│   └── test_writer.py
├── conftest.py
├── pyproject.toml
├── requirements.txt
├── run_etl.py                         ← CLI entrypoint
└── README.md
```

---

## Quickstart

### 1. Activate environment

```bash
conda activate ogclews
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the pipeline

```bash
python run_etl.py
```

Expected output:

```
[etl] Step 1: Validating inputs...
  All input files valid.
[etl] Step 2: Running transformations...
  [energy_investment_to_delta_tau] → delta_tau_annual = 0.042
  [co2_emissions_to_tau_c] → tau_c = 0.019
  [system_cost_to_alpha_G] → alpha_G = [0.035]
[etl] Step 3: Validating outputs...
  Validated params: {'delta_tau_annual': 0.042, 'tau_c': 0.019, 'alpha_G': [0.035]}
[etl] Step 4: Writing exchange file...
[writer] Exchange file written to: outputs/og_exchange.json
[etl] Done.
```

### 4. Custom data directory or schema

```bash
python run_etl.py --data-dir path/to/clews/outputs --schema exchange/schema_clews_to_og.yaml --output outputs/og_exchange.json
```

---

## How the schema works

All variable mappings live in `exchange/schema_clews_to_og.yaml`. Each mapping entry defines:

```yaml
- id: "co2_emissions_to_tau_c"
  description: >
    Total CO2 emissions (Mt CO2) mapped to a carbon consumption
    tax proxy (tau_c) in OG-Core.
  source:
    file: "AnnualTechnologyEmission.csv"
    filters:
      EMISSION: ["CO2"]
    aggregate:
      method: "sum"
      group_by: "YEAR"
    column: "VALUE"
  unit_conversion:
    factor: 1.0
  transform:
    method: "linear_scale"
    slope: 0.0005
    intercept: 0.0
  target:
    parameter: "tau_c"
    type: "scalar"
```

To add a new mapping, add a new entry to the YAML file. No Python changes required.

---

## CLEWS variable reference

The fixture CSVs simulate real CLEWS/OSeMOSYS outputs. All files share a consistent column structure:

| File | Key columns | Unit | Description |
|---|---|---|---|
| `TotalCapacityAnnual.csv` | REGION, TECHNOLOGY, YEAR, VALUE | GW | Installed capacity per technology |
| `ProductionByTechnologyAnnual.csv` | REGION, TECHNOLOGY, YEAR, VALUE | PJ | Energy produced per technology |
| `AnnualTechnologyEmission.csv` | REGION, TECHNOLOGY, EMISSION, YEAR, VALUE | Mt CO2 | Emissions per technology |
| `TotalDiscountedCost.csv` | REGION, YEAR, VALUE | MUSD | Total discounted system cost |

---

## OG-Core parameter mappings

| CLEWS variable | Unit | OG-Core parameter | Transformation |
|---|---|---|---|
| `TotalCapacityAnnual` (energy techs, sum) | GW | `delta_tau_annual` | Normalize GW → TW, scale to [0.04, 0.06] |
| `AnnualTechnologyEmission` (CO2, sum) | Mt CO2 | `tau_c` | Linear scale × 0.0005 |
| `TotalDiscountedCost` (sum) | MUSD | `alpha_G` | Normalize, scale to [0.03, 0.08] |

---

## Validation

Validation runs at two stages:

**Pre-transform** — checks that all required CSV files exist and contain the expected columns. Returns a list of human-readable error strings rather than raising immediately, so all problems are reported at once.

**Post-transform** — validates the transformed parameters against a pydantic model (`OGExchangeParams`) that enforces value ranges matching OG-Core's accepted bounds:

| Parameter | Valid range | Error if violated |
|---|---|---|
| `delta_tau_annual` | (0.0, 1.0) | "delta_tau_annual must be between 0 and 1" |
| `tau_c` | ≥ 0.0 | "tau_c must be non-negative" |
| `alpha_G` | each value in [0.0, 1.0] | "alpha_G values must be in [0, 1]" |

---

## Running tests

```bash
pytest tests/ -v
```

---

## Context: OG–CLEWS integration

This pipeline is **Step 2** of a four-component integration plan:

```
[1] OG-Core Runner       ← 01_og_runner/
[2] ETL Pipeline         ← this project
[3] Coupled Orchestrator (run CLEWS → ETL → OG-Core in one workflow)
[4] Converging Module    (iterate until macro + resource outputs stabilize)
```

The `og_exchange.json` produced here feeds directly into the OG-Core runner from Project 1 — passed as `og_spec` overrides to `p.update_specifications()`. That connection is the foundation of the coupled orchestrator in Project 3.

---

## Requirements

```
pandas
numpy
pyyaml
pydantic
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

Built as part of the [MUIOGO](https://github.com/EAPD-DRB/MUIOGO) project under the Economic Analysis and Policy Division (EAPD), United Nations Department of Economic and Social Affairs (UN DESA).