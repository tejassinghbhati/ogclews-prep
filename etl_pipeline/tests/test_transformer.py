# tests/test_transformer.py
from pathlib import Path
from exchange.transformer import run_transform

def test_transform_returns_all_target_params(tmp_path):
    # Copy fixture CSVs to tmp and run
    import shutil
    shutil.copytree("data/sample_clews_outputs", tmp_path / "clews")
    params = run_transform(
        Path("exchange/schema_clews_to_og.yaml"),
        tmp_path / "clews"
    )
    assert "delta_tau_annual" in params
    assert "tau_c" in params
    assert "alpha_G" in params

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