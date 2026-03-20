"""
validator/schema_validator.py
==============================
Config-dict validation against Pydantic models and business-logic rules.

All public functions return a :class:`ValidationResult` and **never raise**.
Pydantic errors are caught and translated into :class:`ValidationError` entries.
"""
from __future__ import annotations

from typing import Any

from pydantic import ValidationError as PydanticValidationError

from .models import CLEWSInputConfig, OGInputConfig, ValidationError, ValidationResult


_STAGE_SCHEMA = "schema"
_STAGE_EXCHANGE = "exchange"


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _pydantic_errors_to_validation_errors(
    exc: PydanticValidationError, stage: str
) -> list[ValidationError]:
    """Convert every Pydantic ValidationError entry into our own dataclass."""
    result: list[ValidationError] = []
    for err in exc.errors():
        # loc is a tuple of field-path segments, e.g. ("og_spec", "maxiter")
        field_path = " → ".join(str(loc) for loc in err["loc"]) if err["loc"] else "<root>"
        result.append(
            ValidationError(
                stage=stage,
                field=field_path,
                message=err["msg"],
                expected=str(err.get("ctx", {}).get("expected", "see message")),
                received=str(err.get("input", "<unknown>")),
            )
        )
    return result


def _make_err(stage: str, field: str, message: str, expected: str, received: str) -> ValidationError:
    return ValidationError(stage=stage, field=field, message=message, expected=expected, received=received)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def validate_og_config(config_dict: dict[str, Any]) -> ValidationResult:
    """Validate an OG-Core config dict against :class:`OGInputConfig`.

    Returns a :class:`ValidationResult` — never raises.
    """
    try:
        OGInputConfig(**config_dict)
        return ValidationResult.ok()
    except PydanticValidationError as exc:
        return ValidationResult.fail(_pydantic_errors_to_validation_errors(exc, _STAGE_SCHEMA))
    except Exception as exc:  # noqa: BLE001
        return ValidationResult.fail(
            [_make_err(_STAGE_SCHEMA, "<config>", f"Unexpected error: {exc}", "Valid OG config dict", type(exc).__name__)]
        )


def validate_clews_config(config_dict: dict[str, Any]) -> ValidationResult:
    """Validate a CLEWS config dict against :class:`CLEWSInputConfig`.

    Returns a :class:`ValidationResult` — never raises.
    """
    try:
        CLEWSInputConfig(**config_dict)
        return ValidationResult.ok()
    except PydanticValidationError as exc:
        return ValidationResult.fail(_pydantic_errors_to_validation_errors(exc, _STAGE_SCHEMA))
    except Exception as exc:  # noqa: BLE001
        return ValidationResult.fail(
            [_make_err(_STAGE_SCHEMA, "<config>", f"Unexpected error: {exc}", "Valid CLEWS config dict", type(exc).__name__)]
        )


def validate_exchange_params(params_dict: dict[str, Any]) -> ValidationResult:
    """Validate the ``og_exchange.json`` output from the ETL pipeline.

    Checks:
    - ``delta_tau_annual`` in the open interval (0, 1)
    - ``tau_c`` >= 0
    - ``alpha_G`` is a list with all values in [0, 1]

    Returns a :class:`ValidationResult` — never raises.
    """
    errors: list[ValidationError] = []

    # ── delta_tau_annual ──────────────────────────────────────────────────────
    if "delta_tau_annual" not in params_dict:
        errors.append(_make_err(
            _STAGE_EXCHANGE, "delta_tau_annual",
            "Missing required field 'delta_tau_annual'.",
            "float in (0, 1)", "<missing>",
        ))
    else:
        try:
            val = float(params_dict["delta_tau_annual"])
            if not (0 < val < 1):
                errors.append(_make_err(
                    _STAGE_EXCHANGE, "delta_tau_annual",
                    f"'delta_tau_annual' must be strictly between 0 and 1, got {val}.",
                    "0 < delta_tau_annual < 1", str(val),
                ))
        except (TypeError, ValueError):
            errors.append(_make_err(
                _STAGE_EXCHANGE, "delta_tau_annual",
                "'delta_tau_annual' must be a numeric value.",
                "float in (0, 1)", str(params_dict["delta_tau_annual"]),
            ))

    # ── tau_c ─────────────────────────────────────────────────────────────────
    if "tau_c" not in params_dict:
        errors.append(_make_err(
            _STAGE_EXCHANGE, "tau_c",
            "Missing required field 'tau_c'.",
            "float >= 0", "<missing>",
        ))
    else:
        try:
            val = float(params_dict["tau_c"])
            if val < 0:
                errors.append(_make_err(
                    _STAGE_EXCHANGE, "tau_c",
                    f"'tau_c' must be >= 0, got {val}.",
                    "tau_c >= 0", str(val),
                ))
        except (TypeError, ValueError):
            errors.append(_make_err(
                _STAGE_EXCHANGE, "tau_c",
                "'tau_c' must be a numeric value.",
                "float >= 0", str(params_dict["tau_c"]),
            ))

    # ── alpha_G ───────────────────────────────────────────────────────────────
    if "alpha_G" not in params_dict:
        errors.append(_make_err(
            _STAGE_EXCHANGE, "alpha_G",
            "Missing required field 'alpha_G'.",
            "list of floats in [0, 1]", "<missing>",
        ))
    else:
        alpha_g = params_dict["alpha_G"]
        if not isinstance(alpha_g, list):
            errors.append(_make_err(
                _STAGE_EXCHANGE, "alpha_G",
                "'alpha_G' must be a list.",
                "list of floats in [0, 1]", type(alpha_g).__name__,
            ))
        else:
            bad: list[Any] = []
            for item in alpha_g:
                try:
                    v = float(item)
                    if not (0.0 <= v <= 1.0):
                        bad.append(item)
                except (TypeError, ValueError):
                    bad.append(item)
            if bad:
                errors.append(_make_err(
                    _STAGE_EXCHANGE, "alpha_G",
                    f"'alpha_G' contains values outside [0, 1]: {bad[:5]}",
                    "All values in [0, 1]", str(bad[:5]),
                ))

    return ValidationResult.fail(errors) if errors else ValidationResult.ok()
