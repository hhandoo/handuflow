"""Storage-related exception types for HanduFLOW."""

from __future__ import annotations

from handuflow.platform.exceptions.base import HanduflowError


class StorageError(HanduflowError):
    """
    Base exception for all storage operations.
    """