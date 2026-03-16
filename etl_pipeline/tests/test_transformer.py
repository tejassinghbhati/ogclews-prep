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