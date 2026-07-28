"""Data quality-related exception types for HanduFLOW."""

from __future__ import annotations

from handuflow.platform.exceptions.base import HanduflowError


class DataQualityError(HanduflowError):
    """
    Base exception for all data quality operations.
    """
