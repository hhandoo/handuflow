"""Feed specifications validation for HanduFLOW."""

from __future__ import annotations

import logging
import re
from typing import cast

from ...configurator.dataclasses.context import ConfigurationContext
from ...exceptions.errors.validation import ValidationErrors
from ...storage import StoragePath
from ...storage.base import StorageProvider
from ..dataclasses import ValidationResult
from ._common import FeedConfigurationValidation, require_mapping

VALID_SCHEMA_TYPES: frozenset[str] = frozenset(
    {
        "string",
        "binary",
        "boolean",
        "byte",
        "short",
        "integer",
        "long",
        "float",
        "double",
        "date",
        "timestamp",
        "timestamp_ntz",
        "interval",
        "interval year to month",
        "interval day to second",
        "void",
        "array",
        "map",
        "struct",
    }
)

DECIMAL_TYPE_PATTERN = re.compile(
    r"^decimal\(\d+,\d+\)$",
)


class EnforceFeedSpecs(FeedConfigurationValidation):
    """Validate feed_specs in HanduFLOW feed configuration files."""

    @property
    def name(self) -> str:
        return "enforce_feed_specs"

    @property
    def key(self) -> int:
        return 7

    def validate(
        self,
        configuration_context: ConfigurationContext,
    ) -> ValidationResult:
        """Validate feed_specs in all feed configuration YAML files."""

        return self._run_feed_configuration_validation(
            configuration_context,
            scope_label="feed_specs",
            success_message="Feed specifications are valid.",
            unexpected_error_message="Unexpected error during feed_specs validation.",
            validate_file=self.__validate_file,
        )

    def __validate_file(
        self,
        provider: StorageProvider,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_specs in one YAML file."""

        logger.info(
            "Validating feed specifications: %s",
            yml_file.uri,
        )

        root_data = require_mapping(
            self._load_yaml_document(
                provider,
                yml_file,
                logger,
            ),
            ValidationErrors.FEED_CONFIGURATION_INVALID_YML,
        )

        if "feed_specs" not in root_data:
            logger.warning(
                "feed_specs section is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_MISSING,
            )

        feed_specs = require_mapping(
            root_data["feed_specs"],
            ValidationErrors.FEED_SPECS_INVALID,
        )

        self.__validate_primary_key(
            feed_specs,
            yml_file,
            logger,
        )

        optional_validators: tuple[tuple[str, object], ...] = (
            ("composite_key", self.__validate_column_list),
            ("partition_columns", self.__validate_column_list),
            ("optimize_command", self.__validate_optimize_command),
            ("custom_selection", self.__validate_custom_selection),
            ("enforce_schema", self.__validate_enforce_schema),
        )

        for field_name, validator in optional_validators:
            if field_name in feed_specs:
                validator(
                    feed_specs[field_name],
                    field_name,
                    yml_file,
                    logger,
                )

        logger.info(
            "Feed specifications are valid: %s",
            yml_file.uri,
        )

    def __validate_primary_key(
        self,
        feed_specs: dict[str, object],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_specs.primary_key."""

        primary_key = feed_specs.get("primary_key")

        if not isinstance(primary_key, str) or not primary_key.strip():
            logger.warning(
                "feed_specs.primary_key is missing or invalid: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_PRIMARY_KEY_MISSING,
            )

    def __validate_column_list(
        self,
        value: object,
        field_name: str,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate a list of column names."""

        if not isinstance(value, list) or not value:
            logger.warning(
                "feed_specs.%s must be a non-empty list: %s",
                field_name,
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_COLUMN_LIST_INVALID,
            )

        for column_value in cast(list[object], value):
            if not isinstance(column_value, str) or not column_value.strip():
                logger.warning(
                    "feed_specs.%s contains an invalid column: %s",
                    field_name,
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.FEED_SPECS_COLUMN_LIST_INVALID,
                )

    def __validate_optimize_command(
        self,
        value: object,
        _field_name: str,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_specs.optimize_command."""

        optimize_command = require_mapping(
            value,
            ValidationErrors.FEED_SPECS_OPTIMIZE_COMMAND_INVALID,
        )

        if "enabled" not in optimize_command:
            logger.warning(
                "feed_specs.optimize_command.enabled is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_OPTIMIZE_ENABLED_INVALID,
            )

        enabled = optimize_command["enabled"]

        if not isinstance(enabled, bool):
            logger.warning(
                "feed_specs.optimize_command.enabled must be a boolean: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_OPTIMIZE_ENABLED_INVALID,
            )

        if "where" in optimize_command:
            self.__validate_where(
                optimize_command["where"],
                yml_file,
                logger,
            )

        if "zorder_by" in optimize_command:
            self.__validate_zorder_by(
                optimize_command["zorder_by"],
                yml_file,
                logger,
            )

    def __validate_where(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate optimize_command.where."""

        if not isinstance(value, dict) or not value:
            logger.warning(
                "feed_specs.optimize_command.where must be a non-empty mapping: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_OPTIMIZE_WHERE_INVALID,
            )

        where = cast(dict[str, object], value)

        for column_name in where:
            if not column_name.strip():
                logger.warning(
                    "feed_specs.optimize_command.where contains a blank column: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.FEED_SPECS_OPTIMIZE_WHERE_INVALID,
                )

    def __validate_zorder_by(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate optimize_command.zorder_by."""

        if not isinstance(value, list) or not value:
            logger.warning(
                "feed_specs.optimize_command.zorder_by must be a non-empty list: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_ZORDER_BY_INVALID,
            )

        for column_value in cast(list[object], value):
            if not isinstance(column_value, str) or not column_value.strip():
                logger.warning(
                    "feed_specs.optimize_command.zorder_by contains an invalid column: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.FEED_SPECS_ZORDER_BY_INVALID,
                )

    def __validate_custom_selection(
        self,
        value: object,
        _field_name: str,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_specs.custom_selection."""

        custom_selection = require_mapping(
            value,
            ValidationErrors.FEED_SPECS_CUSTOM_SELECTION_INVALID,
        )

        if "enabled" not in custom_selection:
            logger.warning(
                "feed_specs.custom_selection.enabled is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_CUSTOM_SELECTION_ENABLED_INVALID,
            )

        enabled = custom_selection["enabled"]

        if not isinstance(enabled, bool):
            logger.warning(
                "feed_specs.custom_selection.enabled must be a boolean: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_CUSTOM_SELECTION_ENABLED_INVALID,
            )

        if not enabled:
            return

        sql_file = custom_selection.get("sql_file")

        if not isinstance(sql_file, str) or not sql_file.strip():
            logger.warning(
                "feed_specs.custom_selection.sql_file is missing or invalid: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_CUSTOM_SELECTION_SQL_FILE_MISSING,
            )

    def __validate_enforce_schema(
        self,
        value: object,
        _field_name: str,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_specs.enforce_schema."""

        enforce_schema = require_mapping(
            value,
            ValidationErrors.FEED_SPECS_ENFORCE_SCHEMA_INVALID,
        )

        schema_type = enforce_schema.get("type")

        if schema_type != "struct":
            logger.warning(
                "feed_specs.enforce_schema.type must be 'struct': %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_ENFORCE_SCHEMA_TYPE_INVALID,
            )

        fields_value = enforce_schema.get("fields")

        if not isinstance(fields_value, list) or not fields_value:
            logger.warning(
                "feed_specs.enforce_schema.fields must be a non-empty list: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_ENFORCE_SCHEMA_FIELDS_INVALID,
            )

        for field_value in cast(list[object], fields_value):
            self.__validate_schema_field(
                field_value,
                yml_file,
                logger,
            )

    def __validate_schema_field(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate one enforce_schema field."""

        field = require_mapping(
            value,
            ValidationErrors.FEED_SPECS_SCHEMA_FIELD_INVALID,
        )

        name = field.get("name")

        if not isinstance(name, str) or not name.strip():
            logger.warning(
                "Schema field name is missing or invalid: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_NAME_MISSING,
            )

        field_type = field.get("type")

        if not isinstance(field_type, str) or not self.__is_valid_schema_type(
            field_type
        ):
            logger.warning(
                "Schema field type is missing or invalid: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_TYPE_INVALID,
            )

        nullable = field.get("nullable")

        if not isinstance(nullable, bool):
            logger.warning(
                "Schema field nullable must be true or false: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_NULLABLE_INVALID,
            )

        metadata_value = field.get("metadata")

        if not isinstance(metadata_value, dict):
            logger.warning(
                "Schema field metadata must be a mapping: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_METADATA_INVALID,
            )

    @staticmethod
    def __is_valid_schema_type(
        field_type: str,
    ) -> bool:
        """Return whether a schema field type is supported."""

        normalized_type = field_type.strip()

        if normalized_type in VALID_SCHEMA_TYPES:
            return True

        return DECIMAL_TYPE_PATTERN.fullmatch(normalized_type) is not None
