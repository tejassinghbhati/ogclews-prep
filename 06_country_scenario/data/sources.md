# Data Sources — Mauritius Country Scenario

## Country Selection Rationale

Mauritius was selected as the reference country for this scenario for three reasons:

1. **Pioneer CLEWS case study** — Mauritius is one of the earliest documented CLEWS implementations, developed by KTH Royal Institute of Technology and UN DESA, making it the most well-documented reference case.
2. **Small Island Developing State (SIDS)** — directly matches the primary target countries of the OG-CLEWS deployment programme (10+ countries through 2030).
3. **Public data availability** — energy statistics, GDP data, and emissions inventories are all publicly available through international databases.

---

## CLEWS Output Data

The CSV files in `clews_outputs/` are calibrated simulations based on the following public sources.
They represent a Renewable Energy Transition scenario (2020–2035) consistent with Mauritius's NDC targets.

### Energy Capacity (`TotalCapacityAnnual.csv`)
- **Unit:** GW (gigawatts)
- **Technologies modelled:**
  - `SOLAR_PV` — utility-scale solar photovoltaic
  - `WIND_ONSHORE` — onshore wind turbines
  - `BAGASSE_CHP` — combined heat and power from sugarcane bagasse
  - `DIESEL_OPEN_CYCLE` — open-cycle diesel generation (being phased out)
  - `HYDRO_RUN` — run-of-river hydropower
- **Source basis:** Mauritius Long-Term Energy Strategy 2009–2025 (Ministry of Energy); IEA Africa Energy Outlook 2022; IRENA Renewable Power Generation Costs 2022

### Energy Production (`ProductionByTechnologyAnnual.csv`)
- **Unit:** PJ (petajoules)
- **Source basis:** IEA World Energy Balances; Mauritius Central Statistics Office Energy Statistics 2022; KTH CLEWS Mauritius model documentation

### CO2 Emissions (`AnnualTechnologyEmission.csv`)
- **Unit:** Mt CO2 (megatonnes)
- **Emission factors:**
  - Diesel: 0.727 kg CO2/kWh (IPCC 2006 default)
  - Bagasse: 0.060 kg CO2/kWh (net biogenic, partial credit)
  - Solar, Wind, Hydro: 0.000 (zero direct emissions)
- **Source basis:** IPCC 2006 Guidelines for National Greenhouse Gas Inventories; Mauritius Third National Communication to UNFCCC (2021)

### System Costs (`TotalDiscountedCost.csv`)
- **Unit:** MUSD (millions of USD, discounted at 8%)
- **Source basis:** IRENA Renewable Energy Statistics 2023; World Bank energy investment data; IMF World Economic Outlook (Mauritius GDP deflator)

---

## OG-Core Calibration Data

The `og_inputs/og_exchange.json` file was produced by running the ETL pipeline
(`02_etl_pipeline/`) on the CLEWS output CSVs above.

Key macroeconomic calibration parameters for Mauritius:
- **GDP (2020):** ~14.1 billion USD (World Bank)
- **GDP growth rate (pre-COVID baseline):** ~3.8% annually
- **Capital share of income:** ~0.38 (Penn World Tables 10.0)
- **Labor share of income:** ~0.62
- **Government spending as % of GDP:** ~22% (IMF 2022)
- **Source:** World Bank World Development Indicators; Penn World Tables 10.0; IMF Article IV Consultation — Mauritius 2022

---

## Key References

| Source | URL |
|---|---|
| KTH CLEWS Mauritius | https://github.com/KTH-dESA/CLEWS_Mauritius |
| OSeMOSYS GitHub | https://github.com/OSeMOSYS/OSeMOSYS |
| UN DESA EAPD Modelling | https://www.un.org/development/desa/dpad/ |
| IEA Africa Energy Outlook | https://www.iea.org/reports/africa-energy-outlook-2022 |
| IRENA Renewable Stats | https://www.irena.org/Statistics |
| Mauritius NDC (2021) | https://unfccc.int/sites/default/files/NDC/Mauritius |
| World Bank WDI | https://databank.worldbank.org/source/world-development-indicators |
| Penn World Tables 10.0 | https://www.rug.nl/ggdc/productivity/pwt/ |
| IMF WEO Mauritius | https://www.imf.org/en/Publications/WEO |

---

## Disclaimer

The CLEWS output CSVs in this repository are calibrated simulations for
demonstration purposes, consistent with publicly available data and
Mauritius's documented energy transition trajectory. They are not official
UN DESA model outputs. For official country-level CLEWS results,
contact the Economic Analysis and Policy Division (EAPD), UN DESA.