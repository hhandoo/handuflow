"""Simple validation for testing the validation runner."""

from __future__ import annotations

from ..base import Validation
from ..dataclasses import ValidationResult


class PrintValidation(Validation):
    """Print a message and pass."""

    @property
    def name(self) -> str:
        return "print_validation"

    def validate(self) -> ValidationResult:
        print("Running print validation.")
        return ValidationResult(
            self.name,
            True,
            "Print validation completed.",
        )
