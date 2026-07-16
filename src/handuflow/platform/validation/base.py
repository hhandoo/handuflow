"""Base validation contracts for HanduFLOW."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .dataclasses import ValidationResult
from ..configurator.dataclasses.context import ConfigurationContext


class Validation(ABC):
    """Abstract base class for HanduFLOW validation rules."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stable identifier for this validation."""

    @property
    @abstractmethod
    def key(self) -> int:
        """Return the stable identifier key for this validation."""

    @abstractmethod
    def validate(self, configuration_context: ConfigurationContext) -> ValidationResult:
        """Execute the validation and return its outcome.

        Raises:
            ValidationError: When the validation rule is not satisfied.
        """
