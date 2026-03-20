# tests/test_validator.py
from exchange.validator import validate_outputs, validate_inputs
from pathlib import Path
import pytest

def test_valid_params_pass():
    params = {"delta_tau_annual": 0.05, "tau_c": 0.02, "alpha_G": [0.05]}
    result = validate_outputs(params)
    assert result.delta_tau_annual == 0.05

def test_invalid_delta_tau_raises():
    with pytest.raises(Exception):
        validate_outputs({"delta_tau_annual": 1.5, "tau_c": 0.0, "alpha_G": [0.05]})

def test_missing_file_caught(tmp_path):
    errors = validate_inputs(tmp_path, ["TotalCapacityAnnual.csv"])
    assert any("Missing file" in e for e in errors)
