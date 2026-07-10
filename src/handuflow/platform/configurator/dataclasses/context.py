from dataclasses import dataclass

from handuflow.platform.storage import StorageManager, StoragePath
from .logging import LoggingConfiguration
from .default import DefaultConfiguration


@dataclass(frozen=True, slots=True)
class ConfigurationContext:
    """Runtime context shared across the framework."""

    run_id: str
    default: DefaultConfiguration
    logging: LoggingConfiguration
    storage_path: StoragePath
    storage_manager: StorageManager