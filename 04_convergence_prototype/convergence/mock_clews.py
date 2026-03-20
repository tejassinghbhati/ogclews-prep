"""
mock_clews.py
-------------
Mock implementation of the CLEWS/OSeMOSYS resource systems model.

In production, this module will be replaced by a real CLEWS runner
that invokes OSeMOSYS via its Python API and reads actual output CSVs.

For the convergence prototype, this mock simulates CLEWS behavior:
  - Takes macroeconomic parameters from OG-Core as inputs
  - Returns sectoral resource outputs (energy, land, water variables)
  - Adds mild iteration-based drift to simulate model dynamics

CLEWS outputs that feed into OG-Core (via ETL pipeline):
  - delta_tau_annual : capital depreciation proxy (from energy investment)
  - tau_c            : carbon tax proxy (from CO2 emissions)
  - alpha_G          : government spending share (from system costs)

Author: Tejas Singh Bhati
Project: OG-CLEWS Integration — GSoC 2026, UN DESA
"""

import math
import logging

logger = logging.getLogger(__name__)


def run_clews(og_params: dict, iteration: int) -> dict:
    """
    Mock CLEWS run.

    Takes OG-Core macroeconomic outputs as inputs and returns
    CLEWS resource system outputs after applying sector-level dynamics.

    Parameters
    ----------
    og_params : dict
        Macroeconomic parameters from OG-Core:
            - gdp_growth    : annual GDP growth rate
            - capital_share : share of capital in output
            - labor_share   : share of labor in output

    iteration : int
        Current iteration number (used to simulate convergence dynamics)

    Returns
    -------
    dict
        CLEWS resource outputs:
            - delta_tau_annual : capital depreciation proxy
            - tau_c            : carbon consumption tax proxy
            - alpha_G          : government spending share (list)
    """
    gdp_growth    = og_params.get("gdp_growth", 0.03)
    capital_share = og_params.get("capital_share", 0.35)
    labor_share   = og_params.get("labor_share", 0.65)

    # Simulate sector-level dynamics with mild convergence drift
    # In production: read from TotalCapacityAnnual.csv, AnnualTechnologyEmission.csv, TotalDiscountedCost.csv
    decay = math.exp(-0.5 * iteration)  # dampening factor — drives convergence

    # Outputs converge toward fixed points as decay → 0
    delta_tau_annual = round(0.042 + (gdp_growth - 0.03) * 0.1 + 0.002 * decay, 6)
    tau_c            = round(0.019 + (capital_share - 0.35) * 0.05 + 0.001 * decay, 6)
    alpha_G          = [round(0.035 + (labor_share - 0.65) * 0.02 + 0.0005 * decay, 6)]

    outputs = {
        "delta_tau_annual": delta_tau_annual,
        "tau_c": tau_c,
        "alpha_G": alpha_G,
    }

    logger.info(f"  [CLEWS] outputs: {outputs}")
    return outputs