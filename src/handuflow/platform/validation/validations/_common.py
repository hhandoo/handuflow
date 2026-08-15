"""Shared utilities for built-in HanduFLOW validation rules."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, cast

import yaml

from ...configurator.dataclasses.context import ConfigurationContext
from ...exceptions.definition import ErrorDefinition
from ...exceptions.domains.validation import ValidationError
from ...exceptions.errors.validation import ValidationErrors
from ...storage import StoragePath
from ...storage.base import StorageProvider
from ..base import Validation
from ..dataclasses import ValidationResult

FEED_CONFIGURATION_DIR = "feed_configuration"
YML_SUFFIX = ".yml"
CONFIGURATION_FILE = "config.ini"


def ignored_paths(
    configuration_context: ConfigurationContext,
) -> tuple[set[str], set[str]]:
    """Return directory and file names excluded from feed-configuration scans."""

    return (
        {configuration_context.logging.log_directory_name},
        {configuration_context.logging.log_file_name},
    )


def feed_configuration_path(
    root: StoragePath,
) -> StoragePath:
    """Return the feed_configuration directory under the project root."""

    return StoragePath(f"{root.uri}/{FEED_CONFIGURATION_DIR}")


def require_mapping(
    value: object,
    error: ErrorDefinition,
    *,
    require_string_keys: bool = False,
) -> dict[str, Any]:
    """Validate and return a YAML mapping with optional string-key enforcement."""

    if not isinstance(value, dict):
        raise ValidationError(error)

    if not require_string_keys:
        return cast(dict[str, Any], value)

    mapping = cast(dict[object, object], value)
    result: dict[str, Any] = {}

    for key, item in mapping.items():
        if not isinstance(key, str):
            raise ValidationError(error)

        result[key] = item

    return result


class FeedConfigurationValidation(Validation):
    """Base class for validators that scan feed-configuration YAML files."""

    def _discover_yml_files(
        self,
        provider: StorageProvider,
        root: StoragePath,
        ignored_directories: set[str],
        ignored_files: set[str],
        logger: logging.Logger,
    ) -> list[StoragePath]:
        """Recursively collect YAML files under feed_configuration."""

        files = self._recursive_file_lookup(
            provider,
            feed_configuration_path(root),
            ignored_directories,
            ignored_files,
            logger,
        )

        return [
            file_path
            for file_path in files
            if self._has_suffix(file_path, YML_SUFFIX)
        ]

    def _load_yaml_document(
        self,
        provider: StorageProvider,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> object:
        """Read and parse a YAML file, raising validation errors on failure."""

        try:
            content = self._read_text(
                provider,
                yml_file,
            )

            return yaml.safe_load(content)

        except UnicodeDecodeError:
            logger.warning(
                "YAML file is not valid UTF-8: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_CONFIGURATION_YML_MISSING,
            )

        except yaml.YAMLError:
            logger.warning(
                "Invalid YAML file: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_CONFIGURATION_INVALID_YML,
            )

    def _run_feed_configuration_validation(
        self,
        configuration_context: ConfigurationContext,
        *,
        scope_label: str,
        success_message: str,
        unexpected_error_message: str,
        validate_file: Callable[
            [StorageProvider, StoragePath, logging.Logger],
            None,
        ],
    ) -> ValidationResult:
        """Run a validation rule across all feed-configuration YAML files."""

        logger = configuration_context.logging.logger
        provider = configuration_context.storage_manager.provider
        root = configuration_context.storage_path
        ignored_directories, ignored_files = ignored_paths(configuration_context)
        path = feed_configuration_path(root)

        logger.info(
            "Starting %s validation under %s",
            scope_label,
            path.uri,
        )

        try:
            yml_files = self._discover_yml_files(
                provider,
                root,
                ignored_directories,
                ignored_files,
                logger,
            )

            logger.info(
                "Found %d YAML files for %s validation",
                len(yml_files),
                scope_label,
            )

            for yml_file in yml_files:
                validate_file(
                    provider,
                    yml_file,
                    logger,
                )

        except ValidationError as exc:
            logger.warning(
                "%s validation failed: %s",
                scope_label.capitalize(),
                exc,
            )
            raise

        except Exception as exc:
            logger.exception(unexpected_error_message)

            raise ValidationError(
                ValidationErrors.VALIDATION_UNKNOWN,
                cause=exc,
            ) from exc

        logger.info(success_message)

        return ValidationResult(
            self.key,
            self.name,
            True,
            success_message,
        )
