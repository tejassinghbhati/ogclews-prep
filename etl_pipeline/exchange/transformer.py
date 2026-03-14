# exchange/transformer.py
import yaml
import pandas as pd
import numpy as np
from pathlib import Path


def load_schema(schema_path: Path) -> dict:
    with open(schema_path) as f:
        return yaml.safe_load(f)


def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    for col, values in filters.items():
        if values:
            df = df[df[col].isin(values)]
    return df


def _aggregate(df: pd.DataFrame, method: str, group_by: str, column: str) -> pd.Series:
    if method == "sum":
        return df.groupby(group_by)[column].sum()
    elif method == "mean":
        return df.groupby(group_by)[column].mean()
    raise ValueError(f"Unknown aggregation method: {method}")


def _transform(series: pd.Series, transform_config: dict) -> float:
    method = transform_config["method"]
    values = series.values

    if method == "scale_to_range":
        lo, hi = transform_config["min"], transform_config["max"]
        v_min, v_max = values.min(), values.max()
        if v_max == v_min:
            return lo
        normalized = (values.mean() - v_min) / (v_max - v_min)
        return float(lo + normalized * (hi - lo))

    elif method == "linear_scale":
        slope = transform_config["slope"]
        intercept = transform_config.get("intercept", 0.0)
        return float(values.mean() * slope + intercept)

    raise ValueError(f"Unknown transform method: {method}")


def run_transform(schema_path: Path, data_dir: Path) -> dict:
    """
    Execute all mappings in the schema against the CLEWS output CSVs.
    Returns a dict of {og_parameter_name: value} ready for update_specifications().
    """
    schema = load_schema(schema_path)
    results = {}

    for mapping in schema["mappings"]:
        mapping_id = mapping["id"]
        src = mapping["source"]

        # Load source CSV
        csv_path = data_dir / src["file"]
        if not csv_path.exists():
            raise FileNotFoundError(f"[{mapping_id}] Source file not found: {csv_path}")

        df = pd.read_csv(csv_path)

        # Apply filters
        df = _apply_filters(df, src.get("filters", {}))

        # Aggregate
        agg_config = src["aggregate"]
        series = _aggregate(df, agg_config["method"], agg_config["group_by"], src["column"])

        # Unit conversion
        factor = mapping.get("unit_conversion", {}).get("factor", 1.0)
        series = series * factor

        # Transform to scalar
        value = _transform(series, mapping["transform"])

        # Package for OG-Core
        target = mapping["target"]
        param_name = target["parameter"]
        if target["type"] == "list":
            length = target.get("length", 1)
            value = [value] * length

        results[param_name] = value
        print(f"  [{mapping_id}] → {param_name} = {value}")

    return results