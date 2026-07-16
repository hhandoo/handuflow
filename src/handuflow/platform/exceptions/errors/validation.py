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

    FEED_CONFIGURATION_DIR_MISSING = ErrorDefinition(
        code="HF-VALIDATION-003",
        message="Feed configuration directory is missing.",
    )

    FEED_CONFIGURATION_DIR_NOT_DIRECTORY = ErrorDefinition(
        code="HF-VALIDATION-004",
        message="Feed configuration path is not a directory.",
    )

    FEED_CONFIGURATION_FILE_READ_FAILED = ErrorDefinition(
        code="HF-VALIDATION-005",
        message="Failed to read feed configuration yml file.",
    )

    FEED_CONFIGURATION_INVALID_YML = ErrorDefinition(
        code="HF-VALIDATION-006",
        message="Feed configuration yml file is invalid.",
    )

    FEED_CONFIGURATION_INVALID_STRUCTURE = ErrorDefinition(
        code="HF-VALIDATION-007",
        message="Feed configuration yml structure is invalid.",
    )

    FEED_CONFIGURATION_VALIDATION_FAILED = ErrorDefinition(
        code="HF-VALIDATION-008",
        message="Feed configuration validation failed.",
    )
