"""Configuration-related exception types for HanduFLOW."""

from __future__ import annotations

from handuflow.platform.exceptions.base import HanduflowError


class ConfigurationError(HanduflowError):
    """
    Base exception for all configuration operations.
    """