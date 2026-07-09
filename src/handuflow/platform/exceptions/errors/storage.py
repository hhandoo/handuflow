"""Storage error code catalog for HanduFLOW."""

from __future__ import annotations

from handuflow.platform.exceptions.definition import ErrorDefinition


class StorageErrors:
    """
    Storage error catalog.
    """

    NOT_FOUND = ErrorDefinition(
        code="HF-STORAGE-001",
        message="Storage object does not exist.",
    )

    ALREADY_EXISTS = ErrorDefinition(
        code="HF-STORAGE-002",
        message="Storage object already exists.",
    )

    PERMISSION_DENIED = ErrorDefinition(
        code="HF-STORAGE-003",
        message="Permission denied.",
    )

    READ_FAILED = ErrorDefinition(
        code="HF-STORAGE-004",
        message="Failed to read storage object.",
    )

    WRITE_FAILED = ErrorDefinition(
        code="HF-STORAGE-005",
        message="Failed to write storage object.",
    )

    DELETE_FAILED = ErrorDefinition(
        code="HF-STORAGE-006",
        message="Failed to delete storage object.",
    )

    COPY_FAILED = ErrorDefinition(
        code="HF-STORAGE-007",
        message="Failed to copy storage object.",
    )

    MOVE_FAILED = ErrorDefinition(
        code="HF-STORAGE-008",
        message="Failed to move storage object.",
    )

    INVALID_PATH = ErrorDefinition(
        code="HF-STORAGE-009",
        message="Invalid storage path.",
    )

    PROVIDER_ERROR = ErrorDefinition(
        code="HF-STORAGE-010",
        message="Storage provider error.",
    )