"""Feed specifications validation for HanduFLOW."""

from __future__ import annotations

import logging
import re
from typing import cast

import yaml

from handuflow.platform.exceptions.definition import ErrorDefinition

from ...configurator.dataclasses.context import ConfigurationContext
from ...exceptions.domains.validation import ValidationError
from ...exceptions.errors.validation import ValidationErrors
from ...storage import StoragePath
from ...storage.base import StorageProvider
from ..base import Validation
from ..dataclasses import ValidationResult

FEED_CONFIGURATION_DIR = "feed_configuration"
YML_SUFFIX = ".yml"

VALID_SCHEMA_TYPES: set[str] = {
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

DECIMAL_TYPE_PATTERN = re.compile(
    r"^decimal\(\d+,\d+\)$",
)


class EnforceFeedSpecs(Validation):
    """Validate feed_specs in HanduFLOW feed configuration files."""

    @property
    def name(self) -> str:
        """Return validation name."""
        return "enforce_feed_specs"

    @property
    def key(self) -> int:
        """Return validation execution key."""
        return 7

    def validate(
        self,
        configuration_context: ConfigurationContext,
    ) -> ValidationResult:
        """Validate feed_specs in all feed configuration YAML files."""

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
            "Starting feed_specs validation under %s",
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
                "Found %d YAML files for feed_specs validation",
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
                "Feed specs validation failed: %s",
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
                "Unexpected error during feed_specs validation.",
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

        message = "Feed specifications are valid."

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
        """Validate feed_specs in one YAML file."""

        logger.info(
            "Validating feed specifications: %s",
            yml_file.uri,
        )

        try:
            content = self._read_text(
                provider,
                yml_file,
            )

            data: object = yaml.safe_load(content)

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

        root_data = self.__require_mapping(
            data,
            ValidationErrors.FEED_CONFIGURATION_INVALID_YML,
        )

        # -----------------------------------------------------
        # feed_specs
        # -----------------------------------------------------

        if "feed_specs" not in root_data:
            logger.warning(
                "feed_specs section is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_MISSING,
            )

        feed_specs_value = root_data["feed_specs"]

        feed_specs = self.__require_mapping(
            feed_specs_value,
            ValidationErrors.FEED_SPECS_INVALID,
        )

        # -----------------------------------------------------
        # primary_key
        # -----------------------------------------------------

        self.__validate_primary_key(
            feed_specs,
            yml_file,
            logger,
        )

        # -----------------------------------------------------
        # composite_key
        # -----------------------------------------------------

        if "composite_key" in feed_specs:
            self.__validate_column_list(
                feed_specs["composite_key"],
                "composite_key",
                yml_file,
                logger,
            )

        # -----------------------------------------------------
        # partition_columns
        # -----------------------------------------------------

        if "partition_columns" in feed_specs:
            self.__validate_column_list(
                feed_specs["partition_columns"],
                "partition_columns",
                yml_file,
                logger,
            )

        # -----------------------------------------------------
        # optimize_command
        # -----------------------------------------------------

        if "optimize_command" in feed_specs:
            self.__validate_optimize_command(
                feed_specs["optimize_command"],
                yml_file,
                logger,
            )

        # -----------------------------------------------------
        # custom_selection
        # -----------------------------------------------------

        if "custom_selection" in feed_specs:
            self.__validate_custom_selection(
                feed_specs["custom_selection"],
                yml_file,
                logger,
            )

        # -----------------------------------------------------
        # enforce_schema
        # -----------------------------------------------------

        if "enforce_schema" in feed_specs:
            self.__validate_enforce_schema(
                feed_specs["enforce_schema"],
                yml_file,
                logger,
            )

        logger.info(
            "Feed specifications are valid: %s",
            yml_file.uri,
        )

    # =========================================================
    # primary_key
    # =========================================================

    def __validate_primary_key(
        self,
        feed_specs: dict[str, object],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_specs.primary_key."""

        primary_key = feed_specs.get("primary_key")

        if not isinstance(primary_key, str):
            logger.warning(
                "feed_specs.primary_key is missing or invalid: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_PRIMARY_KEY_MISSING,
            )

        if not primary_key.strip():
            logger.warning(
                "feed_specs.primary_key cannot be blank: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_PRIMARY_KEY_MISSING,
            )

    # =========================================================
    # Column list
    # =========================================================

    def __validate_column_list(
        self,
        value: object,
        field_name: str,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate a list of column names."""

        if not isinstance(value, list):
            logger.warning(
                "feed_specs.%s must be a list: %s",
                field_name,
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_COLUMN_LIST_INVALID,
            )

        if not value:
            logger.warning(
                "feed_specs.%s cannot be empty: %s",
                field_name,
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_COLUMN_LIST_INVALID,
            )

        value = cast(list[object], value)

        for column_value in value:
            if not isinstance(column_value, str):
                logger.warning(
                    "feed_specs.%s contains an invalid column: %s",
                    field_name,
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.FEED_SPECS_COLUMN_LIST_INVALID,
                )

            column_name = column_value

            if not column_name.strip():
                logger.warning(
                    "feed_specs.%s contains a blank column: %s",
                    field_name,
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.FEED_SPECS_COLUMN_LIST_INVALID,
                )

    # =========================================================
    # optimize_command
    # =========================================================

    def __validate_optimize_command(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_specs.optimize_command."""

        optimize_command = self.__require_mapping(
            value,
            ValidationErrors.FEED_SPECS_OPTIMIZE_COMMAND_INVALID,
        )

        # -----------------------------------------------------
        # enabled
        # -----------------------------------------------------

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
                "feed_specs.optimize_command.enabled " "must be a boolean: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_OPTIMIZE_ENABLED_INVALID,
            )

        # -----------------------------------------------------
        # where
        # -----------------------------------------------------

        if "where" in optimize_command:
            self.__validate_where(
                optimize_command["where"],
                yml_file,
                logger,
            )

        # -----------------------------------------------------
        # zorder_by
        # -----------------------------------------------------

        if "zorder_by" in optimize_command:
            self.__validate_zorder_by(
                optimize_command["zorder_by"],
                yml_file,
                logger,
            )

    # =========================================================
    # optimize where
    # =========================================================

    def __validate_where(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate optimize_command.where."""

        if not isinstance(value, dict):
            logger.warning(
                "feed_specs.optimize_command.where " "must be a mapping: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_OPTIMIZE_WHERE_INVALID,
            )

        where = cast(dict[str, object], value)

        if not where:
            logger.warning(
                "feed_specs.optimize_command.where " "cannot be empty: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_OPTIMIZE_WHERE_INVALID,
            )

        for column_value in where.keys():
            if not column_value.strip():
                logger.warning(
                    "feed_specs.optimize_command.where " "contains a blank column: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.FEED_SPECS_OPTIMIZE_WHERE_INVALID,
                )

    # =========================================================
    # zorder_by
    # =========================================================

    def __validate_zorder_by(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate optimize_command.zorder_by."""

        if not isinstance(value, list):
            logger.warning(
                "feed_specs.optimize_command.zorder_by " "must be a list: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_ZORDER_BY_INVALID,
            )

        zorder_by = cast(list[object], value)

        if not zorder_by:
            logger.warning(
                "feed_specs.optimize_command.zorder_by " "cannot be empty: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_ZORDER_BY_INVALID,
            )

        for column_value in zorder_by:
            if not isinstance(column_value, str):
                logger.warning(
                    "feed_specs.optimize_command.zorder_by "
                    "contains an invalid column: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.FEED_SPECS_ZORDER_BY_INVALID,
                )

            if not column_value.strip():
                logger.warning(
                    "feed_specs.optimize_command.zorder_by "
                    "contains a blank column: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.FEED_SPECS_ZORDER_BY_INVALID,
                )

    # =========================================================
    # custom_selection
    # =========================================================

    def __validate_custom_selection(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_specs.custom_selection."""

        custom_selection = self.__require_mapping(
            value,
            ValidationErrors.FEED_SPECS_CUSTOM_SELECTION_INVALID,
        )

        # -----------------------------------------------------
        # enabled
        # -----------------------------------------------------

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
                "feed_specs.custom_selection.enabled " "must be a boolean: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_CUSTOM_SELECTION_ENABLED_INVALID,
            )

        # -----------------------------------------------------
        # sql_file
        # -----------------------------------------------------

        if enabled:
            if "sql_file" not in custom_selection:
                logger.warning(
                    "feed_specs.custom_selection.sql_file " "is missing: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.FEED_SPECS_CUSTOM_SELECTION_SQL_FILE_MISSING,
                )

            sql_file = custom_selection["sql_file"]

            if not isinstance(sql_file, str):
                logger.warning(
                    "feed_specs.custom_selection.sql_file " "must be a string: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.FEED_SPECS_CUSTOM_SELECTION_SQL_FILE_MISSING,
                )

            if not sql_file.strip():
                logger.warning(
                    "feed_specs.custom_selection.sql_file " "cannot be blank: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.FEED_SPECS_CUSTOM_SELECTION_SQL_FILE_MISSING,
                )

    # =========================================================
    # enforce_schema
    # =========================================================

    def __validate_enforce_schema(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate feed_specs.enforce_schema."""

        enforce_schema = self.__require_mapping(
            value,
            ValidationErrors.FEED_SPECS_ENFORCE_SCHEMA_INVALID,
        )

        # -----------------------------------------------------
        # type
        # -----------------------------------------------------

        if "type" not in enforce_schema:
            logger.warning(
                "feed_specs.enforce_schema.type is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_ENFORCE_SCHEMA_TYPE_INVALID,
            )

        schema_type = enforce_schema["type"]

        if not isinstance(schema_type, str):
            logger.warning(
                "feed_specs.enforce_schema.type " "must be a string: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_ENFORCE_SCHEMA_TYPE_INVALID,
            )

        if schema_type != "struct":
            logger.warning(
                "feed_specs.enforce_schema.type " "must be 'struct': %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_ENFORCE_SCHEMA_TYPE_INVALID,
            )

        # -----------------------------------------------------
        # fields
        # -----------------------------------------------------

        if "fields" not in enforce_schema:
            logger.warning(
                "feed_specs.enforce_schema.fields is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_ENFORCE_SCHEMA_FIELDS_INVALID,
            )

        fields_value = enforce_schema["fields"]

        if not isinstance(fields_value, list):
            logger.warning(
                "feed_specs.enforce_schema.fields " "must be a list: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_ENFORCE_SCHEMA_FIELDS_INVALID,
            )

        fields: list[object] = cast(list[object], fields_value)

        if not fields:
            logger.warning(
                "feed_specs.enforce_schema.fields " "cannot be empty: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_ENFORCE_SCHEMA_FIELDS_INVALID,
            )

        for field_value in fields:
            self.__validate_schema_field(
                field_value,
                yml_file,
                logger,
            )

    # =========================================================
    # Schema field
    # =========================================================

    def __validate_schema_field(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate one enforce_schema field."""

        field = self.__require_mapping(
            value,
            ValidationErrors.FEED_SPECS_SCHEMA_FIELD_INVALID,
        )

        # -----------------------------------------------------
        # name
        # -----------------------------------------------------

        if "name" not in field:
            logger.warning(
                "Schema field name is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_NAME_MISSING,
            )

        name = field["name"]

        if not isinstance(name, str):
            logger.warning(
                "Schema field name must be a string: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_NAME_MISSING,
            )

        if not name.strip():
            logger.warning(
                "Schema field name cannot be blank: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_NAME_MISSING,
            )

        # -----------------------------------------------------
        # type
        # -----------------------------------------------------

        if "type" not in field:
            logger.warning(
                "Schema field type is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_TYPE_INVALID,
            )

        field_type = field["type"]

        if not isinstance(field_type, str):
            logger.warning(
                "Schema field type must be a string: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_TYPE_INVALID,
            )

        if not self.__is_valid_schema_type(field_type):
            logger.warning(
                "Invalid schema field type '%s': %s",
                field_type,
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_TYPE_INVALID,
            )

        # -----------------------------------------------------
        # nullable
        # -----------------------------------------------------

        if "nullable" not in field:
            logger.warning(
                "Schema field nullable is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_NULLABLE_INVALID,
            )

        nullable = field["nullable"]

        if not isinstance(nullable, bool):
            logger.warning(
                "Schema field nullable must be true or false: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_NULLABLE_INVALID,
            )

        # -----------------------------------------------------
        # metadata
        # -----------------------------------------------------

        if "metadata" not in field:
            logger.warning(
                "Schema field metadata is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_METADATA_INVALID,
            )

        metadata_value = field["metadata"]

        if not isinstance(metadata_value, dict):
            logger.warning(
                "Schema field metadata must be a mapping: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.FEED_SPECS_SCHEMA_FIELD_METADATA_INVALID,
            )

        metadata: dict[str, object] = cast(dict[str, object], metadata_value)

        # keys are statically typed as str (dict[str, object]) so no runtime check
        for _ in metadata.keys():
            pass

    # =========================================================
    # Mapping helper
    # =========================================================

    @staticmethod
    def __require_mapping(
        value: object,
        error: ErrorDefinition,
    ) -> dict[str, object]:
        """Validate and return a YAML mapping with string keys."""

        if not isinstance(value, dict):
            raise ValidationError(error)

        mapping = cast(dict[str, object], value)
        result: dict[str, object] = {}

        for key, item in mapping.items():
            result[key] = item

        return result

    # =========================================================
    # Spark data types
    # =========================================================

    @staticmethod
    def __is_valid_schema_type(
        field_type: str,
    ) -> bool:
        """Return whether a schema field type is supported."""

        normalized_type = field_type.strip()

        if normalized_type in VALID_SCHEMA_TYPES:
            return True

        return (
            DECIMAL_TYPE_PATTERN.fullmatch(
                normalized_type,
            )
            is not None
        )
