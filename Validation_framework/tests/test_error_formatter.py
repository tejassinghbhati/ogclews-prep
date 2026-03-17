"""
tests/test_error_formatter.py
================================
Tests for validator.error_formatter formatting functions.
"""
import json
import pytest

from validator.models import ValidationError, ValidationResult
from validator.error_formatter import format_for_terminal, format_for_ui, format_for_log


# ─── helpers ──────────────────────────────────────────────────────────────────

def _make_error(field="og_spec → maxiter", message="Value too large") -> ValidationError:
    return ValidationError(
        stage="schema",
        field=field,
        message=message,
        expected="<= 1000",
        received="5000",
    )


def _pass_result():
    return ValidationResult.ok()


def _fail_result(n=2):
    return ValidationResult.fail(
        [_make_error(field=f"field_{i}") for i in range(n)],
        warnings=["This is a warning"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# format_for_ui
# ─────────────────────────────────────────────────────────────────────────────

class TestFormatForUi:
    def test_returns_json_serializable_dict(self):
        result = _fail_result()
        ui = format_for_ui(result)
        serialized = json.dumps(ui)          # must not raise
        assert isinstance(serialized, str)

    def test_passed_result_has_empty_errors_list(self):
        ui = format_for_ui(_pass_result())
        assert ui["passed"] is True
        assert ui["errors"] == []
        assert ui["error_count"] == 0

    def test_failed_result_has_correct_error_count(self):
        ui = format_for_ui(_fail_result(3))
        assert ui["passed"] is False
        assert ui["error_count"] == 3
        assert len(ui["errors"]) == 3

    def test_error_entries_have_required_keys(self):
        ui = format_for_ui(_fail_result(1))
        required_keys = {"field", "message", "expected", "received"}
        for entry in ui["errors"]:
            assert required_keys.issubset(entry.keys())

    def test_all_values_are_json_native_types(self):
        """No Python-specific types (Path, dataclass, etc.) should appear."""
        ui = format_for_ui(_fail_result(2))
        # json.dumps raises for non-serialisable types
        json.dumps(ui)

    def test_warnings_included_in_output(self):
        ui = format_for_ui(_fail_result(1))
        assert "This is a warning" in ui["warnings"]


# ─────────────────────────────────────────────────────────────────────────────
# format_for_terminal
# ─────────────────────────────────────────────────────────────────────────────

class TestFormatForTerminal:
    def test_passed_result_contains_checkmark(self):
        output = format_for_terminal(_pass_result())
        assert "PASSED" in output or "✔" in output

    def test_failed_result_contains_field_name(self):
        result = ValidationResult.fail([_make_error(field="og_spec → maxiter")])
        output = format_for_terminal(result)
        assert "og_spec → maxiter" in output

    def test_failed_result_contains_all_errors(self):
        result = _fail_result(3)
        output = format_for_terminal(result)
        for i in range(3):
            assert f"field_{i}" in output


# ─────────────────────────────────────────────────────────────────────────────
# format_for_log
# ─────────────────────────────────────────────────────────────────────────────

class TestFormatForLog:
    def test_passed_log_starts_with_passed(self):
        log = format_for_log(_pass_result())
        assert log.startswith("PASSED")

    def test_failed_log_starts_with_failed(self):
        log = format_for_log(_fail_result(2))
        assert log.startswith("FAILED")

    def test_log_is_single_line(self):
        log = format_for_log(_fail_result(5))
        assert "\n" not in log

    def test_error_count_in_log(self):
        log = format_for_log(_fail_result(4))
        assert "errors=4" in log

    def test_field_name_in_log(self):
        result = ValidationResult.fail([_make_error(field="tau_c")])
        log = format_for_log(result)
        assert "tau_c" in log
