"""
validator/file_validator.py
============================
Physical file-system and CSV structure checks.

All public functions return a :class:`ValidationResult` and **never raise**.
Any I/O or parsing exception is caught and converted into a
:class:`ValidationError` with ``stage="file_check"``.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import ValidationError, ValidationResult


_STAGE = "file_check"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_error(field: str, message: str, expected: str, received: str) -> ValidationError:
    return ValidationError(
        stage=_STAGE,
        field=field,
        message=message,
        expected=expected,
        received=received,
    )


def _read_csv_safe(filepath: Path | str) -> tuple[pd.DataFrame | None, ValidationError | None]:
    """Return (DataFrame, None) on success or (None, error) on failure."""
    try:
        df = pd.read_csv(filepath)
        return df, None
    except Exception as exc:  # noqa: BLE001
        err = _make_error(
            field=str(filepath),
            message=f"Could not read CSV: {exc}",
            expected="A readable CSV file",
            received=type(exc).__name__,
        )
        return None, err


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def check_files_exist(
    data_dir: Path | str,
    required_files: list[str],
) -> ValidationResult:
    """Check that every name in *required_files* exists inside *data_dir*.

    Returns one :class:`ValidationError` per missing file.
    """
    try:
        data_dir = Path(data_dir)
    except Exception as exc:  # noqa: BLE001
        return ValidationResult.fail(
            [_make_error("data_dir", f"Invalid path: {exc}", "A valid directory path", str(data_dir))]
        )

    errors: list[ValidationError] = []

    for filename in required_files:
        target = data_dir / filename
        if not target.exists():
            errors.append(
                _make_error(
                    field=filename,
                    message=f"Required file '{filename}' not found in '{data_dir}'.",
                    expected=str(target),
                    received="<missing>",
                )
            )

    return ValidationResult.fail(errors) if errors else ValidationResult.ok()


def check_csv_columns(
    filepath: Path | str,
    expected_columns: list[str],
) -> ValidationResult:
    """Check that all *expected_columns* are present in the CSV header."""
    df, err = _read_csv_safe(filepath)
    if err:
        return ValidationResult.fail([err])

    actual_cols = set(df.columns.tolist())
    missing = [c for c in expected_columns if c not in actual_cols]

    if missing:
        errors = [
            _make_error(
                field=col,
                message=f"Column '{col}' is missing from '{filepath}'.",
                expected=col,
                received=f"Available columns: {sorted(actual_cols)}",
            )
            for col in missing
        ]
        return ValidationResult.fail(errors)

    return ValidationResult.ok()


def check_csv_not_empty(filepath: Path | str) -> ValidationResult:
    """Check that the CSV contains at least one data row (excluding header)."""
    df, err = _read_csv_safe(filepath)
    if err:
        return ValidationResult.fail([err])

    if df.empty:
        return ValidationResult.fail(
            [
                _make_error(
                    field=str(filepath),
                    message=f"CSV file '{filepath}' has no data rows.",
                    expected="At least 1 data row",
                    received="0 rows",
                )
            ]
        )

    return ValidationResult.ok()


def check_csv_value_ranges(
    filepath: Path | str,
    column: str,
    min_val: float,
    max_val: float,
) -> ValidationResult:
    """Check that every value in *column* satisfies *min_val* <= v <= *max_val*."""
    df, err = _read_csv_safe(filepath)
    if err:
        return ValidationResult.fail([err])

    if column not in df.columns:
        return ValidationResult.fail(
            [
                _make_error(
                    field=column,
                    message=f"Column '{column}' not found in '{filepath}'.",
                    expected=column,
                    received=f"Available: {df.columns.tolist()}",
                )
            ]
        )

    try:
        series = pd.to_numeric(df[column], errors="coerce")
    except Exception as exc:  # noqa: BLE001
        return ValidationResult.fail(
            [_make_error(column, f"Cannot coerce column to numeric: {exc}", "Numeric values", "Non-numeric data")]
        )

    non_null = series.dropna()
    out_of_range = non_null[(non_null < min_val) | (non_null > max_val)]

    errors: list[ValidationError] = []

    if series.isna().any():
        errors.append(
            _make_error(
                field=column,
                message=f"Column '{column}' contains non-numeric or null values.",
                expected="All numeric values",
                received="Some NaN / non-numeric entries",
            )
        )

    if not out_of_range.empty:
        bad_vals = out_of_range.tolist()[:5]  # show first 5
        errors.append(
            _make_error(
                field=column,
                message=(
                    f"Column '{column}' has values outside [{min_val}, {max_val}]. "
                    f"First offenders: {bad_vals}"
                ),
                expected=f"All values in [{min_val}, {max_val}]",
                received=str(bad_vals),
            )
        )

    return ValidationResult.fail(errors) if errors else ValidationResult.ok()
