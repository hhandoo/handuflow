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

    FEED_CONFIGURATION_FILE_READ_FAILED = ErrorDefinition(
        code="HF-VALIDATION-005",
        message="Failed to read feed configuration YAML file.",
    )

    FEED_CONFIGURATION_INVALID_YML = ErrorDefinition(
        code="HF-VALIDATION-006",
        message="Feed configuration YAML file is invalid.",
    )

    FEED_META_MISSING = ErrorDefinition(
        code="HF-VALIDATION-023",
        message="feed_meta section is missing.",
    )

    FEED_META_INVALID = ErrorDefinition(
        code="HF-VALIDATION-024",
        message="feed_meta section is invalid.",
    )

    FEED_META_UNIQUE_IDENTIFIER_MISSING = ErrorDefinition(
        code="HF-VALIDATION-025",
        message="feed_meta.unique_identifier is mandatory.",
    )

    FEED_META_VACUUM_HOURS_MISSING = ErrorDefinition(
        code="HF-VALIDATION-026",
        message="feed_meta.vacuum_hours is mandatory.",
    )

    FEED_META_VACUUM_HOURS_INVALID = ErrorDefinition(
        code="HF-VALIDATION-027",
        message="feed_meta.vacuum_hours must be an integer.",
    )

    FEED_META_VACUUM_HOURS_OUT_OF_RANGE = ErrorDefinition(
        code="HF-VALIDATION-028",
        message="feed_meta.vacuum_hours is outside the allowed range.",
    )

    # ---------------------------------------------------------
    # Load details
    # ---------------------------------------------------------

    FEED_META_LOAD_DETAILS_MISSING = ErrorDefinition(
        code="HF-VALIDATION-029",
        message="load_details section is missing.",
    )

    FEED_META_LOAD_DETAILS_INVALID = ErrorDefinition(
        code="HF-VALIDATION-030",
        message="load_details section is invalid.",
    )

    FEED_META_LOAD_DETAILS_TYPE_MISSING = ErrorDefinition(
        code="HF-VALIDATION-031",
        message="load_details.type is mandatory.",
    )

    FEED_META_LOAD_DETAILS_TYPE_INVALID = ErrorDefinition(
        code="HF-VALIDATION-032",
        message=(
            "load_details.type must be one of FULL_LOAD, "
            "INCREMENTAL_CDC, APPEND_LOAD, or SCD_TYPE_2."
        ),
    )

    # ---------------------------------------------------------
    # Source and target
    # ---------------------------------------------------------

    SOURCE_MISSING = ErrorDefinition(
        code="HF-VALIDATION-033",
        message="source section is missing.",
    )

    SOURCE_INVALID = ErrorDefinition(
        code="HF-VALIDATION-034",
        message="source section is invalid.",
    )

    SOURCE_FIELD_MISSING = ErrorDefinition(
        code="HF-VALIDATION-035",
        message="A mandatory source field is missing or blank.",
    )

    TARGET_MISSING = ErrorDefinition(
        code="HF-VALIDATION-036",
        message="target section is missing.",
    )

    TARGET_INVALID = ErrorDefinition(
        code="HF-VALIDATION-037",
        message="target section is invalid.",
    )

    TARGET_FIELD_MISSING = ErrorDefinition(
        code="HF-VALIDATION-038",
        message="A mandatory target field is missing or blank.",
    )

    # ---------------------------------------------------------
    # Feed specifications
    # ---------------------------------------------------------

    FEED_SPECS_MISSING = ErrorDefinition(
        code="HF-VALIDATION-039",
        message="feed_specs section is missing.",
    )

    FEED_SPECS_INVALID = ErrorDefinition(
        code="HF-VALIDATION-040",
        message="feed_specs section is invalid.",
    )

    FEED_SPECS_PRIMARY_KEY_MISSING = ErrorDefinition(
        code="HF-VALIDATION-041",
        message="feed_specs.primary_key is mandatory.",
    )

    FEED_SPECS_COLUMN_LIST_INVALID = ErrorDefinition(
        code="HF-VALIDATION-042",
        message="Feed specification column list must be a non-empty list of non-blank strings.",
    )

    FEED_SPECS_OPTIMIZE_COMMAND_INVALID = ErrorDefinition(
        code="HF-VALIDATION-043",
        message="feed_specs.optimize_command must be a mapping.",
    )

    FEED_SPECS_OPTIMIZE_ENABLED_INVALID = ErrorDefinition(
        code="HF-VALIDATION-044",
        message="feed_specs.optimize_command.enabled must be a boolean.",
    )

    FEED_SPECS_OPTIMIZE_WHERE_INVALID = ErrorDefinition(
        code="HF-VALIDATION-045",
        message="feed_specs.optimize_command.where must be a non-empty mapping of column names to values.",
    )

    FEED_SPECS_ZORDER_BY_INVALID = ErrorDefinition(
        code="HF-VALIDATION-046",
        message="feed_specs.optimize_command.zorder_by must be a non-empty list of column names.",
    )

    FEED_SPECS_CUSTOM_SELECTION_INVALID = ErrorDefinition(
        code="HF-VALIDATION-047",
        message="feed_specs.custom_selection must be a mapping.",
    )

    FEED_SPECS_CUSTOM_SELECTION_ENABLED_INVALID = ErrorDefinition(
        code="HF-VALIDATION-048",
        message="feed_specs.custom_selection.enabled must be a boolean.",
    )

    FEED_SPECS_CUSTOM_SELECTION_SQL_FILE_MISSING = ErrorDefinition(
        code="HF-VALIDATION-049",
        message="feed_specs.custom_selection.sql_file is mandatory when custom selection is enabled.",
    )

    FEED_SPECS_ENFORCE_SCHEMA_INVALID = ErrorDefinition(
        code="HF-VALIDATION-050",
        message="feed_specs.enforce_schema must be a mapping.",
    )

    FEED_SPECS_ENFORCE_SCHEMA_TYPE_INVALID = ErrorDefinition(
        code="HF-VALIDATION-051",
        message="feed_specs.enforce_schema.type must be 'struct'.",
    )

    FEED_SPECS_ENFORCE_SCHEMA_FIELDS_INVALID = ErrorDefinition(
        code="HF-VALIDATION-052",
        message="feed_specs.enforce_schema.fields must be a non-empty list.",
    )

    FEED_SPECS_SCHEMA_FIELD_INVALID = ErrorDefinition(
        code="HF-VALIDATION-053",
        message="Each enforce_schema field must be a mapping.",
    )

    FEED_SPECS_SCHEMA_FIELD_NAME_MISSING = ErrorDefinition(
        code="HF-VALIDATION-054",
        message="Each enforce_schema field must have a non-blank name.",
    )

    FEED_SPECS_SCHEMA_FIELD_TYPE_INVALID = ErrorDefinition(
        code="HF-VALIDATION-055",
        message="Each enforce_schema field must have a valid Spark data type.",
    )

    FEED_SPECS_SCHEMA_FIELD_NULLABLE_INVALID = ErrorDefinition(
        code="HF-VALIDATION-056",
        message="Each enforce_schema field nullable value must be true or false.",
    )

    FEED_SPECS_SCHEMA_FIELD_METADATA_INVALID = ErrorDefinition(
        code="HF-VALIDATION-057",
        message="Each enforce_schema field metadata must be a mapping.",
    )
