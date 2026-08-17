from dataclasses import dataclass

from ...storage import StorageManager, StoragePath
from .logging import LoggingConfiguration
from .default import DefaultConfiguration
from .spark import SparkConfiguration


@dataclass(frozen=True, slots=True)
class ConfigurationContext:
    """Runtime context shared across the framework."""

    run_id: str
    default: DefaultConfiguration
    logging: LoggingConfiguration
    storage_path: StoragePath
    storage_manager: StorageManager
    spark_config: SparkConfiguration
    list_of_feed_ymls: list[StoragePath]
