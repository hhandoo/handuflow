"""Data quality error definitions for HanduFLOW."""

from __future__ import annotations

from handuflow.platform.exceptions.definition import ErrorDefinition


class DataQualityErrors:
    """Error catalog for the HanduFLOW data quality framework."""


    YML_FILE_NOT_FOUND = ErrorDefinition(
        code="HF-DATA-QUALITY-001",
        message="YML file specified was not found. Please check the file path and ensure that the file exists.",
    )

    INVALID_YAML = ErrorDefinition(
        code="HF-DATA-QUALITY-002",
        message="Failed to parse the data quality YAML configuration.",
    )

    INVALID_CONFIGURATION = ErrorDefinition(
        code="HF-DATA-QUALITY-003",
        message="The data quality configuration is invalid.",
    )

    INVALID_FEED_SOURCE_CONFIGURATION = ErrorDefinition(
        code="HF-DATA-QUALITY-004",
        message="The feed source configuration specified in YML is invalid, please check the YML file and ensure that the source configuration is correct.",
    )

    INVALID_FEED_METADATA = ErrorDefinition(
        code="HF-DATA-QUALITY-005",
        message="The feed metadata is invalid.",
    )

    INVALID_CHECK_CONFIGURATION = ErrorDefinition(
        code="HF-DATA-QUALITY-006",
        message="The data quality check configuration is invalid.",
    )

    UNKNOWN_CHECK_TYPE = ErrorDefinition(
        code="HF-DATA-QUALITY-007",
        message="Unsupported data quality check type.",
    )

    CHECK_CONFIGURATION_PARSE_ERROR = ErrorDefinition(
        code="HF-DATA-QUALITY-008",
        message="Failed to parse the data quality check configuration.",
    )



    DEPENDENCY_DATASET_NOT_FOUND = ErrorDefinition(
        code="HF-DATA-QUALITY-009",
        message="The required dependency dataset was not found.",
    )

    TABLE_NOT_FOUND = ErrorDefinition(
        code="HF-DATA-QUALITY-010",
        message="The requested table was not found.",
    )

    COLUMN_NOT_FOUND = ErrorDefinition(
        code="HF-DATA-QUALITY-011",
        message="The requested column was not found.",
    )


    SQL_QUERY_ERROR = ErrorDefinition(
        code="HF-DATA-QUALITY-012",
        message="Failed to execute the SQL query for the data quality check.",
    )

    CHECK_EXECUTION_FAILED = ErrorDefinition(
        code="HF-DATA-QUALITY-013",
        message="The data quality check execution failed.",
    )

    INVALID_DEPENDENCY_DATASET = ErrorDefinition(
        code="HF-DATA-QUALITY-014",
        message="Dependency dataset configuration is invalid or missing required fields.",
    )

    UNKNOWN = ErrorDefinition(
        code="HF-DATA-QUALITY-999",
        message="An unexpected error occurred while executing data quality checks.",
    )