"""System configurator for HanduFLOW.

Reads framework configuration, configures storage and logging, and exposes
the initialized runtime services for a HanduFLOW application directory.
"""

from __future__ import annotations

import configparser
import logging
import sys
import uuid
from datetime import datetime

from ..logging import StorageFileHandler, StorageRotatingFileHandler
from ..storage import StorageManager, StoragePath, StorageProvider
from ..exceptions import ConfigurationError, ConfigurationErrors, HanduflowError
from .dataclasses import ConfigurationContext, DefaultConfiguration, LoggingConfiguration, SparkConfiguration

from pyspark.sql import SparkSession


CONFIG_FILE_NAME = "config.ini"
DEFAULT_SECTION = "DEFAULT"
LOGGING_SECTION = "LOGGING"
ROTATING_LOG_TYPE = "rotating"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class SystemConfigurator:
    """Initialize storage, logging, and configuration for a HanduFLOW directory."""

    def __init__(self, handu_flow_directory_path: str, spark: SparkSession) -> None:
        if not handu_flow_directory_path:
            raise ConfigurationError(
                ConfigurationErrors.MISSING_HANDUFLOW_DIRECTORY,
                parameter="handu_flow_directory_path",
            )

        self._storage_manager = StorageManager()
        self._base_directory = StoragePath(handu_flow_directory_path)
        self._config = configparser.ConfigParser(interpolation=None)
        self._run_id = str(uuid.uuid4())
        self._context: ConfigurationContext | None = None
        self._spark: SparkSession = spark
        self._list_of_feed_ymls: list[StoragePath] = []

    @property
    def run_id(self) -> str:
        """Return the unique identifier generated for this configuration run."""
        return self._run_id

    def set_storage_provider(self, storage_provider: StorageProvider) -> None:
        """Override the storage provider used to read configuration and write logs."""
        self._storage_manager.set_provider(storage_provider)

    def configure(self) -> ConfigurationContext | None:
        """Read configuration, initialize services, and return the runtime context.

        The context is cached and can be retrieved again via
        `get_configuration_context`.
        """
        try:
            self._read_configuration()
        except HanduflowError:
            raise
        except (OSError, UnicodeError, configparser.Error) as exc:
            raise ConfigurationError(
                ConfigurationErrors.READ_CONFIGURATION_ERROR,
                path=self._config_path.uri,
                cause=exc,
            ) from exc

        try:
            self._context = self._build_context()
        except HanduflowError:
            raise
        except (KeyError, TypeError, ValueError, OSError, configparser.Error) as exc:
            raise ConfigurationError(
                ConfigurationErrors.LOGGER_ERROR,
                cause=exc,
            ) from exc

        return self._context

    def get_configuration_context(self) -> ConfigurationContext:
        """Return the runtime context produced by `configure`."""
        if self._context is None:
            raise ConfigurationError(
                ConfigurationErrors.UNKNOWN_CONFIGURATION_ERROR,
                reason="configure() must be called before the configuration context is available",
            )
        return self._context

    @property
    def _config_path(self) -> StoragePath:
        return StoragePath(f"{self._base_directory.uri}/{CONFIG_FILE_NAME}")

    def _read_list_of_feed_ymls(self) -> list[StoragePath]:
        feed_config_path = StoragePath(f"{self._base_directory.uri}/feed_configuration")
        self._list_of_feed_ymls = (
            self._storage_manager.provider.read_all_files_by_extension_recursively(
                feed_config_path,
                ".yml",
            )
        )
        return self._list_of_feed_ymls

    def _read_configuration(self) -> None:
        raw_config = self._storage_manager.provider.read(self._config_path)
        self._config.read_string(raw_config.decode())

    def _build_context(self) -> ConfigurationContext:
        default = DefaultConfiguration(
            system_name=self._config[DEFAULT_SECTION]["system_name"],
        )
        return ConfigurationContext(
            run_id=self._run_id,
            default=default,
            logging=self._build_logging_configuration(default.system_name),
            storage_path=self._base_directory,
            storage_manager=self._storage_manager,
            spark_config=self._build_spark_configuration(),
            list_of_feed_ymls=self._read_list_of_feed_ymls()
        )


    def _build_spark_configuration(self):
        return SparkConfiguration(
            spark=self._spark
        )

    def _build_logging_configuration(self, system_name: str) -> LoggingConfiguration:
        section = self._config[LOGGING_SECTION]
        log_type = section["type"]
        log_format = section.get("log_format") or DEFAULT_LOG_FORMAT
        log_directory_name = section["log_directory_name"]
        log_file_name = section["log_file_name"]
        max_bytes = section.getint("max_bytes", fallback=0)
        backup_count = section.getint("backup_count", fallback=0)
        default_log_level = int(section["default_log_level"])
        log_retention_days = section.getint("log_retention_days", fallback=0)


        log_directory = StoragePath(f"{self._base_directory.uri}/{log_directory_name}")
        file_handler = self._create_file_handler(
            log_type=log_type,
            log_directory=log_directory,
            log_file_name=log_file_name,
            max_bytes=max_bytes,
            backup_count=backup_count,
            log_retention_days=log_retention_days,
        )
        logger = self._create_logger(
            name=system_name,
            level=default_log_level,
            log_format=log_format,
            file_handler=file_handler,
        )

        return LoggingConfiguration(
            type=log_type,
            log_format=log_format,
            log_directory_name=log_directory_name,
            log_file_name=log_file_name,
            backup_count=backup_count,
            max_bytes=max_bytes,
            default_log_level=default_log_level,
            log_retention_days=log_retention_days,
            logger=logger,
        )

    def _create_file_handler(
        self,
        *,
        log_type: str,
        log_directory: StoragePath,
        log_file_name: str,
        max_bytes: int,
        backup_count: int,
        log_retention_days: int,
    ) -> logging.Handler:
        storage = self._storage_manager.provider

        if log_type == ROTATING_LOG_TYPE:
            log_path = StoragePath(f"{log_directory.uri}/{log_file_name}.log")
            return StorageRotatingFileHandler(log_path, storage, max_bytes, backup_count)

        return StorageFileHandler(
            log_directory,
            log_file_name,
            self._run_id,
            storage,
            log_retention_days=log_retention_days,
            run_date=datetime.now(),
        )

    @staticmethod
    def _create_logger(
        *,
        name: str,
        level: int,
        log_format: str,
        file_handler: logging.Handler,
    ) -> logging.Logger:
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.handlers.clear()
        logger.propagate = False
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger
