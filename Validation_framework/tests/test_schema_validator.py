"""
tests/test_schema_validator.py
================================
Tests for validator.schema_validator functions.
"""
import pytest

from validator.schema_validator import (
    validate_og_config,
    validate_clews_config,
    validate_exchange_params,
)


# ─────────────────────────────────────────────────────────────────────────────
# validate_og_config
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateOgConfig:
    def test_valid_config_passes(self, valid_og_config):
        result = validate_og_config(valid_og_config)
        assert result.passed
        assert result.errors == []

    def test_out_of_range_maxiter_returns_error_with_field_name(self):
        cfg = {
            "scenario_name": "test",
            "country_module": "og_usa.calibrate",
            "time_path": True,
            "start_year": 2025,
            "og_spec": {"maxiter": 5000},
        }
        result = validate_og_config(cfg)
        assert not result.passed
        # error must mention "maxiter"
        assert any("maxiter" in e.field for e in result.errors), (
            f"Expected 'maxiter' in error fields, got: {[e.field for e in result.errors]}"
        )

    def test_missing_required_field_returns_error(self):
        """start_year is required — omitting it must produce a schema error."""
        cfg = {
            "scenario_name": "test",
            "country_module": "og_usa.calibrate",
            "time_path": True,
            # start_year deliberately omitted
        }
        result = validate_og_config(cfg)
        assert not result.passed
        assert any("start_year" in e.field for e in result.errors)

    def test_invalid_config_from_sample_file_fails(self, invalid_og_config):
        """The sample invalid file must produce at least two errors."""
        result = validate_og_config(invalid_og_config)
        assert not result.passed
        assert len(result.errors) >= 2

    def test_out_of_range_nu_returns_error(self):
        cfg = {
            "scenario_name": "test",
            "country_module": "og_usa.calibrate",
            "time_path": False,
            "start_year": 2030,
            "og_spec": {"nu": 1.5},
        }
        result = validate_og_config(cfg)
        assert not result.passed
        assert any("nu" in e.field for e in result.errors)

    def test_never_raises_on_garbage_input(self):
        result = validate_og_config({"x": object()})
        assert not result.passed


# ─────────────────────────────────────────────────────────────────────────────
# validate_clews_config
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateClewsConfig:
    def test_valid_config_passes(self, valid_clews_config):
        result = validate_clews_config(valid_clews_config)
        assert result.passed

    def test_missing_region_fails(self, valid_clews_config):
        del valid_clews_config["region"]
        result = validate_clews_config(valid_clews_config)
        assert not result.passed
        assert any("region" in e.field for e in result.errors)

    def test_end_year_before_start_year_fails(self, valid_clews_config):
        valid_clews_config["end_year"] = valid_clews_config["start_year"] - 1
        result = validate_clews_config(valid_clews_config)
        assert not result.passed

    def test_never_raises_on_empty_dict(self):
        result = validate_clews_config({})
        assert not result.passed


# ─────────────────────────────────────────────────────────────────────────────
# validate_exchange_params
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateExchangeParams:
    def _good(self):
        return {
            "delta_tau_annual": 0.05,
            "tau_c": 0.25,
            "alpha_G": [0.0, 0.3, 0.7, 1.0],
        }

    def test_valid_params_pass(self):
        assert validate_exchange_params(self._good()).passed

    def test_negative_tau_c_fails(self):
        p = self._good()
        p["tau_c"] = -0.1
        result = validate_exchange_params(p)
        assert not result.passed
        assert any("tau_c" in e.field for e in result.errors)

    def test_delta_tau_annual_zero_fails(self):
        p = self._good()
        p["delta_tau_annual"] = 0.0
        result = validate_exchange_params(p)
        assert not result.passed
        assert any("delta_tau_annual" in e.field for e in result.errors)

    def test_alpha_g_out_of_range_fails(self):
        p = self._good()
        p["alpha_G"] = [0.5, 1.5, -0.1]
        result = validate_exchange_params(p)
        assert not result.passed
        assert any("alpha_G" in e.field for e in result.errors)

    def test_missing_all_keys_returns_three_errors(self):
        result = validate_exchange_params({})
        assert not result.passed
        assert len(result.errors) == 3

    def test_alpha_g_not_a_list_fails(self):
        p = self._good()
        p["alpha_G"] = "not-a-list"
        result = validate_exchange_params(p)
        assert not result.passed
