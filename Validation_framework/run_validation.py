#!/usr/bin/env python
"""
run_validation.py
==================
CLI entrypoint for the Validation Framework.

Usage examples::

    # Validate an OG-Core config, print coloured terminal output
    python run_validation.py --model og --config sample_data/valid_og_config.json

    # Also check that required files exist in a data directory
    python run_validation.py --model og --config sample_data/valid_og_config.json \\
        --data-dir ./data --required-files TotalCapacity.csv Production.csv

    # Output as JSON (for API integration)
    python run_validation.py --model og --config sample_data/invalid_og_config.json \\
        --output-format ui

    # Output as flat log string
    python run_validation.py --model clews --config my_clews.json --output-format log

Exit codes:
    0 — all validation checks passed
    1 — one or more validation errors found
    2 — argument or I/O error (bad path, unreadable JSON, etc.)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validator.error_formatter import format_for_log, format_for_terminal, format_for_ui
from validator.file_validator import check_files_exist
from validator.models import ValidationError, ValidationResult
from validator.schema_validator import validate_clews_config, validate_og_config


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _merge_results(*results: ValidationResult) -> ValidationResult:
    """Merge multiple ValidationResult objects into one."""
    all_errors: list[ValidationError] = []
    all_warnings: list[str] = []
    for r in results:
        all_errors.extend(r.errors)
        all_warnings.extend(r.warnings)
    return ValidationResult(
        passed=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings,
    )


def _load_json(path: str) -> tuple[dict | None, str | None]:
    """Return (parsed dict, None) on success or (None, error message) on failure."""
    try:
        with open(path) as fh:
            return json.load(fh), None
    except FileNotFoundError:
        return None, f"Config file not found: {path}"
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON in '{path}': {exc}"
    except Exception as exc:  # noqa: BLE001
        return None, f"Cannot read config: {exc}"


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_validation",
        description="Validate CLEWS or OG-Core config files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--model",
        choices=["og", "clews"],
        required=True,
        help="Which model config to validate.",
    )
    parser.add_argument(
        "--config",
        required=True,
        metavar="PATH",
        help="Path to the JSON config file.",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        metavar="PATH",
        help="(Optional) Directory to check for required data files.",
    )
    parser.add_argument(
        "--required-files",
        nargs="*",
        default=[],
        metavar="FILE",
        help="Filenames that must exist inside --data-dir.",
    )
    parser.add_argument(
        "--output-format",
        choices=["terminal", "ui", "log"],
        default="terminal",
        help="How to format the output (default: terminal).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # 1. Load config JSON ──────────────────────────────────────────────────────
    config_dict, load_err = _load_json(args.config)
    if load_err:
        print(f"ERROR: {load_err}", file=sys.stderr)
        return 2

    results: list[ValidationResult] = []

    # 2. File checks (optional) ────────────────────────────────────────────────
    if args.data_dir:
        file_result = check_files_exist(
            data_dir=Path(args.data_dir),
            required_files=args.required_files,
        )
        results.append(file_result)

    # 3. Schema validation ─────────────────────────────────────────────────────
    if args.model == "og":
        schema_result = validate_og_config(config_dict)
    else:
        schema_result = validate_clews_config(config_dict)
    results.append(schema_result)

    # 4. Merge & format ────────────────────────────────────────────────────────
    final = _merge_results(*results)

    if args.output_format == "terminal":
        print(format_for_terminal(final))
    elif args.output_format == "ui":
        print(json.dumps(format_for_ui(final), indent=2))
    else:  # log
        print(format_for_log(final))

    return 0 if final.passed else 1


if __name__ == "__main__":
    sys.exit(main())
