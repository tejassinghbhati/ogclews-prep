# GSoC 2026 — OG-CLEWS Preparation

> **Contributor 1 — Scientific Programming & Model Integration**
> United Nations Office of Information and Communications Technology (UN OICT)
> Economic Analysis and Policy Division (EAPD), UN Department of Economic and Social Affairs (UN DESA)

This repository documents my preparation work for the **OG–CLEWS** integration project under Google Summer of Code 2026. It contains six self-contained projects that demonstrate readiness to deliver the Contributor 1 scope — scientific programming, model integration, ETL pipeline design, validation, convergence logic, and API backend extension.

Every project here was built before the application deadline — not because it was required, but because I wanted to understand the problem before claiming I could solve it.

---

## What is OG-CLEWS?

**OG-CLEWS** integrates two mature, widely-used open-source policy modelling frameworks that currently operate as entirely separate tools:

**CLEWS** (Climate, Land, Energy, Water Systems), built on **OSeMOSYS** (Open Source Energy Modelling System), models the physical interactions among land use, the energy sector, and water systems under climate change scenarios. It answers questions like: *Does Mauritius have enough land and water to implement a biofuel policy? What happens to the energy system if rainfall drops by 20%?*

**OG-Core** is an overlapping-generations macroeconomic model that enables dynamic general equilibrium analysis of fiscal, demographic, and economic policies over the long term. It answers questions like: *How does a carbon tax affect GDP growth over the next 30 years? What happens to wages and interest rates if the government increases energy infrastructure investment?*

Neither model can answer both questions. Together, they can. The OG-CLEWS project creates a standardized, automated interface between them — a shared execution layer, an ETL data bridge, and a unified user interface — enabling integrated analyses that are not currently possible with any existing tool.

This integration will be deployed in more than **10 target countries** under a USD 2 million programme through 2030, including Small Island Developing States, Land-Locked Countries, and Least Developed Countries that are disproportionately exposed to climate risk and least equipped with proprietary modelling infrastructure.

---

## Repository Overview

```
ogclews-prep/
├── 01_og_runner/                ✅ OG-Core standalone runner
├── 02_etl_pipeline/             ✅ CLEWS → OG-Core data exchange pipeline
├── 03_validation_framework/     ✅ Schema validation for pipeline inputs/outputs
├── 04_convergence_prototype/    ✅ Iterative coupled model convergence logic
├── 05_ogcore_api/               ✅ Flask API endpoints for MUIOGO backend
├── 06_country_scenario/         ✅ End-to-end Mauritius worked example
└── README.md                 ← this file
```

---

## Projects

| # | Project | Status | Hours | Description |
|---|---|---|---|---|
| 01 | [OG-Core Runner](#01-og-core-runner) | ✅ Complete | ~15h | Standalone programmatic runner with structured output, log capture, and metadata |
| 02 | [ETL Pipeline](#02-etl-pipeline) | ✅ Complete | ~20h | CLEWS → OG-Core schema-driven data exchange pipeline with pydantic validation |
| 03 | [Validation Framework](#03-validation-framework) | ✅ Complete | ~12h | Pre/post-run schema validation with structured UI-ready error messages |
| 04 | [Convergence Prototype](#04-convergence-prototype) | ✅ Complete | ~18h | Iterative coupled model loop with L2 norm convergence and full logging |
| 05 | [Flask API Endpoints](#05-flask-api-endpoints) | ✅ Complete | ~14h | OG-Core run/status/results endpoints mirroring MUIOGO's existing API pattern |
| 06 | [Country Scenario](#06-country-scenario) | ✅ Complete | ~16h | End-to-end Mauritius renewable transition scenario with 3 executed notebooks |

---

## 01 — OG-Core Runner

**Path:** `og_runner/`
**Why it matters:** The mentors need to see that I understand how OG-Core executes internally — not just that I have read the documentation. This runner proves I can wire OG-Core into MUIOGO's backend programmatically.

### What it does

- Takes a `YAML` config file as input — scenario name, parameters, output directory
- Runs OG-Core programmatically via `ogcore.execute.runner()` and `p.update_specifications()`
- Captures all stdout/stderr to a structured log file in real time
- Writes all outputs to a standardised directory structure:

```
outputs/{run_id}/
    results/          ← OG-Core output files
    logs/
    │   └── ogcore_run.log
    └── metadata.json ← timestamp, parameters used, run status, output paths
```

- `metadata.json` records every parameter used, the run timestamp, final status (`completed` / `failed`), and file paths — making every run fully reproducible and auditable

### File structure

```
01_og_runner/
├── runner/
│   ├── __init__.py
│   ├── config_loader.py     ← reads YAML, returns RunConfig dataclass
│   └── og_runner.py         ← programmatic OG-Core execution wrapper
├── configs/
│   └── sample_config.yaml   ← sample scenario configuration
├── outputs/                 ← auto-created on first run
├── run_og.py                ← CLI entry point
├── requirements.txt
└── README.md
```

### Sample config

```yaml
run_id: mauritius_baseline
scenario: renewable_transition_2035
ogcore_params:
  gdp_growth: 0.038
  capital_share: 0.38
  labor_share: 0.62
output_dir: outputs/
```

### Sample log output

```
2026-03-14 11:29:00  INFO     OG-Core Run — mauritius_baseline
2026-03-14 11:29:00  INFO     Loading specifications...
2026-03-14 11:29:01  INFO     Applying parameter overrides: {'gdp_growth': 0.038, ...}
2026-03-14 11:29:01  INFO     Running steady-state solver...
2026-03-14 11:29:45  INFO     SS solved. Running TPI...
2026-03-14 11:31:12  INFO     TPI converged. Writing outputs...
2026-03-14 11:31:13  INFO     Run complete — status: COMPLETED
```

### Sample metadata.json

```json
{
  "run_id": "mauritius_baseline",
  "status": "completed",
  "timestamp": "2026-03-14T11:31:13",
  "parameters": { "gdp_growth": 0.038, "capital_share": 0.38 },
  "output_dirs": {
    "results": "outputs/mauritius_baseline/results/",
    "logs": "outputs/mauritius_baseline/logs/",
    "metadata": "outputs/mauritius_baseline/metadata.json"
  }
}
```

---

## 02 — ETL Pipeline

**Path:** `etl_pipeline/`
**Why it matters:** This is the most critical deliverable of Contributor 1's scope. The ETL pipeline is the intellectual bridge between two models that currently have no data connection. Building even a partial version before GSoC is the single biggest differentiator.

### What it does

- Reads CLEWS/OSeMOSYS output CSVs: capacity, emissions, production, system costs
- Applies filters, aggregations, unit conversions, and scaling transforms — all defined in a **declarative YAML schema**, not hardcoded in Python
- Validates inputs before transformation and outputs after, using `pydantic` models
- Writes a clean, JSON-serializable `og_exchange.json` file ready to be passed to the OG-Core runner
- Every step produces structured, human-readable errors — not raw Python tracebacks

### The key design decision: schema-driven

All variable mappings live in `schema_clews_to_og.yaml`. Adding a new variable mapping requires editing the YAML file only — no Python changes required. This is critical for the GSoC project because the exact mappings will evolve with mentor feedback and country-specific calibration.

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

### CLEWS variable mappings

| CLEWS File | Variable | Unit | OG-Core Parameter | Transformation |
|---|---|---|---|---|
| `TotalCapacityAnnual.csv` | Energy tech capacity sum | GW | `delta_tau_annual` | GW → TW, normalize [0.04, 0.06] |
| `AnnualTechnologyEmission.csv` | CO2 total | Mt CO2 | `tau_c` | Linear scale × 0.0005 |
| `TotalDiscountedCost.csv` | System cost sum | MUSD | `alpha_G` | Cost/GDP, normalize [0.03, 0.08] |

### Validation

Runs at two stages with pydantic:

**Pre-transform:** checks all required CSV files exist and contain expected columns. Returns a complete list of all errors at once — not just the first one.

**Post-transform:** validates transformed parameters against `OGExchangeParams` with enforced value ranges matching OG-Core's accepted bounds.

| Parameter | Valid range | Error if violated |
|---|---|---|
| `delta_tau_annual` | (0.0, 1.0) | "delta_tau_annual must be between 0 and 1" |
| `tau_c` | ≥ 0.0 | "tau_c must be non-negative" |
| `alpha_G` | each in [0.0, 1.0] | "alpha_G values must be in [0, 1]" |

### Sample output

```json
{
  "generated_at": "2026-03-14T11:29:11",
  "source_model": "CLEWS/OSeMOSYS",
  "target_model": "OG-Core",
  "og_parameters": {
    "delta_tau_annual": 0.042,
    "tau_c": 0.019,
    "alpha_G": [0.035]
  }
}
```

### File structure

```
02_etl_pipeline/
├── data/
│   └── sample_clews_outputs/
│       ├── TotalCapacityAnnual.csv
│       ├── ProductionByTechnologyAnnual.csv
│       ├── AnnualTechnologyEmission.csv
│       └── TotalDiscountedCost.csv
├── exchange/
│   ├── __init__.py
│   ├── schema_clews_to_og.yaml    ← all variable mappings
│   ├── transformer.py             ← reads schema, executes transforms
│   ├── validator.py               ← pydantic pre/post validation
│   └── writer.py                  ← writes og_exchange.json
├── outputs/
│   └── og_exchange.json
├── tests/
│   ├── test_transformer.py
│   ├── test_validator.py
│   └── test_writer.py
├── conftest.py
├── run_etl.py                     ← CLI entry point
├── requirements.txt
└── README.md
```

---

## 03 — Validation Framework

**Path:** `validation_framework/`
**Why it matters:** The proposal explicitly mentions *"validation checks that confirm required inputs exist at each step."* Showing this is already prototyped demonstrates I have thought through production-readiness, not just the happy path.

### What it does

- Checks required files exist before any model run — fails fast with a human-readable list of all missing files
- Validates input data types and value ranges against a defined schema using `pydantic` and `jsonschema`
- Returns structured error objects suitable for direct display in a UI — not raw Python exceptions
- Runs as a standalone module that can validate CLEWS inputs, OG-Core inputs, or ETL exchange files independently

### Error format

All errors are returned as structured objects, not string messages:

```json
{
  "stage": "pre_transform",
  "errors": [
    {
      "file": "AnnualTechnologyEmission.csv",
      "error": "Required column 'EMISSION' not found",
      "severity": "error"
    },
    {
      "file": "TotalCapacityAnnual.csv",
      "error": "Column VALUE contains 3 negative entries",
      "severity": "warning"
    }
  ],
  "passed": false
}
```

### File structure

```
03_validation_framework/
├── validation/
│   ├── __init__.py
│   ├── input_validator.py     ← file existence and column checks
│   ├── schema_validator.py    ← pydantic/jsonschema value validation
│   └── error_formatter.py     ← structures errors for UI consumption
├── schemas/
│   ├── clews_input.yaml       ← expected CLEWS CSV schemas
│   └── og_exchange.yaml       ← expected ETL output schema
├── tests/
├── run_validation.py          ← CLI entry point
├── requirements.txt
└── README.md
```

---

## 04 — Convergence Prototype

**Path:** `convergence_prototype/`
**Why it matters:** The converging module is the hardest part of the entire GSoC project. Demonstrating a working prototype — even with mocked models — shows I have already thought through the architecture before the programme even starts.

### What it does

- Runs CLEWS (mocked) with current macroeconomic parameters from OG-Core
- Transforms CLEWS outputs into OG-Core inputs via the ETL mapping
- Runs OG-Core (mocked) with transformed inputs
- Computes the **L2 norm** (Euclidean distance) between successive parameter vectors as the convergence metric
- Stops when `delta < threshold` (default: `1e-4`) or max iterations reached
- Logs every iteration's state — inputs, outputs, delta, per-variable breakdown
- Writes `history.json` and `metadata.json` to a timestamped output directory

### Convergence metric

```python
delta = || params_curr - params_prev ||_2
```

When this value falls below the threshold, CLEWS and OG-Core have reached a mutually consistent solution — neither model's outputs would meaningfully change if you ran the loop again.

### Verified convergence

Running the prototype on Mauritius-calibrated initial parameters:

```
── Iteration 1 ─────────────  delta: 0.00502462
── Iteration 2 ─────────────  delta: 0.00353595
── Iteration 3 ─────────────  delta: 0.00345511
── Iteration 4 ─────────────  delta: 0.00340486
── Iteration 5 ─────────────  delta: 0.00338363
── Iteration 6 ─────────────  delta: 0.00192847
── Iteration 7 ─────────────  delta: 0.00006586

✓ Converged at iteration 7  (delta=6.59e-05 < 1.00e-04)
```

### From mock to production

The mock runners are clearly isolated in their own modules. Replacing them requires only:
1. Replace `mock_clews.run_clews()` with the real OSeMOSYS/CLEWS runner
2. Replace `mock_ogcore.run_ogcore()` with a call to `ogcore.execute.runner()`
3. Wire in the ETL pipeline from `etl_pipeline/` for the transform steps

The orchestrator, metrics, and output structure remain unchanged.

### File structure

```
04_convergence_prototype/
├── convergence/
│   ├── __init__.py
│   ├── mock_clews.py          ← mock CLEWS runner (clearly labeled)
│   ├── mock_ogcore.py         ← mock OG-Core runner (clearly labeled)
│   ├── metrics.py             ← L2 norm + per-variable delta
│   └── orchestrator.py        ← iterative coupling loop
├── outputs/
│   └── {run_id}/
│       ├── convergence.log
│       ├── history.json
│       └── metadata.json
├── run_convergence.py         ← CLI entry point
├── requirements.txt
└── README.md
```

### CLI usage

```bash
# Default run
python run_convergence.py

# Custom threshold and max iterations
python run_convergence.py --threshold 1e-5 --max-iterations 30

# Custom output directory
python run_convergence.py --output-dir runs/mauritius/
```

---

## 05 — Flask API Endpoints

**Path:** `ogcore_api/`
**Why it matters:** MUIOGO's backend is Flask-based. The GSoC deliverable requires OG-Core to be triggerable from the frontend UI. This project extends the existing API with a new Blueprint — following MUIOGO's exact patterns — without touching any existing files.

### What it does

Adds five new endpoints to MUIOGO's Flask backend, mirroring the structure of `CaseRoute.py`:

| Endpoint | Method | Description |
|---|---|---|
| `/ogcore/run` | POST | Trigger an OG-Core run (non-blocking background thread) |
| `/ogcore/status/<run_id>` | GET | Poll run status: `running` / `completed` / `failed` |
| `/ogcore/results/<run_id>` | GET | Return output file paths and macroeconomic results |
| `/ogcore/runs` | POST | List all OG-Core runs for the active case session |
| `/ogcore/run/<run_id>` | DELETE | Delete a run's output directory |

### Design principles — mirrors CaseRoute.py exactly

| MUIOGO convention | This implementation |
|---|---|
| `Blueprint('CaseRoute', __name__)` | `Blueprint('OGCoreRoute', __name__)` |
| `{"message": "...", "status_code": "success"}` | Same exact response format |
| `try/except(IOError)` error handling | Same pattern throughout |
| `session.get('osycase')` for auth | Same session validation |
| `Config.DATA_STORAGE` path management | Same path resolution |
| `res/{run_name}/` output structure | `res/ogcore_{run_id}/` same layout |

### Integration

Drop-in addition — does not modify any existing MUIOGO files. Only two lines added to `app.py`:

```python
from Routes.OGCore.OGCoreRoute import ogcore_api
app.register_blueprint(ogcore_api)
```

### Sample run request and response

**POST `/ogcore/run`**
```json
// Request
{
  "casename": "Mauritius_NDC",
  "ogcore_params": {
    "gdp_growth": 0.038,
    "capital_share": 0.38,
    "labor_share": 0.62
  }
}

// Response (immediate — run dispatched to background thread)
{
  "message": "OG-Core run <b>ogcore_20260314_113000</b> started!",
  "status_code": "running",
  "run_id": "ogcore_20260314_113000"
}
```

**GET `/ogcore/results/ogcore_20260314_113000`**
```json
{
  "run_id": "ogcore_20260314_113000",
  "status": "completed",
  "results": {
    "macro_aggregates": {
      "GDP_growth": 0.0406,
      "investment_share": 0.1235,
      "consumption_share": 0.8344
    },
    "factor_prices": {
      "wage_rate": 1.065,
      "interest_rate": 0.0408
    },
    "fiscal": {
      "tax_revenue_pct_gdp": 0.216
    }
  },
  "status_code": "success"
}
```

### File structure

```
05_ogcore_api/
├── API/
│   ├── app_patch.py                    ← two lines to add to app.py
│   ├── Routes/
│   │   └── OGCore/
│   │       ├── __init__.py
│   │       └── OGCoreRoute.py          ← Blueprint with 5 endpoints
│   └── Classes/
│       └── OGCore/
│           ├── __init__.py
│           └── OGCoreRunner.py         ← programmatic OG-Core runner class
└── README.md
```

---

## 06 — Country Scenario

**Path:** `country_scenario/`
**Why it matters:** A worked example for a real country is the difference between a proposal that describes a solution and one that demonstrates it. This scenario traces the full OG-CLEWS workflow from CLEWS outputs to macroeconomic results — documented, executed, and interpretable.

### Country: Republic of Mauritius

Mauritius was selected because it is one of the earliest documented CLEWS implementations by KTH and UN DESA, it is a Small Island Developing State (exactly the primary target of the OG-CLEWS deployment), and all required data is publicly available. Its 2015 NDC commits to 35% renewable electricity by 2025 and 60% by 2030 — a clear, tractable policy scenario to model.

### Scenario: Renewable Energy Transition 2020–2035

Technologies modelled:

| Code | Technology | Role in scenario |
|---|---|---|
| `SOLAR_PV` | Utility-scale solar PV | Scales from 0.12 GW to 2.20 GW (+18×) |
| `WIND_ONSHORE` | Onshore wind | Scales from 0.05 GW to 0.86 GW (+17×) |
| `BAGASSE_CHP` | Sugarcane bagasse CHP | Stable baseload — uniquely Mauritian |
| `DIESEL_OPEN_CYCLE` | Open-cycle diesel | Phased out: 0.48 GW → 0.08 GW (−83%) |
| `HYDRO_RUN` | Run-of-river hydro | Stable at 0.06 GW |

### The three notebooks

**`01_clews_output_exploration.ipynb`** — loads all four CLEWS CSVs, generates 4 charts (capacity trends, production mix, CO2 trajectory, system cost curve), and summarises the key statistics at the CLEWS output boundary.

**`02_etl_trace.ipynb`** — runs the ETL pipeline step by step on the Mauritius data. Every transformation is shown: input value, method, output value, and why the mapping makes economic sense. Produces `og_exchange.json`.

**`03_ogcore_scenario.ipynb`** — takes `og_exchange.json`, shows what OG-Core receives at its input boundary, runs the macroeconomic scenario calibrated to Mauritius's 2020 baseline, and interprets results against IMF/World Bank data.

### ETL trace — Mauritius

| CLEWS Output | Input Value | Method | OG-Core Parameter | Output Value |
|---|---|---|---|---|
| Energy capacity (Solar+Wind+Bagasse, mean) | 0.001833 TW | Normalize [0.04, 0.06] | `delta_tau_annual` | 0.045922 |
| CO2 emissions (mean annual) | 1.250 Mt | × 0.0005 | `tau_c` | 0.000625 |
| Total discounted cost / GDP proxy | 0.02439 | Normalize [0.03, 0.08] | `alpha_G` | 0.042193 |

### OG-Core results — Mauritius

| Indicator | Baseline | Renewable Transition | Delta |
|---|---|---|---|
| GDP Growth Rate | 3.80% | 4.06% | **▲ +0.26pp** |
| Capital Share of Output | 0.380 | 0.386 | ▲ +0.006 |
| Wage Index (2020 = 1) | 1.000 | 1.065 | **▲ +6.5%** |
| Real Interest Rate | 4.20% | 4.08% | ▼ −0.12pp |
| Tax Revenue (% GDP) | 19.2% | 21.6% | **▲ +2.4pp** |
| CO2 Emissions (2035) | — | 0.547 Mt | ▼ −83% vs 2020 |

**What this tells a policymaker:** Mauritius's renewable energy transition is not just physically feasible — CLEWS confirms land, water, and energy resource constraints can be met. It is also macroeconomically beneficial. The capital deepening from sustained renewable investment lifts long-run GDP growth by 0.26 percentage points, wages rise 6.5% above baseline, and the expanding tax base raises fiscal revenues by 2.4 percentage points of GDP. This is precisely the integrated insight that neither model can produce independently — and exactly what OG-CLEWS enables.

### File structure

```
06_country_scenario/
├── data/
│   ├── clews_outputs/
│   │   ├── TotalCapacityAnnual.csv
│   │   ├── ProductionByTechnologyAnnual.csv
│   │   ├── AnnualTechnologyEmission.csv
│   │   └── TotalDiscountedCost.csv
│   ├── og_inputs/
│   │   └── og_exchange.json           ← computed by ETL pipeline
│   └── sources.md                     ← full data provenance
├── notebooks/
│   ├── 01_clews_output_exploration.ipynb
│   ├── 02_etl_trace.ipynb
│   └── 03_ogcore_scenario.ipynb
├── outputs/
│   ├── og_results.json
│   ├── workflow_summary.md
│   ├── fig1_capacity.png
│   ├── fig2_production_mix.png
│   ├── fig3_emissions.png
│   ├── fig4_system_cost.png
│   ├── fig5_co2_to_tauc.png
│   └── fig6_ogcore_results.png
├── requirements.txt
└── README.md
```

---

## The Four-Component Integration Plan

All six projects map directly to the GSoC deliverables for Contributor 1:

```
GSoC Deliverable                         Preparation Project
─────────────────────────────────────────────────────────────
OG-Core module in MUIO (backend)    ←    01_og_runner
ETL pipeline (CLEWS → OG-Core)      ←    02_etl_pipeline
Validation checks at each step      ←    03_validation_framework
Converging module prototype         ←    04_convergence_prototype
OG-Core API endpoints in MUIOGO     ←    05_ogcore_api
Country scenario documentation      ←    06_country_scenario
```

---

## Technical Stack

| Layer | Technology |
|---|---|
| Model execution | `ogcore`, `osemosys` (Python APIs) |
| Data processing | `pandas`, `numpy`, `xarray` |
| Validation | `pydantic`, `jsonschema` |
| API backend | `Flask`, `Blueprint` (mirrors MUIOGO) |
| Schema definition | `YAML` (declarative, no Python changes for new mappings) |
| Testing | `pytest` |
| Notebooks | `Jupyter`, `matplotlib` |
| Convergence metric | L2 norm (Euclidean distance between parameter vectors) |
| Logging | Python `logging` with file + console handlers |
| Output format | Structured JSON + timestamped run directories |

---

## Running the Projects

Each project is self-contained with its own `requirements.txt` and `README.md`.

```bash
# ETL Pipeline
cd etl_pipeline
pip install -r requirements.txt
python run_etl.py

# Convergence Prototype
cd convergence_prototype
pip install -r requirements.txt
python run_convergence.py --threshold 1e-4 --max-iterations 20

# Country Scenario (run notebooks in order)
cd country_scenario
pip install -r requirements.txt
jupyter notebook notebooks/
```

---

## Related Repositories

| Repository | Description |
|---|---|
| [EAPD-DRB/MUIOGO](https://github.com/EAPD-DRB/MUIOGO) | Main MUIOGO project — Flask backend + frontend UI |
| [PSLmodels/OG-Core](https://github.com/PSLmodels/OG-Core) | OG-Core macroeconomic model |
| [OSeMOSYS/OSeMOSYS](https://github.com/OSeMOSYS/OSeMOSYS) | OSeMOSYS energy modelling system |
| [OSeMOSYS/MUIO](https://github.com/OSeMOSYS/MUIO) | Original MUIO — upstream of MUIOGO |

---

## About the Contributor

I am applying as **Contributor 1 — Scientific Programming & Model Integration** for the OG-CLEWS project under UN OICT / UN DESA.

My focus is on the backend integration layer: the ETL pipeline, the coupled orchestrator, the convergence logic, and the scenario validation framework. I have spent the weeks before this application running both models locally, building a working data bridge between them, and studying the boundary between what CLEWS produces and what OG-Core consumes — not because I was asked to, but because I wanted to understand the problem before claiming I could solve it.

There is no project in this GSoC cycle I could be more committed to delivering.

---

## License

Apache License 2.0 — consistent with MUIOGO and OG-Core.

---

*GSoC 2026 — UN OICT / UN DESA Economic Analysis and Policy Division*