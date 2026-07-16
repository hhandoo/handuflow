"""Built-in HanduFLOW validation rules."""

from __future__ import annotations

from ..base import Validation
from .directory_structure_validation import DirectoryStructureValidation
from .feed_configuration_validation import FeedConfigurationValidation

VALIDATIONS: list[Validation] = [
    DirectoryStructureValidation(),
    FeedConfigurationValidation(),
]

__all__ = [
    "VALIDATIONS",
]
