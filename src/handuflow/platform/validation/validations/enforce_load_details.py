"""Load details validation for HanduFLOW."""

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

LOAD_TYPES = {
    "FULL_LOAD",
    "INCREMENTAL_CDC",
    "APPEND_LOAD",
    "SCD_TYPE_2",
}


class EnforceLoadDetails(Validation):
    """Validate load_details in HanduFLOW feed configuration files."""

    @property
    def name(self) -> str:
        return "enforce_load_details"

    @property
    def key(self) -> int:
        return 5

    def validate(
        self,
        configuration_context: ConfigurationContext,
    ) -> ValidationResult:
        """Validate load_details in all feed configuration YAML files."""

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
            "Starting load_details validation under %s",
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
                "Found %d YAML files for load_details validation",
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
                "Load details validation failed: %s",
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
                "Unexpected error during load_details validation.",
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

        message = "Load details are valid."

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
        """Validate load_details in one YAML file."""

        logger.info(
            "Validating load details: %s",
            yml_file.uri,
        )

        try:
            content = self._read_text(
                provider,
                yml_file,
            )

            data = yaml.safe_load(content)

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

        if not isinstance(data, dict):
            logger.warning(
                "YAML root must be a mapping: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_CONFIGURATION_INVALID_YML,
            )

        data = cast(
            dict[str, Any],
            data,
        )

        # -----------------------------------------------------
        # load_details must exist
        # -----------------------------------------------------

        load_details = data.get("load_details")

        if load_details is None:
            logger.warning(
                "load_details section is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_LOAD_DETAILS_MISSING,
            )

        if not isinstance(load_details, dict):
            logger.warning(
                "load_details must be a mapping: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_LOAD_DETAILS_INVALID,
            )

        load_details = cast(
            dict[str, Any],
            load_details,
        )

        self.__validate_type(
            load_details,
            yml_file,
            logger,
        )

        logger.info(
            "Load details are valid: %s",
            yml_file.uri,
        )

    # =========================================================
    # load_details.type
    # =========================================================

    def __validate_type(
        self,
        load_details: dict[str, Any],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate load_details.type."""

        load_type = load_details.get("type")

        if not isinstance(load_type, str):
            logger.warning(
                "load_details.type is missing or invalid: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_LOAD_DETAILS_TYPE_MISSING,
            )

        if not load_type.strip():
            logger.warning(
                "load_details.type cannot be blank: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_LOAD_DETAILS_TYPE_MISSING,
            )

        if load_type not in LOAD_TYPES:
            logger.warning(
                "Invalid load_details.type '%s': %s",
                load_type,
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_LOAD_DETAILS_TYPE_INVALID,
            )
