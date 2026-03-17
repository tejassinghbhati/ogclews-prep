"""
validator/models.py
===================
Pydantic models and plain dataclasses used throughout the validation framework.

All validation-domain types live here so they can be imported by any other
module without creating circular dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# Dataclasses — lightweight result / error containers
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ValidationError:
    """Single validation failure with rich context."""
    stage: str        # e.g. "file_check", "schema", "exchange"
    field: str        # field or filename that failed
    message: str      # human-readable description
    expected: str     # what was expected
    received: str     # what was actually found

    def to_dict(self) -> dict[str, str]:
        return {
            "stage": self.stage,
            "field": self.field,
            "message": self.message,
            "expected": self.expected,
            "received": self.received,
        }


@dataclass
class ValidationResult:
    """Aggregated outcome of one or more validation checks."""
    passed: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": list(self.warnings),
        }

    # convenience ─────────────────────────────────────────────────────────────
    @classmethod
    def ok(cls, warnings: list[str] | None = None) -> "ValidationResult":
        return cls(passed=True, errors=[], warnings=warnings or [])

    @classmethod
    def fail(
        cls,
        errors: list[ValidationError],
        warnings: list[str] | None = None,
    ) -> "ValidationResult":
        return cls(passed=False, errors=errors, warnings=warnings or [])


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────────────────────────────────────

class OGSpecParams(BaseModel):
    """
    Nested model for the ``og_spec`` sub-dict inside OGInputConfig.
    All fields are optional; only those present are validated.
    """
    model_config = {"extra": "allow"}   # allow unknown OG-Core keys

    maxiter: int | None = Field(
        default=None,
        ge=1,
        le=1000,
        description="Maximum iterations for SS/TPI solver.",
    )
    mindist_SS: float | None = Field(
        default=None,
        ge=1e-12,
        le=1.0,
        description="Minimum distance criterion for SS convergence.",
    )
    nu: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Coefficient of updating in TPI.",
    )


class OGInputConfig(BaseModel):
    """Top-level config for an OG-Core model run."""
    scenario_name: str = Field(..., description="Unique label for this run.")
    country_module: str = Field(
        ..., description="Python import path of the country calibration module."
    )
    time_path: bool = Field(
        ..., description="Whether to compute the full transition path."
    )
    start_year: int = Field(
        ...,
        ge=2020,
        le=2100,
        description="First year of the simulation.",
    )
    og_spec: OGSpecParams = Field(
        default_factory=OGSpecParams,
        description="OG-Core parameter overrides.",
    )

    @model_validator(mode="after")
    def _start_year_sanity(self) -> "OGInputConfig":
        # Placeholder for any cross-field checks; extend as needed.
        return self


class CLEWSInputConfig(BaseModel):
    """Top-level config for a CLEWS model run."""
    data_dir: Path = Field(..., description="Directory containing CLEWS data files.")
    required_files: list[str] = Field(
        default_factory=list,
        description="File names that must exist inside data_dir.",
    )
    region: str = Field(..., description="Geographic region identifier.")
    start_year: int = Field(..., ge=2020, le=2100, description="Simulation start year.")
    end_year: int = Field(..., description="Simulation end year.")

    @field_validator("end_year")
    @classmethod
    def _end_after_start(cls, v: int, info: Any) -> int:
        start = (info.data or {}).get("start_year")
        if start is not None and v < start:
            raise ValueError(
                f"end_year ({v}) must be >= start_year ({start})."
            )
        return v
