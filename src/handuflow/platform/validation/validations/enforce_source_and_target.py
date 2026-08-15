"""Source and target validation for HanduFLOW."""

from __future__ import annotations

import logging
from typing import Any

from ...configurator.dataclasses.context import ConfigurationContext
from ...exceptions.definition import ErrorDefinition
from ...exceptions.errors.validation import ValidationErrors
from ...storage import StoragePath
from ...storage.base import StorageProvider
from ..dataclasses import ValidationResult
from ._common import FeedConfigurationValidation, require_mapping

_REQUIRED_FIELDS = ("type", "format", "schema", "table")

_SECTION_ERRORS: dict[str, tuple[ErrorDefinition, ErrorDefinition]] = {
    "source": (
        ValidationErrors.SOURCE_MISSING,
        ValidationErrors.SOURCE_INVALID,
    ),
    "target": (
        ValidationErrors.TARGET_MISSING,
        ValidationErrors.TARGET_INVALID,
    ),
}

_FIELD_ERRORS: dict[str, ErrorDefinition] = {
    "source": ValidationErrors.SOURCE_FIELD_MISSING,
    "target": ValidationErrors.TARGET_FIELD_MISSING,
}


class EnforceSourceAndTarget(FeedConfigurationValidation):
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

        return self._run_feed_configuration_validation(
            configuration_context,
            scope_label="source and target",
            success_message="Source and target are valid.",
            unexpected_error_message=(
                "Unexpected error during source and target validation."
            ),
            validate_file=self.__validate_file,
        )

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

        data = require_mapping(
            self._load_yaml_document(
                provider,
                yml_file,
                logger,
            ),
            ValidationErrors.FEED_CONFIGURATION_INVALID_YML,
        )

        for section_name in ("source", "target"):
            self.__validate_section(
                data.get(section_name),
                section_name,
                yml_file,
                logger,
            )

        logger.info(
            "Source and target are valid: %s",
            yml_file.uri,
        )

    def __validate_section(
        self,
        section_value: object,
        section_name: str,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate a source or target section."""

        missing_error, invalid_error = _SECTION_ERRORS[section_name]

        if section_value is None:
            logger.warning(
                "%s section is missing: %s",
                section_name,
                yml_file.uri,
            )

            self._raise_validation_error(missing_error)

        section = require_mapping(
            section_value,
            invalid_error,
        )

        for field_name in _REQUIRED_FIELDS:
            self.__validate_field(
                section,
                section_name,
                field_name,
                yml_file,
                logger,
            )

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
        field_error = _FIELD_ERRORS[section_name]

        if not isinstance(value, str) or not value.strip():
            logger.warning(
                "%s.%s is missing or invalid: %s",
                section_name,
                field_name,
                yml_file.uri,
            )

            self._raise_validation_error(field_error)
