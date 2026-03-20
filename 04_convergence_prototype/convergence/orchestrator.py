"""
orchestrator.py
---------------
Core convergence orchestrator for the OG-CLEWS coupled model loop.

This module implements the iterative coupling strategy between
CLEWS/OSeMOSYS (resource systems) and OG-Core (macroeconomic model):

    [1] Run CLEWS with current macro parameters
    [2] Transform CLEWS outputs → OG-Core inputs (ETL forward)
    [3] Run OG-Core with transformed inputs
    [4] Compute convergence delta (L2 norm)
    [5] If delta < threshold → converged, stop
        Else → update macro parameters, go to [1]

In production:
  - run_clews()  → real OSeMOSYS/CLEWS runner
  - run_ogcore() → real ogcore.execute.runner() call
  - ETL steps    → etl_pipeline.exchange.transformer

Author: Tejas Singh Bhati
Project: OG-CLEWS Integration — GSoC 2026, UN DESA
"""

import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

from .mock_clews import run_clews
from .mock_ogcore import run_ogcore
from .metrics import compute_delta, compute_per_variable_delta


# ── Default convergence settings ────────────────────────────────────────────

DEFAULT_THRESHOLD      = 1e-4   # L2 norm threshold for convergence
DEFAULT_MAX_ITERATIONS = 20     # hard stop if convergence not reached


# ── Logging setup ────────────────────────────────────────────────────────────

def _setup_logger(log_path: Path) -> logging.Logger:
    """Configure a logger that writes to both file and stdout."""
    logger = logging.getLogger("ogclews.convergence")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

    # File handler
    fh = logging.FileHandler(log_path, mode="w")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger


# ── Main orchestrator ─────────────────────────────────────────────────────────

def run_convergence(
    initial_og_params: dict,
    output_dir: Path,
    threshold: float = DEFAULT_THRESHOLD,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> dict:
    """
    Run the OG-CLEWS iterative convergence loop.

    Parameters
    ----------
    initial_og_params : dict
        Starting macroeconomic parameters for OG-Core:
            - gdp_growth    : float
            - capital_share : float
            - labor_share   : float

    output_dir : Path
        Directory to write all outputs:
            outputs/{run_id}/
                convergence.log
                history.json
                metadata.json

    threshold : float
        L2 norm convergence threshold. Default: 1e-4.

    max_iterations : int
        Maximum number of coupled iterations. Default: 20.

    Returns
    -------
    dict
        Run metadata including status, iteration count, final delta,
        and output file paths.
    """
    run_id    = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir   = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    log_path  = run_dir / "convergence.log"
    logger    = _setup_logger(log_path)

    logger.info("=" * 60)
    logger.info("OG-CLEWS Convergence Prototype")
    logger.info(f"Run ID       : {run_id}")
    logger.info(f"Threshold    : {threshold}")
    logger.info(f"Max iters    : {max_iterations}")
    logger.info(f"Output dir   : {run_dir}")
    logger.info("=" * 60)

    og_params = initial_og_params.copy()
    history   = []
    status    = "max_iterations_reached"

    for i in range(1, max_iterations + 1):
        logger.info(f"\n── Iteration {i} {'─' * 40}")
        logger.info(f"  OG-Core inputs : {og_params}")

        # ── Step 1: Run CLEWS ───────────────────────────────────────────
        logger.info("  [1/3] Running CLEWS...")
        clews_outputs = run_clews(og_params, i)

        # ── Step 2: Run OG-Core ─────────────────────────────────────────
        logger.info("  [2/3] Running OG-Core...")
        new_og_params = run_ogcore(clews_outputs, i)

        # ── Step 3: Compute convergence delta ───────────────────────────
        logger.info("  [3/3] Computing convergence delta...")
        delta     = compute_delta(og_params, new_og_params)
        per_var   = compute_per_variable_delta(og_params, new_og_params)

        logger.info(f"  delta (L2)     : {delta:.8f}  (threshold: {threshold})")
        logger.info(f"  per-variable   : {per_var}")

        # ── Record iteration state ──────────────────────────────────────
        history.append({
            "iteration"    : i,
            "og_inputs"    : og_params,
            "clews_outputs": clews_outputs,
            "og_outputs"   : new_og_params,
            "delta"        : delta,
            "per_variable" : per_var,
        })

        # ── Check convergence ───────────────────────────────────────────
        if delta < threshold:
            logger.info(f"\n✓ Converged at iteration {i}  (delta={delta:.2e} < {threshold:.2e})")
            status = "converged"
            og_params = new_og_params
            break

        og_params = new_og_params

    else:
        logger.warning(
            f"\n⚠ Maximum iterations ({max_iterations}) reached without convergence. "
            f"Final delta: {history[-1]['delta']:.6f}"
        )

    # ── Write history ───────────────────────────────────────────────────────
    history_path = run_dir / "history.json"
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
    logger.info(f"\nHistory written  → {history_path}")

    # ── Write metadata ──────────────────────────────────────────────────────
    metadata = {
        "run_id"           : run_id,
        "status"           : status,
        "iterations"       : len(history),
        "final_delta"      : history[-1]["delta"],
        "threshold"        : threshold,
        "max_iterations"   : max_iterations,
        "initial_og_params": initial_og_params,
        "final_og_params"  : og_params,
        "timestamp"        : datetime.now().isoformat(),
        "output_files"     : {
            "log"    : str(log_path),
            "history": str(history_path),
        }
    }

    metadata_path = run_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Metadata written → {metadata_path}")

    logger.info("\n" + "=" * 60)
    logger.info(f"Run complete — status: {status.upper()}")
    logger.info("=" * 60)

    metadata["output_files"]["metadata"] = str(metadata_path)
    return metadata