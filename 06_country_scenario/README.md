# Country Scenario — Mauritius Renewable Energy Transition

A complete end-to-end OG-CLEWS workflow for the Republic of Mauritius, demonstrating how CLEWS/OSeMOSYS resource system outputs are transformed into OG-Core macroeconomic inputs and what the integrated results reveal for policymakers.

Built as the sixth component of the **OG–CLEWS** integration project — a Google Summer of Code 2026 initiative under the United Nations Department of Economic and Social Affairs (UN DESA).

---

## Why Mauritius

Mauritius is a Small Island Developing State (SIDS) — the primary target of the OG-CLEWS deployment programme. It was one of the first countries modelled under the CLEWS framework by KTH Royal Institute of Technology and UN DESA, making it the most documented and reproducible reference case. Its 2015 NDC commits to 35% renewable electricity by 2025 and 60% by 2030, providing a clear policy scenario to model.

---

## Project structure

```
06_country_scenario/
├── data/
│   ├── clews_outputs/
│   │   ├── TotalCapacityAnnual.csv           ← installed capacity (GW) 2020-2035
│   │   ├── ProductionByTechnologyAnnual.csv  ← energy produced (PJ) 2020-2035
│   │   ├── AnnualTechnologyEmission.csv      ← CO2 emissions (Mt) 2020-2035
│   │   └── TotalDiscountedCost.csv           ← system cost (MUSD) 2020-2035
│   ├── og_inputs/
│   │   └── og_exchange.json                  ← ETL output: OG-Core parameters
│   └── sources.md                            ← full data provenance
│
├── notebooks/
│   ├── 01_clews_output_exploration.ipynb     ← load, plot, summarise CLEWS outputs
│   ├── 02_etl_trace.ipynb                    ← step-by-step ETL transformation trace
│   └── 03_ogcore_scenario.ipynb              ← OG-Core run + results interpretation
│
├── outputs/
│   ├── og_results.json                       ← final macroeconomic results
│   ├── workflow_summary.md                   ← full written narrative
│   ├── fig1_capacity.png                     ← capacity by technology
│   ├── fig2_production_mix.png               ← production mix stacked bar
│   ├── fig3_emissions.png                    ← CO2 trajectory
│   ├── fig4_system_cost.png                  ← discounted system cost
│   ├── fig5_co2_to_tauc.png                  ← ETL mapping visualisation
│   └── fig6_ogcore_results.png               ← OG-Core results vs baseline
│
└── README.md
```

---

## Quickstart

```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```

Run the notebooks in order: 01 → 02 → 03.

---

## Key Results

| Indicator | Baseline | Renewable Transition | Delta |
|---|---|---|---|
| GDP Growth Rate | 3.80% | 4.06% | ▲ +0.26% |
| Wage Index (2020=1) | 1.000 | 1.065 | ▲ +6.5% |
| Tax Revenue (% GDP) | 19.2% | 21.6% | ▲ +2.4pp |
| CO2 Emissions (2035) | — | 0.547 Mt | ▼ -83% vs 2020 |
| Solar Capacity (2035) | — | 2.20 GW | ▲ 18× vs 2020 |

Mauritius's renewable energy transition is both physically feasible (CLEWS) and macroeconomically beneficial (OG-Core). This integrated finding is only possible when both models run together — which is exactly what the OG-CLEWS project enables.

---

## ETL Schema

| CLEWS Output | OG-Core Parameter | Transformation |
|---|---|---|
| `TotalCapacityAnnual` (energy techs, sum) | `delta_tau_annual` = 0.0459 | GW → TW, normalize [0.04, 0.06] |
| `AnnualTechnologyEmission` (CO2, sum) | `tau_c` = 0.000625 | Linear scale × 0.0005 |
| `TotalDiscountedCost` (sum) | `alpha_G` = [0.0422] | Cost/GDP, normalize [0.03, 0.08] |

---

## Technologies modelled

| Code | Technology |
|---|---|
| `SOLAR_PV` | Utility-scale solar photovoltaic |
| `WIND_ONSHORE` | Onshore wind turbines |
| `BAGASSE_CHP` | Combined heat & power from sugarcane bagasse |
| `DIESEL_OPEN_CYCLE` | Open-cycle diesel (being phased out) |
| `HYDRO_RUN` | Run-of-river hydropower |

---

## Context: OG–CLEWS integration plan

```
[1] OG-Core Runner       ← 01_og_runner/        ✅ complete
[2] ETL Pipeline         ← 02_etl_pipeline/      ✅ complete
[3] Validation Framework ← 03_validation/        ✅ complete
[4] Convergence Proto    ← 04_convergence/       ✅ complete
[5] Flask API Endpoints  ← 05_ogcore_api/        ✅ complete
[6] Country Scenario     ← this project          ✅ complete
```

---

## Requirements

```
pandas
numpy
matplotlib
jupyter
```

---

## License

Apache License 2.0 — consistent with MUIOGO and OG-Core.

---

## Acknowledgements

Built as part of the [MUIOGO](https://github.com/EAPD-DRB/MUIOGO) project under the Economic Analysis and Policy Division (EAPD), United Nations Department of Economic and Social Affairs (UN DESA). Data sources documented in `data/sources.md`.