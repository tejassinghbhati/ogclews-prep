"""
Root conftest.py — shared pytest fixtures for all test modules.
"""
import json
import pytest
from pathlib import Path


# ── Sample config dicts (mirrors sample_data/) ──────────────────────────────

@pytest.fixture()
def valid_og_config():
    sample = Path(__file__).parent / "sample_data" / "valid_og_config.json"
    with sample.open() as fh:
        return json.load(fh)


@pytest.fixture()
def invalid_og_config():
    sample = Path(__file__).parent / "sample_data" / "invalid_og_config.json"
    with sample.open() as fh:
        return json.load(fh)


@pytest.fixture()
def valid_clews_config(tmp_path):
    """A minimal CLEWSInputConfig dict pointing at a temp data_dir."""
    return {
        "data_dir": str(tmp_path),
        "required_files": [],
        "region": "SSA",
        "start_year": 2025,
        "end_year": 2050,
    }


# ── Temporary CSV helpers ────────────────────────────────────────────────────

@pytest.fixture()
def simple_csv(tmp_path):
    """Creates a one-column CSV and returns its Path."""
    csv_file = tmp_path / "simple.csv"
    csv_file.write_text("year,value\n2025,100\n2026,200\n")
    return csv_file
