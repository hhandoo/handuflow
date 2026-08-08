"""Validation error code catalog for HanduFLOW."""

from __future__ import annotations

from handuflow.platform.exceptions.definition import ErrorDefinition


class ValidationErrors:
    """Validation error catalog."""

    VALIDATION_FAILED = ErrorDefinition(
        code="HF-VALIDATION-001",
        message="Validation failed.",
    )

    VALIDATION_UNKNOWN = ErrorDefinition(
        code="HF-VALIDATION-002",
        message="An unexpected error occurred during validation.",
    )

    # ---------------------------------------------------------
    # Root configuration
    # ---------------------------------------------------------

    CONFIGURATION_FILE_MISSING = ErrorDefinition(
        code="HF-VALIDATION-003",
        message="Required configuration file is missing.",
    )

    CONFIGURATION_FILE_NOT_FILE = ErrorDefinition(
        code="HF-VALIDATION-004",
        message="Configuration path is not a file.",
    )

    CONFIGURATION_FILE_READ_FAILED = ErrorDefinition(
        code="HF-VALIDATION-005",
        message="Failed to read configuration file.",
    )

    CONFIGURATION_FILE_INVALID_ENCODING = ErrorDefinition(
        code="HF-VALIDATION-006",
        message="Configuration file has an invalid encoding.",
    )

    CONFIGURATION_FILE_INVALID_INI = ErrorDefinition(
        code="HF-VALIDATION-007",
        message="Configuration file contains invalid INI syntax.",
    )

    # ---------------------------------------------------------
    # Feed configuration directory
    # ---------------------------------------------------------

    FEED_CONFIGURATION_DIR_MISSING = ErrorDefinition(
        code="HF-VALIDATION-008",
        message="Feed configuration directory is missing.",
    )

    FEED_CONFIGURATION_DIR_NOT_DIRECTORY = ErrorDefinition(
        code="HF-VALIDATION-009",
        message="Feed configuration path is not a directory.",
    )

    FEED_CONFIGURATION_YML_MISSING = ErrorDefinition(
        code="HF-VALIDATION-010",
        message="No YAML files were found under the feed configuration directory.",
    )

    FEED_CONFIGURATION_LEAF_YML_MISSING = ErrorDefinition(
        code="HF-VALIDATION-011",
        message="A leaf feed configuration directory does not contain a YAML file.",
    )

    # ---------------------------------------------------------
    # Naming
    # ---------------------------------------------------------

    DIRECTORY_NAME_INVALID = ErrorDefinition(
        code="HF-VALIDATION-012",
        message="Directory name does not follow lower snake_case.",
    )

    FILE_NAME_INVALID = ErrorDefinition(
        code="HF-VALIDATION-013",
        message="File name does not follow lower snake_case.",
    )

    CONFIGURATION_SYSTEM_NAME_MISSING = ErrorDefinition(
        code="HF-VALIDATION-014",
        message="system_name is mandatory in the DEFAULT section.",
    )

    CONFIGURATION_SYSTEM_NAME_INVALID = ErrorDefinition(
        code="HF-VALIDATION-015",
        message="system_name must contain only alphanumeric characters.",
    )

    CONFIGURATION_ENVIRONMENT_MISSING = ErrorDefinition(
        code="HF-VALIDATION-016",
        message="environment is mandatory in the DEFAULT section.",
    )

    CONFIGURATION_LOGGING_TYPE_MISSING = ErrorDefinition(
        code="HF-VALIDATION-017",
        message="Logging type is mandatory.",
    )

    CONFIGURATION_LOGGING_TYPE_INVALID = ErrorDefinition(
        code="HF-VALIDATION-018",
        message="Logging type must be either standard or rotating.",
    )

    CONFIGURATION_LOG_DIRECTORY_MISSING = ErrorDefinition(
        code="HF-VALIDATION-019",
        message="log_directory_name is mandatory.",
    )

    CONFIGURATION_LOG_FILE_MISSING = ErrorDefinition(
        code="HF-VALIDATION-020",
        message="log_file_name is mandatory.",
    )

    CONFIGURATION_DEFAULT_LOG_LEVEL_MISSING = ErrorDefinition(
        code="HF-VALIDATION-021",
        message="default_log_level is mandatory.",
    )

    CONFIGURATION_VALUE_INVALID = ErrorDefinition(
        code="HF-VALIDATION-022",
        message="Configuration value is invalid.",
    )
