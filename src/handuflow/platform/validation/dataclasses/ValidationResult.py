from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Outcome of a single validation rule."""

    validation_key: int
    validation_name: str
    passed: bool
    message: str = ""