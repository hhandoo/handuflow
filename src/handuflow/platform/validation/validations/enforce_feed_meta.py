"""Feed metadata validation for HanduFLOW."""

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

MIN_VACUUM_HOURS = 168
MAX_VACUUM_HOURS = 26280


class EnforceFeedMeta(FeedConfigurationValidation):
    """Validate feed_meta in HanduFLOW feed configuration files."""

    @property
    def name(self) -> str:
        return "Enforce Feed Meta"

    @property
    def key(self) -> int:
        return 4

    def validate(
        self,
        configuration_context: ConfigurationContext,
    ) -> ValidationResult:
        """Validate feed_meta in all feed configuration YAML files."""

        return self._run_feed_configuration_validation(
            configuration_context,
            scope_label="feed_meta",
            success_message="Feed metadata is valid.",
            unexpected_error_message="Unexpected error during feed_meta validation.",
            validate_file=self.__validate_file,
        )

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

        data = require_mapping(
            self._load_yaml_document(
                provider,
                yml_file,
                logger,
            ),
            ValidationErrors.FEED_CONFIGURATION_INVALID_YML,
        )

        feed_meta_value = data.get("feed_meta")

        if feed_meta_value is None:
            logger.warning(
                "feed_meta section is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_MISSING,
            )

        feed_meta = require_mapping(
            feed_meta_value,
            ValidationErrors.FEED_META_INVALID,
        )

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

        self.__validate_optional_string_field(
            feed_meta,
            "upstream_identifier",
            ValidationErrors.FEED_META_UPSTREAM_IDENTIFIER_INVALID,
            yml_file,
            logger,
        )

        self.__validate_optional_string_field(
            feed_meta,
            "downstream_identifier",
            ValidationErrors.FEED_META_DOWNSTREAM_IDENTIFIER_INVALID,
            yml_file,
            logger,
        )

        self.__validate_optional_string_field(
            feed_meta,
            "batch_key",
            ValidationErrors.FEED_META_BATCH_KEY_INVALID,
            yml_file,
            logger,
        )

        logger.info(
            "Feed metadata is valid: %s",
            yml_file.uri,
        )

    def __validate_unique_identifier(
        self,
        feed_meta: dict[str, Any],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_meta.unique_identifier."""

        unique_identifier = feed_meta.get("unique_identifier")

        if not isinstance(unique_identifier, str) or not unique_identifier.strip():
            logger.warning(
                "feed_meta.unique_identifier is missing or invalid: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_UNIQUE_IDENTIFIER_MISSING,
            )

    def __validate_vacuum_hours(
        self,
        feed_meta: dict[str, Any],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_meta.vacuum_hours."""

        vacuum_hours = feed_meta.get("vacuum_hours")

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
        if isinstance(vacuum_hours, bool) or not isinstance(vacuum_hours, int):
            logger.warning(
                "feed_meta.vacuum_hours must be an integer: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_VACUUM_HOURS_INVALID,
            )

        if not MIN_VACUUM_HOURS <= vacuum_hours <= MAX_VACUUM_HOURS:
            logger.warning(
                "feed_meta.vacuum_hours is outside the allowed range [%d, %d]: %s",
                MIN_VACUUM_HOURS,
                MAX_VACUUM_HOURS,
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_META_VACUUM_HOURS_OUT_OF_RANGE,
            )

    def __validate_optional_string_field(
        self,
        feed_meta: dict[str, Any],
        field_name: str,
        error: ErrorDefinition,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate an optional feed_meta string field."""

        if field_name not in feed_meta:
            return

        value = feed_meta.get(field_name)

        if value is None:
            return

        if not isinstance(value, str) or not value.strip():
            logger.warning(
                "feed_meta.%s is invalid: %s",
                field_name,
                yml_file.uri,
            )

            self._raise_validation_error(error)
