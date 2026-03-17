"""
tests/test_file_validator.py
=============================
Tests for validator.file_validator functions.
"""
import pytest
from pathlib import Path

from validator.file_validator import (
    check_files_exist,
    check_csv_columns,
    check_csv_not_empty,
    check_csv_value_ranges,
)


# ─────────────────────────────────────────────────────────────────────────────
# check_files_exist
# ─────────────────────────────────────────────────────────────────────────────

class TestCheckFilesExist:
    def test_missing_file_returns_error_with_correct_stage_and_field(self, tmp_path):
        result = check_files_exist(tmp_path, ["missing.csv"])
        assert not result.passed
        assert len(result.errors) == 1
        err = result.errors[0]
        assert err.stage == "file_check"
        assert err.field == "missing.csv"

    def test_all_files_present_returns_passed(self, tmp_path):
        (tmp_path / "data.csv").write_text("a,b\n1,2\n")
        result = check_files_exist(tmp_path, ["data.csv"])
        assert result.passed
        assert result.errors == []

    def test_multiple_missing_files_returns_one_error_each(self, tmp_path):
        result = check_files_exist(tmp_path, ["a.csv", "b.csv", "c.csv"])
        assert not result.passed
        assert len(result.errors) == 3
        fields = {e.field for e in result.errors}
        assert fields == {"a.csv", "b.csv", "c.csv"}

    def test_empty_required_list_always_passes(self, tmp_path):
        result = check_files_exist(tmp_path, [])
        assert result.passed

    def test_mixed_present_and_missing(self, tmp_path):
        (tmp_path / "exists.csv").write_text("x\n1\n")
        result = check_files_exist(tmp_path, ["exists.csv", "nope.csv"])
        assert not result.passed
        assert len(result.errors) == 1
        assert result.errors[0].field == "nope.csv"


# ─────────────────────────────────────────────────────────────────────────────
# check_csv_columns
# ─────────────────────────────────────────────────────────────────────────────

class TestCheckCsvColumns:
    def test_all_columns_present_passes(self, simple_csv):
        result = check_csv_columns(simple_csv, ["year", "value"])
        assert result.passed

    def test_missing_column_returns_correct_error(self, simple_csv):
        result = check_csv_columns(simple_csv, ["year", "value", "region"])
        assert not result.passed
        assert any(e.field == "region" for e in result.errors)
        assert result.errors[0].stage == "file_check"

    def test_no_expected_columns_always_passes(self, simple_csv):
        result = check_csv_columns(simple_csv, [])
        assert result.passed

    def test_nonexistent_csv_returns_error(self, tmp_path):
        result = check_csv_columns(tmp_path / "ghost.csv", ["col"])
        assert not result.passed
        assert result.errors[0].stage == "file_check"


# ─────────────────────────────────────────────────────────────────────────────
# check_csv_not_empty
# ─────────────────────────────────────────────────────────────────────────────

class TestCheckCsvNotEmpty:
    def test_non_empty_csv_passes(self, simple_csv):
        assert check_csv_not_empty(simple_csv).passed

    def test_header_only_csv_fails(self, tmp_path):
        f = tmp_path / "empty.csv"
        f.write_text("col1,col2\n")
        result = check_csv_not_empty(f)
        assert not result.passed
        assert "0 rows" in result.errors[0].received

    def test_nonexistent_file_returns_error(self, tmp_path):
        result = check_csv_not_empty(tmp_path / "nope.csv")
        assert not result.passed


# ─────────────────────────────────────────────────────────────────────────────
# check_csv_value_ranges
# ─────────────────────────────────────────────────────────────────────────────

class TestCheckCsvValueRanges:
    def test_values_in_range_passes(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("x\n0.5\n0.7\n0.1\n")
        assert check_csv_value_ranges(f, "x", 0.0, 1.0).passed

    def test_out_of_range_value_fails(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("x\n0.5\n2.0\n0.1\n")
        result = check_csv_value_ranges(f, "x", 0.0, 1.0)
        assert not result.passed
        assert any("outside" in e.message for e in result.errors)

    def test_missing_column_returns_error(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("y\n1\n2\n")
        result = check_csv_value_ranges(f, "x", 0, 10)
        assert not result.passed
        assert result.errors[0].field == "x"
