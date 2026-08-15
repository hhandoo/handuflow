"""Built-in HanduFLOW validation rules."""

from __future__ import annotations

from ..base import Validation

# from .directory_structure_validation import DirectoryStructureValidation
# from .feed_configuration_validation import FeedConfigurationValidation
from .enforce_HFdir_structure import EnforceHFDirStructure
from .enforce_master_config import EnforceMasterConfig
from .enforce_feed_meta import EnforceFeedMeta
from .enforce_load_details import EnforceLoadDetails
from .enforce_source_and_target import EnforceSourceAndTarget
from .enforce_feed_specs import EnforceFeedSpecs
from .enforce_data_quality_checks import EnforceDataQualityChecks

VALIDATIONS: list[Validation] = [
    EnforceHFDirStructure(),
    EnforceMasterConfig(),
    EnforceFeedMeta(),
    EnforceLoadDetails(),
    EnforceSourceAndTarget(),
    EnforceFeedSpecs(),
    EnforceDataQualityChecks(),
]

__all__ = [
    "VALIDATIONS",
]
