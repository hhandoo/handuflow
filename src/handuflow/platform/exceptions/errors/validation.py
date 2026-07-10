"""Validation error code catalog for HanduFLOW."""

from __future__ import annotations

from handuflow.platform.exceptions.definition import ErrorDefinition


class ValidationErrors:
    """
    Validation error catalog.
    """

    VALIDATION_FAILED = ErrorDefinition(
        code="HF-VALIDATION-001",
        message="Validation failed.",
    )

    VALIDATION_UNKNOWN = ErrorDefinition(
        code="HF-VALIDATION-002",
        message="Something went wrong while performing validation.",
    )
