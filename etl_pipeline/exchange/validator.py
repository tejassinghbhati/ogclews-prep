# exchange/validator.py
from pydantic import BaseModel, field_validator, ValidationError
from pathlib import Path
from typing import Union
import pandas as pd


REQUIRED_CSV_COLUMNS = {
    "TotalCapacityAnnual.csv":         ["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    "ProductionByTechnologyAnnual.csv":["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    "AnnualTechnologyEmission.csv":    ["REGION", "TECHNOLOGY", "EMISSION", "YEAR", "VALUE"],
    "TotalDiscountedCost.csv":         ["REGION", "YEAR", "VALUE"],
}


class OGExchangeParams(BaseModel):
    delta_tau_annual: float
    tau_c: float
    alpha_G: list[float]

    @field_validator("delta_tau_annual")
    @classmethod
    def check_delta_tau(cls, v):
        if not (0.0 < v < 1.0):
            raise ValueError(f"delta_tau_annual must be between 0 and 1, got {v}")
        return v

    @field_validator("tau_c")
    @classmethod
    def check_tau_c(cls, v):
        if v < 0:
            raise ValueError(f"tau_c must be non-negative, got {v}")
        return v

    @field_validator("alpha_G")
    @classmethod
    def check_alpha_G(cls, v):
        for val in v:
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"alpha_G values must be in [0, 1], got {val}")
        return v


def validate_inputs(data_dir: Path, required_files: list[str]) -> list[str]:
    """Check required CSVs exist and have expected columns. Returns list of errors."""
    errors = []
    for filename in required_files:
        path = data_dir / filename
        if not path.exists():
            errors.append(f"Missing file: {filename}")
            continue
        df = pd.read_csv(path)
        expected = REQUIRED_CSV_COLUMNS.get(filename, [])
        missing_cols = [c for c in expected if c not in df.columns]
        if missing_cols:
            errors.append(f"{filename}: missing columns {missing_cols}")
    return errors


def validate_outputs(params: dict) -> OGExchangeParams:
    """Validate transformed parameters against OG-Core schema. Raises on failure."""
    return OGExchangeParams(**params)