"""HanduFLOW directory structure validation."""

from __future__ import annotations

import configparser
import logging

from ...configurator.dataclasses.context import ConfigurationContext
from ...exceptions.domains.validation import ValidationError
from ...exceptions.errors.validation import ValidationErrors
from ...storage import StoragePath
from ...storage.base import StorageProvider
from ..base import Validation
from ..dataclasses import ValidationResult

FEED_CONFIGURATION_DIR = "feed_configuration"
CONFIGURATION_FILE = "config.ini"
YML_SUFFIX = ".yml"


class EnforceHFDirStructure(Validation):
    """Validate the HanduFLOW directory structure."""

    @property
    def name(self) -> str:
        return "enforce_HFdir_structure"

    @property
    def key(self) -> int:
        return 2

    def validate(
        self,
        configuration_context: ConfigurationContext,
    ) -> ValidationResult:
        """Validate the HanduFLOW directory structure."""

        logger = configuration_context.logging.logger
        provider = configuration_context.storage_manager.provider
        root = configuration_context.storage_path
        logger.info(
            "Starting directory structure validation for %s",
            root.uri,
        )
        ignored_directories = {
            configuration_context.logging.log_directory_name,
        }
        ignored_files = {
            configuration_context.logging.log_file_name,
        }
        try:
            self.__validate_root_configuration(
                provider,
                root,
                logger,
            )

            self.__validate_feed_configuration(
                provider,
                root,
                ignored_directories,
                ignored_files,
                logger,
            )

            self.__validate_naming(
                provider,
                root,
                ignored_directories,
                ignored_files,
                logger,
            )
        except ValidationError as exc:
            logger.warning(
                "Directory structure validation failed: %s",
                exc,
            )
            return ValidationResult(
                self.key,
                self.name,
                False,
                str(exc),
            )
        except Exception as exc:
            logger.exception(
                "Unexpected error during directory structure validation.",
            )
            error = ValidationError(
                ValidationErrors.VALIDATION_UNKNOWN,
            )
            logger.error(
                "Unexpected validation error: %s",
                exc,
            )
            return ValidationResult(
                self.key,
                self.name,
                False,
                str(error),
            )
        message = "HanduFLOW directory structure is valid."
        logger.info(message)
        return ValidationResult(
            self.key,
            self.name,
            True,
            message,
        )

    def __validate_root_configuration(
        self,
        provider: StorageProvider,
        root: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate the required root config.ini file."""
        config_path = StoragePath(
            f"{root.uri}/{CONFIGURATION_FILE}",
        )
        logger.info(
            "Checking required configuration file: %s",
            config_path.uri,
        )
        if not provider.exists(config_path):
            logger.warning(
                "Required configuration file is missing: %s",
                config_path.uri,
            )

            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_FILE_MISSING,
            )
        if provider.is_directory(config_path):
            logger.warning(
                "Configuration path is a directory: %s",
                config_path.uri,
            )

            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_FILE_NOT_FILE,
            )
        try:
            content = self._read_text(
                provider,
                config_path,
            )
        except UnicodeDecodeError as exc:
            logger.warning(
                "Configuration file is not valid UTF-8: %s",
                config_path.uri,
            )
            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_FILE_INVALID_ENCODING,
            )
            raise AssertionError from exc

        except OSError as exc:
            logger.exception(
                "Failed to read configuration file: %s",
                config_path.uri,
            )

            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_FILE_READ_FAILED,
            )

            raise AssertionError from exc
        try:
            parser = configparser.ConfigParser()
            parser.read_string(content)
        except configparser.Error as exc:
            logger.warning(
                "Configuration file contains invalid INI syntax: %s",
                config_path.uri,
            )
            self._raise_validation_error(
                ValidationErrors.CONFIGURATION_FILE_INVALID_INI,
            )
            raise AssertionError from exc
        logger.info(
            "Configuration file is valid: %s",
            config_path.uri,
        )

    def __validate_feed_configuration(
        self,
        provider: StorageProvider,
        root: StoragePath,
        ignored_directories: set[str],
        ignored_files: set[str],
        logger: logging.Logger,
    ) -> None:
        """Validate the feed_configuration directory."""

        feed_config_path = StoragePath(
            f"{root.uri}/{FEED_CONFIGURATION_DIR}",
        )
        logger.info(
            "Checking required directory: %s",
            feed_config_path.uri,
        )
        if not provider.exists(feed_config_path):
            logger.warning(
                "Feed configuration directory is missing: %s",
                feed_config_path.uri,
            )
            self._raise_validation_error(
                ValidationErrors.FEED_CONFIGURATION_DIR_MISSING,
            )
        if not provider.is_directory(feed_config_path):
            logger.warning(
                "Feed configuration path is not a directory: %s",
                feed_config_path.uri,
            )
            self._raise_validation_error(
                ValidationErrors.FEED_CONFIGURATION_DIR_NOT_DIRECTORY,
            )
        directories = self._recursive_directory_lookup(
            provider,
            feed_config_path,
            ignored_directories,
            logger,
        )
        all_directories = [
            feed_config_path,
            *directories,
        ]
        all_files = self._recursive_file_lookup(
            provider,
            feed_config_path,
            ignored_directories,
            ignored_files,
            logger,
        )
        yml_files = [file for file in all_files if self._has_suffix(file, YML_SUFFIX)]
        if not yml_files:
            logger.warning(
                "No YAML files found under %s",
                feed_config_path.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_CONFIGURATION_YML_MISSING,
            )
        for directory in all_directories:

            children = list(
                provider.list(directory),
            )

            child_directories = [
                child
                for child in children
                if provider.is_directory(child)
                and self._path_name(child) not in ignored_directories
            ]
            if child_directories:
                continue
            child_yml_files = [
                child
                for child in children
                if not provider.is_directory(child)
                and self._path_name(child) not in ignored_files
                and self._has_suffix(child, YML_SUFFIX)
            ]
            if child_yml_files:
                continue
            logger.warning(
                "Deepest directory does not contain a YAML file: %s",
                directory.uri,
            )
            self._raise_validation_error(
                ValidationErrors.FEED_CONFIGURATION_LEAF_YML_MISSING,
            )
        logger.info(
            "Checked %d directories under %s",
            len(all_directories),
            FEED_CONFIGURATION_DIR,
        )
        logger.info(
            "Found %d YAML files under %s",
            len(yml_files),
            FEED_CONFIGURATION_DIR,
        )

    def __validate_naming(
        self,
        provider: StorageProvider,
        root: StoragePath,
        ignored_directories: set[str],
        ignored_files: set[str],
        logger: logging.Logger,
    ) -> None:
        """Validate directory and file names."""
        directories = self._recursive_directory_lookup(
            provider,
            root,
            ignored_directories,
            logger,
        )
        for directory in directories:
            if self._is_snake_case_directory(directory):
                continue
            logger.warning(
                "Directory name is not lower snake_case: %s",
                directory.uri,
            )
            self._raise_validation_error(
                ValidationErrors.DIRECTORY_NAME_INVALID,
            )
        files = self._recursive_file_lookup(
            provider,
            root,
            ignored_directories,
            ignored_files,
            logger,
        )
        for file in files:
            if self._is_snake_case_file(file):
                continue
            logger.warning(
                "File name is not lower snake_case: %s",
                file.uri,
            )
            self._raise_validation_error(
                ValidationErrors.FILE_NAME_INVALID,
            )
        logger.info(
            "Checked %d directories and %d files for naming",
            len(directories),
            len(files),
        )
