"""Load details validation for HanduFLOW."""

from __future__ import annotations

import logging
from typing import Any

from ...configurator.dataclasses.context import ConfigurationContext
from ...exceptions.errors.validation import ValidationErrors
from ...storage import StoragePath
from ...storage.base import StorageProvider
from ..dataclasses import ValidationResult
from ._common import FeedConfigurationValidation, require_mapping

LOAD_TYPES = frozenset(
    {
        "FULL_LOAD",
        "INCREMENTAL_CDC",
        "APPEND_LOAD",
        "SCD_TYPE_2",
    }
)


class EnforceLoadDetails(FeedConfigurationValidation):
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

        return self._run_feed_configuration_validation(
            configuration_context,
            scope_label="load_details",
            success_message="Load details are valid.",
            unexpected_error_message="Unexpected error during load_details validation.",
            validate_file=self.__validate_file,
        )

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

        data = require_mapping(
            self._load_yaml_document(
                provider,
                yml_file,
                logger,
            ),
            ValidationErrors.FEED_CONFIGURATION_INVALID_YML,
        )

        load_details_value = data.get("load_details")

        if load_details_value is None:
            logger.warning(
                "load_details section is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_LOAD_DETAILS_MISSING,
            )

        load_details = require_mapping(
            load_details_value,
            ValidationErrors.FEED_META_LOAD_DETAILS_INVALID,
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

    def __validate_type(
        self,
        load_details: dict[str, Any],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate load_details.type."""

        load_type = load_details.get("type")

        if not isinstance(load_type, str) or not load_type.strip():
            logger.warning(
                "load_details.type is missing or invalid: %s",
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
