"""
metrics.py
----------
Convergence metrics for the OG-CLEWS iterative coupling loop.

The core metric is the L2 norm (Euclidean distance) between two
successive parameter vectors. When this delta falls below a defined
threshold, the coupled system is considered converged.

In production, this module can be extended with:
  - Weighted L2 norm (weight variables by economic importance)
  - Max-norm (convergence based on worst-case variable)
  - Per-variable tracking (to identify which variable is slowest to converge)

Author: Tejas Singh Bhati
Project: OG-CLEWS Integration — GSoC 2026, UN DESA
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)


def _flatten(params: dict) -> np.ndarray:
    """
    Flatten a parameter dictionary into a 1D numpy array.

    Lists within values are unpacked element-wise.
    All values must be numeric.

    Parameters
    ----------
    params : dict
        Dictionary of scalar or list numeric values.

    Returns
    -------
    np.ndarray
        1D array of all numeric values in insertion order.
    """
    values = []
    for v in params.values():
        if isinstance(v, list):
            values.extend(v)
        else:
            values.append(v)
    return np.array(values, dtype=float)


def compute_delta(prev: dict, curr: dict) -> float:
    """
    Compute the L2 norm (Euclidean distance) between two
    successive parameter dictionaries.

    This is the primary convergence metric for the OG-CLEWS
    iterative loop. A smaller delta means the two models are
    producing more consistent outputs across iterations.

    Parameters
    ----------
    prev : dict
        Parameter values from the previous iteration.
    curr : dict
        Parameter values from the current iteration.

    Returns
    -------
    float
        L2 norm of (curr - prev). Returns 0.0 if both are empty.

    Raises
    ------
    ValueError
        If prev and curr have different keys or incompatible shapes.
    """
    if set(prev.keys()) != set(curr.keys()):
        raise ValueError(
            f"Parameter key mismatch between iterations.\n"
            f"  prev keys: {sorted(prev.keys())}\n"
            f"  curr keys: {sorted(curr.keys())}"
        )

    # Align by key order to ensure consistent vector positions
    keys = sorted(prev.keys())
    prev_aligned = _flatten({k: prev[k] for k in keys})
    curr_aligned = _flatten({k: curr[k] for k in keys})

    if prev_aligned.shape != curr_aligned.shape:
        raise ValueError(
            f"Shape mismatch after flattening: "
            f"{prev_aligned.shape} vs {curr_aligned.shape}"
        )

    delta = float(np.linalg.norm(curr_aligned - prev_aligned))
    logger.debug(f"  [metrics] L2 delta = {delta:.8f}")
    return delta


def compute_per_variable_delta(prev: dict, curr: dict) -> dict:
    """
    Compute the absolute change for each variable individually.

    Useful for diagnosing which variable is slowest to converge.

    Parameters
    ----------
    prev : dict
        Parameter values from the previous iteration.
    curr : dict
        Parameter values from the current iteration.

    Returns
    -------
    dict
        Mapping of variable name to absolute change.
        List-valued variables are reported as their L2 norm.
    """
    result = {}
    for key in prev:
        p = prev[key]
        c = curr[key]
        if isinstance(p, list) and isinstance(c, list):
            result[key] = float(np.linalg.norm(
                np.array(c, dtype=float) - np.array(p, dtype=float)
            ))
        else:
            result[key] = abs(float(c) - float(p))
    return result