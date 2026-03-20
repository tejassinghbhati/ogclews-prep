# runner/summary_extractor.py
import pickle
import csv
import json
import numpy as np
from pathlib import Path

# The variables we care about for ETL into CLEWS later
SS_KEYS = ["Y_ss", "K_ss", "L_ss", "C_ss", "r_ss", "w_ss", "T_H_ss", "TR_ss"]
TPI_KEYS = ["Y", "K", "L", "C", "r", "w", "T_H"]

def _load_pkl(path: Path) -> dict:
    with open(path, "rb") as f:
        return pickle.load(f)

def _to_scalar(val):
    if isinstance(val, np.ndarray):
        return float(val.flat[0]) if val.size == 1 else val.tolist()
    return float(val) if hasattr(val, "__float__") else val

def extract_summary(results_dir: Path, scenario: str = "BASELINE") -> dict:
    ss_path = results_dir / f"OUTPUT_{scenario}" / "SS" / "SS_vars.pkl"
    tpi_path = results_dir / f"OUTPUT_{scenario}" / "TPI" / "TPI_vars.pkl"

    summary = {}

    if ss_path.exists():
        ss = _load_pkl(ss_path)
        for key in SS_KEYS:
            if key in ss:
                summary[key] = _to_scalar(ss[key])

    if tpi_path.exists():
        tpi = _load_pkl(tpi_path)
        for key in TPI_KEYS:
            if key in tpi:
                val = tpi[key]
                # TPI vars are time-series arrays — store first 10 years
                summary[f"{key}_path"] = _to_scalar(val[:10]) if isinstance(val, np.ndarray) else val

    return summary

def write_summary_csv(summary: dict, output_path: Path):
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["variable", "value"])
        for k, v in summary.items():
            writer.writerow([k, json.dumps(v) if isinstance(v, list) else v])