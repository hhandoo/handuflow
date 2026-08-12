"""Source and target validation for HanduFLOW."""

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


class EnforceSourceAndTarget(Validation):
    """Validate source and target in HanduFLOW feed configuration files."""

    @property
    def name(self) -> str:
        return "enforce_source_and_target"

    @property
    def key(self) -> int:
        return 6

    def validate(
        self,
        configuration_context: ConfigurationContext,
    ) -> ValidationResult:
        """Validate source and target in all feed configuration YAML files."""

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
            "Starting source and target validation under %s",
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
                "Found %d YAML files for source and target validation",
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
                "Source and target validation failed: %s",
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
                "Unexpected error during source and target validation.",
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

        message = "Source and target are valid."

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
        """Validate source and target in one YAML file."""

        logger.info(
            "Validating source and target: %s",
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
        # Source
        # -----------------------------------------------------

        source = data.get("source")

        if source is None:
            logger.warning(
                "source section is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.SOURCE_MISSING,
            )

        if not isinstance(source, dict):
            logger.warning(
                "source must be a mapping: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.SOURCE_INVALID,
            )

        source = cast(
            dict[str, Any],
            source,
        )

        self.__validate_section(
            source,
            "source",
            yml_file,
            logger,
        )

        # -----------------------------------------------------
        # Target
        # -----------------------------------------------------

        target = data.get("target")

        if target is None:
            logger.warning(
                "target section is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.TARGET_MISSING,
            )

        if not isinstance(target, dict):
            logger.warning(
                "target must be a mapping: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.TARGET_INVALID,
            )

        target = cast(
            dict[str, Any],
            target,
        )

        self.__validate_section(
            target,
            "target",
            yml_file,
            logger,
        )

        logger.info(
            "Source and target are valid: %s",
            yml_file.uri,
        )

    # =========================================================
    # Source / Target section
    # =========================================================

    def __validate_section(
        self,
        section: dict[str, Any],
        section_name: str,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate a source or target section."""

        self.__validate_field(
            section,
            section_name,
            "type",
            yml_file,
            logger,
        )

        self.__validate_field(
            section,
            section_name,
            "format",
            yml_file,
            logger,
        )

        self.__validate_field(
            section,
            section_name,
            "schema",
            yml_file,
            logger,
        )

        self.__validate_field(
            section,
            section_name,
            "table",
            yml_file,
            logger,
        )

    # =========================================================
    # Source / Target fields
    # =========================================================

    def __validate_field(
        self,
        section: dict[str, Any],
        section_name: str,
        field_name: str,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate a mandatory source or target field."""

        value = section.get(field_name)

        if not isinstance(value, str):
            logger.warning(
                "%s.%s is missing or invalid: %s",
                section_name,
                field_name,
                yml_file.uri,
            )

            if section_name == "source":
                self._raise_validation_error(
                    ValidationErrors.SOURCE_FIELD_MISSING,
                )

            self._raise_validation_error(
                ValidationErrors.TARGET_FIELD_MISSING,
            )

        if not value.strip():
            logger.warning(
                "%s.%s cannot be blank: %s",
                section_name,
                field_name,
                yml_file.uri,
            )

            if section_name == "source":
                self._raise_validation_error(
                    ValidationErrors.SOURCE_FIELD_MISSING,
                )

            self._raise_validation_error(
                ValidationErrors.TARGET_FIELD_MISSING,
            )
