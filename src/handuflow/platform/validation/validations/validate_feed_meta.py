"""Feed metadata validation for HanduFLOW."""

from __future__ import annotations

import logging
from typing import Any, cast
import yaml

from ...configurator.dataclasses.context import ConfigurationContext
from ...exceptions.domains.validation import ValidationError
from ...exceptions.errors.validation import ValidationErrors
from ...storage import StoragePath
from ...storage.base import StorageProvider
from ..base import Validation
from ..dataclasses import ValidationResult

FEED_CONFIGURATION_DIR = "feed_configuration"
YML_SUFFIX = ".yml"

MIN_VACUUM_HOURS = 168
MAX_VACUUM_HOURS = 26280


class FeedMetaValidation(Validation):
    """Validate feed_meta in HanduFLOW feed configuration files."""

    @property
    def name(self) -> str:
        return "feed_meta_validation"

    @property
    def key(self) -> int:
        return 4

    def validate(
        self,
        configuration_context: ConfigurationContext,
    ) -> ValidationResult:
        """Validate feed_meta in all feed configuration YAML files."""

        logger = configuration_context.logging.logger
        provider = configuration_context.storage_manager.provider
        root = configuration_context.storage_path

        ignored_directories = {
            configuration_context.logging.log_directory_name,
        }

        ignored_files = {
            configuration_context.logging.log_file_name,
        }

        feed_configuration_path = StoragePath(
            f"{root.uri}/{FEED_CONFIGURATION_DIR}",
        )

        logger.info(
            "Starting feed_meta validation under %s",
            feed_configuration_path.uri,
        )

        try:
            yml_files = self._recursive_file_lookup(
                provider,
                feed_configuration_path,
                ignored_directories,
                ignored_files,
                logger,
            )

            yml_files = [
                file for file in yml_files if self._has_suffix(file, YML_SUFFIX)
            ]

            logger.info(
                "Found %d YAML files for feed_meta validation",
                len(yml_files),
            )

            for yml_file in yml_files:
                self.__validate_file(
                    provider,
                    yml_file,
                    logger,
                )

        except ValidationError as exc:
            logger.warning(
                "Feed metadata validation failed: %s",
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
                "Unexpected error during feed_meta validation.",
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

        message = "Feed metadata is valid."

        logger.info(message)

        return ValidationResult(
            self.key,
            self.name,
            True,
            message,
        )

    # =========================================================
    # YAML file validation
    # =========================================================

    def __validate_file(
        self,
        provider: StorageProvider,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_meta in one YAML file."""

        logger.info(
            "Validating feed metadata: %s",
            yml_file.uri,
        )

        try:
            content = self._read_text(
                provider,
                yml_file,
            )

            data: dict[str, Any] = yaml.safe_load(content)

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

        # -----------------------------------------------------
        # Root must be a mapping
        # -----------------------------------------------------

        # -----------------------------------------------------
        # feed_meta must exist
        # -----------------------------------------------------

        feed_meta = data.get("feed_meta")

        if feed_meta is None:
            logger.warning(
                "feed_meta section is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_MISSING,
            )

        if not isinstance(feed_meta, dict):
            logger.warning(
                "feed_meta must be a mapping: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_INVALID,
            )

        feed_meta = cast(dict[str, Any], feed_meta)

        self.__validate_unique_identifier(
            feed_meta,
            yml_file,
            logger,
        )

        self.__validate_vacuum_hours(
            feed_meta,
            yml_file,
            logger,
        )

        # upstream_identifier and downstream_identifier
        # are intentionally optional.

        logger.info(
            "Feed metadata is valid: %s",
            yml_file.uri,
        )

    # =========================================================
    # unique_identifier
    # =========================================================

    def __validate_unique_identifier(
        self,
        feed_meta: dict[Any, Any],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_meta.unique_identifier."""

        unique_identifier = feed_meta.get(
            "unique_identifier",
        )

        if not isinstance(unique_identifier, str):
            logger.warning(
                "feed_meta.unique_identifier is missing or invalid: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_UNIQUE_IDENTIFIER_MISSING,
            )

        if not unique_identifier.strip():
            logger.warning(
                "feed_meta.unique_identifier cannot be empty: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_UNIQUE_IDENTIFIER_MISSING,
            )

    # =========================================================
    # vacuum_hours
    # =========================================================

    def __validate_vacuum_hours(
        self,
        feed_meta: dict[Any, Any],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_meta.vacuum_hours."""

        vacuum_hours = feed_meta.get(
            "vacuum_hours",
        )

        if vacuum_hours is None:
            logger.warning(
                "feed_meta.vacuum_hours is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_VACUUM_HOURS_MISSING,
            )

        # bool is technically an int in Python, but should not
        # be accepted as a vacuum hour value.
        if isinstance(vacuum_hours, bool):
            logger.warning(
                "feed_meta.vacuum_hours must be an integer: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_VACUUM_HOURS_INVALID,
            )

        if not isinstance(vacuum_hours, int):
            logger.warning(
                "feed_meta.vacuum_hours must be an integer: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_VACUUM_HOURS_INVALID,
            )

        if not (MIN_VACUUM_HOURS <= vacuum_hours <= MAX_VACUUM_HOURS):
            logger.warning(
                "feed_meta.vacuum_hours is outside the allowed " "range [%d, %d]: %s",
                MIN_VACUUM_HOURS,
                MAX_VACUUM_HOURS,
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_VACUUM_HOURS_OUT_OF_RANGE,
            )
