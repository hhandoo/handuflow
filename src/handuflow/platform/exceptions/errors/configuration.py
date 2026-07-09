"""Configuration error code catalog for HanduFLOW."""

from __future__ import annotations

from handuflow.platform.exceptions.definition import ErrorDefinition


class ConfigurationErrors:
    """
    Configuration Error Catalog.
    """

    MISSING_HANDUFLOW_DIRECTORY = ErrorDefinition(
        code="HF-CONFIGURATION-001",
        message="Missing HanduFLOW directory path.",
    )

    READ_CONFIGURATION_ERROR = ErrorDefinition(
        code="HF-CONFIGURATION-002",
        message="Something went wrong while reading configuration file.",
    )
    LOGGER_ERROR = ErrorDefinition(
        code="HF-CONFIGURATION-003",
        message="Something went wrong while creating the logger.",
    )

    UNKNOWN_CONFIGURATION_ERROR = ErrorDefinition(
        code="HF-CONFIGURATION-004",
        message="Unknown configuration error.",
    )