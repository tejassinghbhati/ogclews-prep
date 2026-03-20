# Convergence Prototype — OG-CLEWS

A prototype implementation of the iterative convergence loop between the CLEWS/OSeMOSYS resource systems model and the OG-Core macroeconomic model. Built as the fourth component of the **OG–CLEWS** integration project — a Google Summer of Code 2026 initiative under the United Nations Department of Economic and Social Affairs (UN DESA).

This prototype demonstrates the hardest architectural challenge of the full project: making two independent models talk to each other repeatedly until their outputs stabilize into a consistent solution.

---

## What this does

- Runs CLEWS (mocked) with current macroeconomic parameters
- Transforms CLEWS outputs into OG-Core inputs via a declarative mapping
- Runs OG-Core (mocked) with transformed inputs
- Computes an L2 norm convergence delta between successive parameter vectors
- Stops when delta falls below threshold or max iterations are reached
- Logs every iteration's state to a structured file
- Writes `history.json` and `metadata.json` to a timestamped output directory

---

## Convergence strategy

The coupled system converges when the macroeconomic outputs of OG-Core stop changing meaningfully between iterations — i.e., when CLEWS and OG-Core have reached a mutually consistent solution.

The convergence metric is the **L2 norm** (Euclidean distance) between the OG-Core parameter vectors of two successive iterations:

```
delta = || params_curr - params_prev ||_2
```

When `delta < threshold` (default: `1e-4`), the loop terminates with status `converged`.

---

## Project structure

```
04_convergence_prototype/
├── convergence/
│   ├── __init__.py          ← package exports
│   ├── mock_clews.py        ← mock CLEWS/OSeMOSYS runner
│   ├── mock_ogcore.py       ← mock OG-Core runner
│   ├── metrics.py           ← L2 norm + per-variable delta
│   └── orchestrator.py      ← iterative coupling loop
├── outputs/                 ← auto-created on first run
├── run_convergence.py       ← CLI entry point
├── requirements.txt
└── README.md
```

---

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run with defaults

```bash
python run_convergence.py
```

### 3. Custom run

```bash
python run_convergence.py --threshold 1e-5 --max-iterations 30 --output-dir runs/
```

---

## Expected output

```
OG-CLEWS Convergence Prototype
============================================================
Initial parameters : {
  "gdp_growth": 0.03,
  "capital_share": 0.35,
  "labor_share": 0.65
}
Threshold          : 0.0001
Max iterations     : 20
Output directory   : outputs
============================================================

2026-03-14 11:30:00  INFO     ── Iteration 1 ────────────────────────────
2026-03-14 11:30:00  INFO       OG-Core inputs : {'gdp_growth': 0.03, ...}
2026-03-14 11:30:00  INFO       [1/3] Running CLEWS...
2026-03-14 11:30:00  INFO       [CLEWS] outputs: {'delta_tau_annual': 0.044, ...}
2026-03-14 11:30:00  INFO       [2/3] Running OG-Core...
2026-03-14 11:30:00  INFO       [OG-Core] outputs: {'gdp_growth': 0.033, ...}
2026-03-14 11:30:00  INFO       [3/3] Computing convergence delta...
2026-03-14 11:30:00  INFO       delta (L2)     : 0.00412300  (threshold: 0.0001)
...
2026-03-14 11:30:00  INFO     ✓ Converged at iteration 8  (delta=8.21e-05 < 1.00e-04)
```

---

## Output files

Each run produces a timestamped directory under `outputs/`:

```
outputs/
└── 20260314_113000/
    ├── convergence.log     ← full iteration log
    ├── history.json        ← per-iteration state (inputs, outputs, delta)
    └── metadata.json       ← run summary (status, iterations, final delta)
```

### metadata.json

```json
{
  "run_id": "20260314_113000",
  "status": "converged",
  "iterations": 8,
  "final_delta": 0.0000821,
  "threshold": 0.0001,
  "max_iterations": 20,
  "initial_og_params": { "gdp_growth": 0.03, "capital_share": 0.35, "labor_share": 0.65 },
  "final_og_params": { "gdp_growth": 0.0328, "capital_share": 0.352, "labor_share": 0.648 },
  "timestamp": "2026-03-14T11:30:00"
}
```

---

## Coupling modes

This prototype implements **one-way coupling with feedback** (CLEWS → OG-Core → CLEWS). The full GSoC project will extend this to:

| Mode | Description |
|---|---|
| Coupled (one-way) | CLEWS → ETL → OG-Core, single pass |
| Coupled (two-way) | CLEWS → OG-Core → CLEWS, single feedback loop |
| **Converging** | **CLEWS ↔ OG-Core iterated until stable** ← this prototype |

---

## From mock to production

The mock runners are clearly labeled and isolated in their own modules. Replacing them with real model runners requires only:

1. Replace `mock_clews.run_clews()` with a call to the real OSeMOSYS/CLEWS runner and CSV reader
2. Replace `mock_ogcore.run_ogcore()` with a call to `ogcore.execute.runner()` via `p.update_specifications()`
3. Wire in the ETL pipeline from `02_etl_pipeline/` for the transform steps

The orchestrator, metrics, and output structure remain unchanged.

---

## Context: OG–CLEWS integration plan

```
[1] OG-Core Runner       ← 01_og_runner/        ✅ complete
[2] ETL Pipeline         ← 02_etl_pipeline/      ✅ complete
[3] Validation Framework ← 03_validation/        ✅ complete
[4] Convergence Proto    ← this project          ✅ complete
```

---

## Requirements

```
numpy
pytest
```

---

## License

Apache License 2.0 — consistent with the MUIOGO and OG-Core projects.

---

## Acknowledgements

Built as part of the [MUIOGO](https://github.com/EAPD-DRB/MUIOGO) project under the Economic Analysis and Policy Division (EAPD), United Nations Department of Economic and Social Affairs (UN DESA).