"""Built-in HanduFLOW validation rules."""

from __future__ import annotations

from ..base import Validation

# from .directory_structure_validation import DirectoryStructureValidation
# from .feed_configuration_validation import FeedConfigurationValidation
from .enforce_HFdir_structure import EnforceHFDirStructure
from .HF_config_validation import HFConfigValidation

VALIDATIONS: list[Validation] = [EnforceHFDirStructure(), HFConfigValidation()]

__all__ = [
    "VALIDATIONS",
]
