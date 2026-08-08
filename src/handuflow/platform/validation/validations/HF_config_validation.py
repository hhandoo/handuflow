"""HanduFLOW configuration file content validation."""

from __future__ import annotations

import configparser
import logging
import re

from ...configurator.dataclasses.context import ConfigurationContext
from ...exceptions.domains.validation import ValidationError
from ...exceptions.errors.validation import ValidationErrors
from ...storage import StoragePath
from ...storage.base import StorageProvider
from ..base import Validation
from ..dataclasses import ValidationResult
from ...exceptions.definition import ErrorDefinition

CONFIGURATION_FILE = "config.ini"

DEFAULT_SECTION = "DEFAULT"
LOGGING_SECTION = "LOGGING"

LOGGING_TYPE_OPTIONS = {
    "standard",
    "rotating",
}

SYSTEM_NAME_PATTERN = re.compile(
    r"^[A-Za-z0-9]+$",
)


class HFConfigValidation(Validation):
    """Validate the contents of the HanduFLOW config.ini file."""

    @property
    def name(self) -> str:
        return "hf_config_validation"

    @property
    def key(self) -> int:
        return 3

    def validate(
        self,
        configuration_context: ConfigurationContext,
    ) -> ValidationResult:
        """Validate the HanduFLOW configuration."""
        logger = configuration_context.logging.logger
        provider = configuration_context.storage_manager.provider
        root = configuration_context.storage_path
        config_path = StoragePath(
            f"{root.uri}/{CONFIGURATION_FILE}",
        )
        logger.info(
            "Starting config.ini validation for %s",
            config_path.uri,
        )
        try:
            parser = self.__load_configuration(
                provider,
                config_path,
                logger,
            )
            self.__validate_default_section(
                parser,
                logger,
            )
            self.__validate_logging_section(
                parser,
                logger,
            )
        except ValidationError as exc:
            logger.warning(
                "Configuration validation failed: %s",
                exc,
            )
            return ValidationResult(
                self.key,
                self.name,
                False,
                str(exc),
            )
        except Exception:
            logger.exception(
                "Unexpected error during config.ini validation.",
            )
            error = ValidationError(
                ValidationErrors.VALIDATION_UNKNOWN,
            )
            return ValidationResult(
                self.key,
                self.name,
                False,
                str(error),
            )
        message = "HanduFLOW configuration is valid."
        logger.info(message)
        return ValidationResult(
            self.key,
            self.name,
            True,
            message,
        )

    def __load_configuration(
        self,
        provider: StorageProvider,
        config_path: StoragePath,
        logger: logging.Logger,
    ) -> configparser.ConfigParser:
        """Read and parse config.ini."""
        if not provider.exists(config_path):
            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_FILE_MISSING,
            )
        if provider.is_directory(config_path):
            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_FILE_NOT_FILE,
            )
        try:
            content: str = self._read_text(
                provider,
                config_path,
            )
        except UnicodeDecodeError:
            logger.warning(
                "Configuration file is not valid UTF-8: %s",
                config_path.uri,
            )
            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_FILE_INVALID_ENCODING,
            )
        except OSError:
            logger.exception(
                "Failed to read configuration file: %s",
                config_path.uri,
            )
            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_FILE_READ_FAILED,
            )
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read_string(content)
        except configparser.Error:
            logger.warning(
                "Configuration file contains invalid INI syntax: %s",
                config_path.uri,
            )
            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_FILE_INVALID_INI,
            )
        return parser

    def __validate_default_section(
        self,
        parser: configparser.ConfigParser,
        logger: logging.Logger,
    ) -> None:
        """Validate the DEFAULT section."""
        system_name = self.__get_required_value(
            parser["DEFAULT"],
            "system_name",
            ValidationErrors.CONFIGURATION_SYSTEM_NAME_MISSING,
            logger,
        )
        if not SYSTEM_NAME_PATTERN.fullmatch(system_name):
            logger.warning(
                "system_name must contain only alphanumeric " "characters: %s",
                system_name,
            )
            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_SYSTEM_NAME_INVALID,
            )
        self.__get_required_value(
            parser["DEFAULT"],
            "environment",
            ValidationErrors.CONFIGURATION_ENVIRONMENT_MISSING,
            logger,
        )
        logger.info(
            "DEFAULT configuration is valid.",
        )

    def __validate_logging_section(
        self,
        parser: configparser.ConfigParser,
        logger: logging.Logger,
    ) -> None:
        """Validate the LOGGING section."""
        if not parser.has_section(LOGGING_SECTION):
            logger.warning(
                "LOGGING section is missing.",
            )

            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_LOGGING_TYPE_MISSING,
            )
        logging_config = parser[LOGGING_SECTION]
        logging_type = self.__get_required_value(
            logging_config,
            "type",
            ValidationErrors.CONFIGURATION_LOGGING_TYPE_MISSING,
            logger,
        )
        logging_type = logging_type.lower()
        if logging_type not in LOGGING_TYPE_OPTIONS:
            logger.warning(
                "Invalid logging type: %s",
                logging_type,
            )

            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_LOGGING_TYPE_INVALID,
            )
        log_format = self.__get_optional_value(
            logging_config,
            "log_format",
        )

        if log_format is not None:
            logger.info(
                "Custom log format configured.",
            )
        self.__get_required_value(
            logging_config,
            "log_directory_name",
            ValidationErrors.CONFIGURATION_LOG_DIRECTORY_MISSING,
            logger,
        )
        self.__get_required_value(
            logging_config,
            "log_file_name",
            ValidationErrors.CONFIGURATION_LOG_FILE_MISSING,
            logger,
        )
        backup_count = self.__get_optional_value(
            logging_config,
            "backup_count",
        )

        if backup_count is not None:
            self.__validate_integer(
                backup_count,
                "backup_count",
                logger,
            )
        max_bytes = self.__get_optional_value(
            logging_config,
            "max_bytes",
        )
        if max_bytes is not None:
            self.__validate_integer(
                max_bytes,
                "max_bytes",
                logger,
            )
        default_log_level = self.__get_required_value(
            logging_config,
            "default_log_level",
            ValidationErrors.CONFIGURATION_DEFAULT_LOG_LEVEL_MISSING,
            logger,
        )
        self.__validate_integer(
            default_log_level,
            "default_log_level",
            logger,
        )
        log_retention_days = self.__get_optional_value(
            logging_config,
            "log_retention_days",
        )
        if log_retention_days is not None:
            self.__validate_integer(
                log_retention_days,
                "log_retention_days",
                logger,
            )
        logger.info(
            "LOGGING configuration is valid.",
        )

    @staticmethod
    def __get_optional_value(
        section: configparser.SectionProxy,
        key: str,
    ) -> str | None:
        """Return an optional configuration value."""
        value = section.get(
            key,
            fallback=None,
        )
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        return value

    def __get_required_value(
        self,
        section: configparser.SectionProxy,
        key: str,
        error: ErrorDefinition,
        logger: logging.Logger,
    ) -> str:
        """Return a required configuration value."""
        value = self.__get_optional_value(
            section,
            key,
        )
        if value is not None:
            return value
        logger.warning(
            "Required configuration value is missing: %s",
            key,
        )
        self._raise_validation_error(error)

    def __validate_integer(
        self,
        value: str,
        field_name: str,
        logger: logging.Logger,
    ) -> None:
        """Validate an integer configuration value."""
        try:
            int(value)
        except ValueError:
            logger.warning(
                "Configuration value must be an integer: %s=%s",
                field_name,
                value,
            )
            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_VALUE_INVALID,
            )
