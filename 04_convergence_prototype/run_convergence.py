"""
run_convergence.py
------------------
Entry point for the OG-CLEWS convergence prototype.

Usage
-----
Default run (uses built-in initial parameters):
    python run_convergence.py

Custom threshold and max iterations:
    python run_convergence.py --threshold 1e-5 --max-iterations 30

Custom output directory:
    python run_convergence.py --output-dir path/to/outputs

Full custom run:
    python run_convergence.py --threshold 1e-5 --max-iterations 30 --output-dir runs/

Author: Tejas Singh Bhati
Project: OG-CLEWS Integration — GSoC 2026, UN DESA
"""

import argparse
import json
from pathlib import Path

from convergence import run_convergence


# ── Default initial parameters ────────────────────────────────────────────────
# These represent starting macroeconomic conditions passed to OG-Core
# on the first iteration. In production, these come from a country
# calibration file or from a prior CLEWS-only run.

DEFAULT_INITIAL_PARAMS = {
    "gdp_growth"   : 0.03,   # 3% annual GDP growth
    "capital_share": 0.35,   # capital's share of output
    "labor_share"  : 0.65,   # labor's share of output
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the OG-CLEWS iterative convergence prototype.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=1e-4,
        help="L2 norm convergence threshold",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=20,
        help="Maximum number of coupled iterations",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Base directory for run outputs",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("\nOG-CLEWS Convergence Prototype")
    print("=" * 60)
    print(f"Initial parameters : {json.dumps(DEFAULT_INITIAL_PARAMS, indent=2)}")
    print(f"Threshold          : {args.threshold}")
    print(f"Max iterations     : {args.max_iterations}")
    print(f"Output directory   : {args.output_dir}")
    print("=" * 60 + "\n")

    metadata = run_convergence(
        initial_og_params=DEFAULT_INITIAL_PARAMS,
        output_dir=args.output_dir,
        threshold=args.threshold,
        max_iterations=args.max_iterations,
    )

    print("\n── Run Summary ──────────────────────────────────────────")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()