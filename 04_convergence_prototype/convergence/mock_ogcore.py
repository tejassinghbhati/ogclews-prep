"""
mock_ogcore.py
--------------
Mock implementation of the OG-Core macroeconomic model.

In production, this module will be replaced by a real OG-Core runner
that invokes ogcore.execute.runner() programmatically, passing
transformed CLEWS outputs via p.update_specifications().

For the convergence prototype, this mock simulates OG-Core behavior:
  - Takes CLEWS resource system outputs as inputs (via ETL exchange)
  - Returns macroeconomic aggregates (GDP growth, factor shares)
  - Applies mild iteration-based drift to simulate model dynamics

OG-Core outputs that feed back into CLEWS (via reverse ETL):
  - gdp_growth    : annual GDP growth rate
  - capital_share : capital's share of output
  - labor_share   : labor's share of output

Author: Tejas Singh Bhati
Project: OG-CLEWS Integration — GSoC 2026, UN DESA
"""

import math
import logging

logger = logging.getLogger(__name__)


def run_ogcore(clews_params: dict, iteration: int) -> dict:
    """
    Mock OG-Core run.

    Takes CLEWS resource outputs (post-ETL transformation) as inputs
    and returns macroeconomic aggregates.

    Parameters
    ----------
    clews_params : dict
        Resource system parameters from CLEWS (post-ETL):
            - delta_tau_annual : capital depreciation proxy
            - tau_c            : carbon consumption tax proxy
            - alpha_G          : government spending share (list)

    iteration : int
        Current iteration number (used to simulate convergence dynamics)

    Returns
    -------
    dict
        OG-Core macroeconomic outputs:
            - gdp_growth    : annual GDP growth rate
            - capital_share : share of capital in output
            - labor_share   : share of labor in output
    """
    delta_tau = clews_params.get("delta_tau_annual", 0.04)
    tau_c     = clews_params.get("tau_c", 0.02)
    alpha_G   = clews_params.get("alpha_G", [0.035])
    alpha_G_val = alpha_G[0] if isinstance(alpha_G, list) else alpha_G

    # Simulate macroeconomic response with mild convergence drift
    # In production: run ogcore.execute.runner() and parse SS/TPI outputs
    decay = math.exp(-0.5 * iteration)

    # Outputs converge toward fixed points as decay → 0
    gdp_growth    = round(0.03 + delta_tau * 0.5 + 0.002 * decay, 6)
    capital_share = round(0.35 + tau_c * 0.08 + 0.0005 * decay, 6)
    labor_share   = round(1.0 - capital_share, 6)

    outputs = {
        "gdp_growth": gdp_growth,
        "capital_share": capital_share,
        "labor_share": labor_share,
    }

    logger.info(f"  [OG-Core] outputs: {outputs}")
    return outputs