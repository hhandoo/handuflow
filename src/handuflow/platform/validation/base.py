"""Base validation contracts for HanduFLOW."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .dataclasses import ValidationResult


class Validation(ABC):
    """Abstract base class for HanduFLOW validation rules."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stable identifier for this validation."""

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Execute the validation and return its outcome.

        Raises:
            ValidationError: When the validation rule is not satisfied.
        """
