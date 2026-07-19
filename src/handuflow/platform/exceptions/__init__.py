"""Exception framework for HanduFLOW platform services."""

from __future__ import annotations

from .base import HanduflowError
from .domains.configuration import ConfigurationError
from .domains.data_quality import DataQualityError
from .domains.storage import StorageError
from .errors.configuration import ConfigurationErrors
from .errors.data_quality import DataQualityErrors
from .errors.storage import StorageErrors

__all__ = [
    "HanduflowError",
    "ConfigurationError",
    "ConfigurationErrors",
    "DataQualityError",
    "DataQualityErrors",
    "StorageError",
    "StorageErrors",
]
