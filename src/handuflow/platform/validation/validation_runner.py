"""Driver for executing HanduFLOW validation rules."""

from __future__ import annotations

from ..exceptions.base import HanduflowError
from ..exceptions.domains.validation import ValidationError
from ..exceptions.errors.validation import ValidationErrors
from .base import Validation
from .dataclasses import ValidationResult
from .validations import VALIDATIONS
from ..configurator.dataclasses.context import ConfigurationContext


class ValidationRunner:
    """Run registered validations and collect their outcom"""

    def __init__(self, validations: list[Validation], configuration_context: ConfigurationContext) -> None:
        self._configuration_context = configuration_context
        self._validations = VALIDATIONS

    def run(self, *, raise_on_failure: bool = False) -> list[ValidationResult]:
        """Execute all registered validations."""
        results: list[ValidationResult] = []
        failures: list[ValidationError] = []

        for validation in self._validations:
            try:
                results.append(validation.validate())
            except ValidationError as exc:
                failures.append(exc)
                results.append(
                    ValidationResult(
                        validation.name,
                        False,
                        exc.message,
                    )
                )
            except HanduflowError:
                raise
            except Exception as exc:
                error = ValidationError(
                    ValidationErrors.VALIDATION_UNKNOWN,
                    validation_name=validation.name,
                    cause=exc,
                )
                failures.append(error)
                results.append(
                    ValidationResult(
                        validation.name,
                        False,
                        error.message,
                    )
                )

        if raise_on_failure and failures:
            if len(failures) == 1:
                raise failures[0]
            raise ValidationError(
                ValidationErrors.VALIDATION_FAILED,
                failure_count=len(failures),
                failures=[failure.to_dict() for failure in failures],
            )

        return results

    def all_passed(self) -> bool:
        """Return True when every registered validation passes."""
        return all(result.passed for result in self.run())
