"""Driver for executing HanduFLOW validation rules."""

from __future__ import annotations
from .base import Validation
from ..exceptions.domains.validation import ValidationError
from ..exceptions.errors.validation import ValidationErrors
from ..exceptions import HanduflowError
from .dataclasses import ValidationResult
from .validations import VALIDATIONS
from ..configurator.dataclasses.context import ConfigurationContext


class ValidationRunner:
    """Run registered validations and collect their outc"""

    def __init__(self, configuration_context: ConfigurationContext) -> None:
        self._configuration_context = configuration_context
        self._validations = VALIDATIONS

    def add_validation(self, validation: Validation) -> None:
        self._validations.append(validation)

    def run(self, *, raise_on_failure: bool = False) -> list[ValidationResult]:
        """Execute all registered validations."""
        logger = self._configuration_context.logging.logger
        results: list[ValidationResult] = []
        failures: list[ValidationError] = []
        total = len(self._validations)

        for index, validation in enumerate(self._validations, start=1):
            try:
                result = validation.validate(self._configuration_context)
                results.append(result)
                logger.info(
                    "VALIDATION [%d/%d]: %s : PASSED",
                    index,
                    total,
                    validation.name,
                )
            except ValidationError as exc:
                failures.append(exc)
                results.append(
                    ValidationResult(
                        validation.key,
                        validation.name,
                        False,
                        exc.message,
                    )
                )
                logger.error(
                    "VALIDATION [%d/%d]: %s : FAILED",
                    index,
                    total,
                    validation.name,
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
                        validation.key,
                        validation.name,
                        False,
                        error.message,
                    )
                )
                logger.error(
                    "VALIDATION [%d/%d]: %s : FAILED",
                    index,
                    total,
                    validation.name,
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
