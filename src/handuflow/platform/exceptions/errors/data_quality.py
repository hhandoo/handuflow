"""Data quality error code catalog for HanduFLOW."""

from __future__ import annotations

from handuflow.platform.exceptions.definition import ErrorDefinition


class DataQualityErrors:
    """
    Data quality error catalog.
    """

    TABLE_NOT_FOUND = ErrorDefinition(
        code="HF-DATA-QUALITY-001",
        message="Table not found.",
    )

    COLUMN_NOT_FOUND = ErrorDefinition(
        code="HF-DATA-QUALITY-002",
        message="Column not found.",
    )

    SQL_QUERY_ERROR = ErrorDefinition(
        code="HF-DATA-QUALITY-003",
        message="Something went wrong while building a dataframe with the provided query.",
    )

    DATA_QUALITY_UNKNOWN = ErrorDefinition(
        code="HF-DATA-QUALITY-004",
        message="Something went wrong while performing data quality check.",
    )
