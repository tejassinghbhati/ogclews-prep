"""
validator/error_formatter.py
=============================
Formats a :class:`ValidationResult` for three different consumers:

* Terminal output  — coloured text for developers running CLI tools
* UI (JSON) output — clean dict for Flask / REST API responses
* Log output       — flat single-line string for log files
"""
from __future__ import annotations

import json

from colorama import Fore, Style, init as colorama_init

from .models import ValidationResult


# Ensure Windows terminals also get ANSI colour codes
colorama_init(autoreset=True)


# ─────────────────────────────────────────────────────────────────────────────
# format_for_terminal
# ─────────────────────────────────────────────────────────────────────────────

def format_for_terminal(result: ValidationResult) -> str:
    """Return a coloured string suitable for printing to a terminal.

    * Green checkmark on pass.
    * Red ``✗`` per error with field name and message.
    * Yellow warnings (if any).
    """
    lines: list[str] = []

    if result.passed:
        lines.append(f"{Fore.GREEN}✔ Validation PASSED — all checks OK.{Style.RESET_ALL}")
    else:
        lines.append(
            f"{Fore.RED}✗ Validation FAILED — {len(result.errors)} error(s) found.{Style.RESET_ALL}"
        )
        for err in result.errors:
            lines.append(
                f"  {Fore.RED}✗{Style.RESET_ALL} [{err.stage}] "
                f"{Fore.YELLOW}{err.field}{Style.RESET_ALL}: "
                f"{err.message}"
            )
            lines.append(
                f"      expected : {err.expected}"
            )
            lines.append(
                f"      received : {err.received}"
            )

    for warning in result.warnings:
        lines.append(f"  {Fore.YELLOW}⚠ WARNING:{Style.RESET_ALL} {warning}")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# format_for_ui
# ─────────────────────────────────────────────────────────────────────────────

def format_for_ui(result: ValidationResult) -> dict:
    """Return a fully JSON-serialisable dict for Flask / REST API consumers.

    Schema::

        {
            "passed": bool,
            "error_count": int,
            "errors": [
                {
                    "field": str,
                    "message": str,
                    "expected": str,
                    "received": str
                },
                ...
            ],
            "warnings": [str, ...]
        }

    No Python-specific types (Path, dataclass, etc.) are present.
    """
    errors_list = [
        {
            "field": str(err.field),
            "message": str(err.message),
            "expected": str(err.expected),
            "received": str(err.received),
        }
        for err in result.errors
    ]

    payload: dict = {
        "passed": bool(result.passed),
        "error_count": len(errors_list),
        "errors": errors_list,
        "warnings": [str(w) for w in result.warnings],
    }

    # Sanity check — guarantee JSON-serialisability
    json.dumps(payload)   # will raise if any non-serialisable type slips through
    return payload


# ─────────────────────────────────────────────────────────────────────────────
# format_for_log
# ─────────────────────────────────────────────────────────────────────────────

def format_for_log(result: ValidationResult) -> str:
    """Return a flat single-line string suitable for writing to a log file.

    Format::

        PASSED | errors=0 | warnings=0
        FAILED | errors=3 | warnings=1 | [schema] og_spec → maxiter: Input should be less than or equal to 1000 | ...
    """
    status = "PASSED" if result.passed else "FAILED"
    parts = [
        status,
        f"errors={len(result.errors)}",
        f"warnings={len(result.warnings)}",
    ]
    for err in result.errors:
        parts.append(f"[{err.stage}] {err.field}: {err.message}")
    for w in result.warnings:
        parts.append(f"[WARNING] {w}")

    return " | ".join(parts)
