"""Validation-related exception types for HanduFLOW."""

from __future__ import annotations

from handuflow.platform.exceptions.base import HanduflowError


class ValidationError(HanduflowError):
    """
    Base exception for all validation operations.
    """
