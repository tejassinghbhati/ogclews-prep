# OG-Core Flask API — MUIOGO Backend Extension

A Flask Blueprint that extends MUIOGO's existing API backend with OG-Core run management endpoints. Built as the fifth component of the **OG–CLEWS** integration project — a Google Summer of Code 2026 initiative under the United Nations Department of Economic and Social Affairs (UN DESA).

This follows the exact same patterns as the existing CLEWS endpoints in `CaseRoute.py` — Blueprint registration, response format, session validation, error handling, and directory structure.

---

## What this adds to MUIOGO

| Endpoint | Method | Description |
|---|---|---|
| `/ogcore/run` | POST | Trigger an OG-Core run (non-blocking) |
| `/ogcore/status/<run_id>` | GET | Poll run status |
| `/ogcore/results/<run_id>` | GET | Retrieve results for a completed run |
| `/ogcore/runs` | POST | List all OG-Core runs for active case |
| `/ogcore/run/<run_id>` | DELETE | Delete a run's output directory |

---

## Files

```
05_ogcore_api/
├── API/
│   ├── app_patch.py                    ← two lines to add to existing app.py
│   ├── Routes/
│   │   └── OGCore/
│   │       ├── __init__.py
│   │       └── OGCoreRoute.py          ← Flask Blueprint (5 endpoints)
│   └── Classes/
│       └── OGCore/
│           ├── __init__.py
│           └── OGCoreRunner.py         ← programmatic OG-Core runner
└── README.md
```

---

## How to integrate into MUIOGO

This is designed as a drop-in addition — it does not modify any existing files.

### Step 1 — Copy the new files

```bash
cp -r API/Routes/OGCore   MUIOGO/API/Routes/
cp -r API/Classes/OGCore  MUIOGO/API/Classes/
```

### Step 2 — Register the Blueprint in app.py

Open `MUIOGO/API/app.py` and add two lines:

```python
# After existing route imports:
from Routes.OGCore.OGCoreRoute import ogcore_api

# After existing blueprint registrations:
app.register_blueprint(ogcore_api)
```

That's it. The five endpoints are now live.

---

## Endpoint reference

### POST `/ogcore/run`

Trigger an OG-Core run for the active case session.

**Request:**
```json
{
  "casename": "MyScenario",
  "ogcore_params": {
    "gdp_growth": 0.03,
    "capital_share": 0.35,
    "labor_share": 0.65
  }
}
```

**Response:**
```json
{
  "message": "OG-Core run <b>ogcore_20260314_113000</b> started!",
  "status_code": "running",
  "run_id": "ogcore_20260314_113000"
}
```

The run executes in a background thread. The response is immediate — poll `/ogcore/status/<run_id>` to track progress.

---

### GET `/ogcore/status/<run_id>`

Poll run status. Returns `"running"` | `"completed"` | `"failed"`.

**Response:**
```json
{
  "run_id": "ogcore_20260314_113000",
  "status": "completed",
  "casename": "MyScenario",
  "status_code": "success"
}
```

---

### GET `/ogcore/results/<run_id>`

Return output file paths and key macroeconomic results.

**Response:**
```json
{
  "run_id": "ogcore_20260314_113000",
  "casename": "MyScenario",
  "status": "completed",
  "results": {
    "macro_aggregates": {
      "GDP_growth": 0.03,
      "investment_share": 0.105,
      "consumption_share": 0.895
    },
    "factor_prices": {
      "wage_rate": 1.06,
      "interest_rate": 0.047
    },
    "fiscal": {
      "tax_revenue_pct_gdp": 0.195
    }
  },
  "output_dirs": {
    "results": "DataStorage/MyScenario/res/ogcore_20260314_113000/results",
    "logs": "DataStorage/MyScenario/res/ogcore_20260314_113000/logs",
    "metadata": "DataStorage/MyScenario/res/ogcore_20260314_113000/metadata.json"
  },
  "status_code": "success"
}
```

---

### POST `/ogcore/runs`

List all OG-Core runs for a case.

**Request:** `{ "casename": "MyScenario" }`

**Response:** `{ "runs": ["ogcore_20260315_...", "ogcore_20260314_..."], "status_code": "success" }`

---

### DELETE `/ogcore/run/<run_id>`

Delete a run's output directory. Requires active session.

**Response:** `{ "message": "Run <b>ogcore_...</b> deleted!", "status_code": "success" }`

---

## Output directory structure

Each run produces a timestamped directory under `DataStorage/{casename}/res/`:

```
DataStorage/
└── MyScenario/
    └── res/
        └── ogcore_20260314_113000/
            ├── results/
            │   └── og_results.json     ← macroeconomic aggregates
            ├── logs/
            │   └── ogcore_run.log      ← full execution log
            └── metadata.json           ← run config, status, timestamps
```

This mirrors the existing CLEWS output structure in MUIOGO exactly.

---

## From mock to production

The `OGCoreRunner._mock_run()` method currently returns simulated outputs. Replacing it with real OG-Core execution requires only uncommenting the production block in `OGCoreRunner.run()`:

```python
import ogcore.parameters as Specifications
import ogcore.execute as runner

p = Specifications.Calibration()
p.update_specifications(overrides)

with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
    runner.run_og_spec(p, output_base=str(self.results_dir))
```

The Blueprint, endpoints, response format, and output structure remain unchanged.

---

## Context: OG–CLEWS integration plan

```
[1] OG-Core Runner       ← 01_og_runner/        ✅ complete
[2] ETL Pipeline         ← 02_etl_pipeline/      ✅ complete
[3] Validation Framework ← 03_validation/        ✅ complete
[4] Convergence Proto    ← 04_convergence/       ✅ complete
[5] Flask API Endpoints  ← this project          ✅ complete
```

---

## License

Apache License 2.0 — consistent with MUIOGO and OG-Core.