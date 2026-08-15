"""Data quality checks validation for HanduFLOW."""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import cast

import yaml

from ...configurator.dataclasses.context import ConfigurationContext
from ...exceptions.domains.validation import ValidationError
from ...exceptions.errors.validation import ErrorDefinition, ValidationErrors
from ...storage import StoragePath
from ...storage.base import StorageProvider
from ..base import Validation
from ..dataclasses import ValidationResult

FEED_CONFIGURATION_DIR = "feed_configuration"
YML_SUFFIX = ".yml"

VALID_RUN_TYPES: set[str] = {
    "PRE_LOAD",
    "POST_LOAD",
}

VALID_CHECK_NAMES: set[str] = {
    "range_check",
    "duplicate_check",
    "not_blank_check",
    "null_check",
    "custom_check",
}


class EnforceDataQualityChecks(Validation):
    """Validate data_quality_checks in HanduFLOW feed configuration files."""

    @property
    def name(self) -> str:
        """Return validation name."""
        return "enforce_data_quality_checks"

    @property
    def key(self) -> int:
        """Return validation execution key."""
        return 8

    def validate(
        self,
        configuration_context: ConfigurationContext,
    ) -> ValidationResult:
        """Validate data_quality_checks in all feed configuration YAML files."""

        logger = configuration_context.logging.logger
        provider = configuration_context.storage_manager.provider
        root = configuration_context.storage_path

        ignored_directories: set[str] = {
            configuration_context.logging.log_directory_name,
        }

        ignored_files: set[str] = {
            configuration_context.logging.log_file_name,
        }

        feed_configuration_path = StoragePath(
            f"{root.uri}/{FEED_CONFIGURATION_DIR}",
        )

        logger.info(
            "Starting data quality checks validation under %s",
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
                "Found %d YAML files for data quality checks validation",
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
                "Data quality checks validation failed: %s",
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
                "Unexpected error during data quality checks validation.",
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

        message = "Data quality checks are valid."

        logger.info(message)

        return ValidationResult(
            self.key,
            self.name,
            True,
            message,
        )

    def __validate_file(
        self,
        provider: StorageProvider,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate data_quality_checks in one YAML file."""

        logger.info(
            "Validating data quality checks: %s",
            yml_file.uri,
        )

        try:
            content: str = self._read_text(
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

        root_data = self.__as_string_mapping(
            data,
            ValidationErrors.FEED_CONFIGURATION_INVALID_YML,
        )

        if "data_quality_checks" not in root_data:
            logger.warning(
                "data_quality_checks section is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECKS_MISSING,
            )

        data_quality_checks_value = root_data["data_quality_checks"]

        if not isinstance(data_quality_checks_value, list):
            logger.warning(
                "data_quality_checks must be a list: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECKS_INVALID,
            )

        data_quality_checks = cast(list[object], data_quality_checks_value)

        if not data_quality_checks:
            logger.warning(
                "data_quality_checks cannot be empty: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECKS_INVALID,
            )

        check_group_identifiers: set[str] = set()

        for check_group_value in data_quality_checks:
            check_group = self.__as_string_mapping(
                check_group_value,
                ValidationErrors.DATA_QUALITY_CHECK_GROUP_INVALID,
            )

            self.__validate_check_group(
                check_group,
                check_group_identifiers,
                yml_file,
                logger,
            )

        logger.info(
            "Data quality checks are valid: %s",
            yml_file.uri,
        )

    def __validate_check_group(
        self,
        check_group: dict[str, object],
        check_group_identifiers: set[str],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate one data quality check group."""

        if "check_group_identifier" not in check_group:
            logger.warning(
                "check_group_identifier is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_GROUP_IDENTIFIER_MISSING,
            )

        identifier_value = check_group["check_group_identifier"]

        if not isinstance(identifier_value, str):
            logger.warning(
                "check_group_identifier must be a string: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_GROUP_IDENTIFIER_INVALID,
            )

        check_group_identifier: str = identifier_value.strip()

        if not check_group_identifier:
            logger.warning(
                "check_group_identifier cannot be blank: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_GROUP_IDENTIFIER_INVALID,
            )

        if check_group_identifier in check_group_identifiers:
            logger.warning(
                "Duplicate check_group_identifier '%s': %s",
                check_group_identifier,
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_GROUP_IDENTIFIER_DUPLICATE,
            )

        check_group_identifiers.add(check_group_identifier)

        if "description" not in check_group:
            logger.warning(
                "description is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_DESCRIPTION_MISSING,
            )

        description_value = check_group["description"]

        if not isinstance(description_value, str):
            logger.warning(
                "description must be a string: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_DESCRIPTION_INVALID,
            )

        if not description_value.strip():
            logger.warning(
                "description cannot be blank: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_DESCRIPTION_INVALID,
            )

        if "run_type" not in check_group:
            logger.warning(
                "run_type is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_RUN_TYPE_MISSING,
            )

        run_type_value = check_group["run_type"]

        if not isinstance(run_type_value, str):
            logger.warning(
                "run_type must be a string: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_RUN_TYPE_INVALID,
            )

        if run_type_value not in VALID_RUN_TYPES:
            logger.warning(
                "Invalid run_type '%s': %s",
                run_type_value,
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_RUN_TYPE_INVALID,
            )

        if "dependency_datasets" in check_group:
            self.__validate_dependency_datasets(
                check_group["dependency_datasets"],
                yml_file,
                logger,
            )

        if "column" not in check_group:
            logger.warning(
                "column is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_COLUMN_MISSING,
            )

        column_value = check_group["column"]

        if not isinstance(column_value, str):
            logger.warning(
                "column must be a string: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_COLUMN_INVALID,
            )

        if not column_value.strip():
            logger.warning(
                "column cannot be blank: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_COLUMN_INVALID,
            )

        # -----------------------------------------------------
        # checks
        # -----------------------------------------------------

        if "checks" not in check_group:
            logger.warning(
                "checks is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECKS_LIST_MISSING,
            )

        checks_value = check_group["checks"]

        if not isinstance(checks_value, list):
            logger.warning(
                "checks must be a list: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECKS_LIST_INVALID,
            )

        checks: list[object] = cast(list[object], checks_value)

        if not checks:
            logger.warning(
                "checks cannot be empty: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECKS_LIST_INVALID,
            )

        for check_value in checks:
            check = self.__as_string_mapping(
                check_value,
                ValidationErrors.DATA_QUALITY_CHECK_INVALID,
            )

            self.__validate_check(
                check,
                yml_file,
                logger,
            )

    # =========================================================
    # dependency_datasets
    # =========================================================

    def __validate_dependency_datasets(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate dependency_datasets."""

        if not isinstance(value, list):
            logger.warning(
                "dependency_datasets must be a list: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_DEPENDENCY_DATASETS_INVALID,
            )

        dependency_datasets = cast(list[str], value)

        for dataset_value in dependency_datasets:
            if not dataset_value.strip():
                logger.warning(
                    "dependency_datasets cannot contain blank values: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.DATA_QUALITY_DEPENDENCY_DATASETS_INVALID,
                )

    # =========================================================
    # Individual check
    # =========================================================

    def __validate_check(
        self,
        check: dict[str, object],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate one data quality check."""

        if "name" not in check:
            logger.warning(
                "Data quality check name is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_NAME_MISSING,
            )

        check_name_value = check["name"]

        if not isinstance(check_name_value, str):
            logger.warning(
                "Data quality check name must be a string: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_NAME_INVALID,
            )

        check_name = check_name_value.strip()

        if check_name not in VALID_CHECK_NAMES:
            logger.warning(
                "Invalid data quality check name '%s': %s",
                check_name,
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_NAME_INVALID,
            )

        if check_name == "range_check":
            self.__validate_range_check(
                check,
                yml_file,
                logger,
            )
            return

        if check_name == "duplicate_check":
            self.__validate_simple_check(
                check,
                yml_file,
                logger,
            )
            return

        if check_name == "not_blank_check":
            self.__validate_simple_check(
                check,
                yml_file,
                logger,
            )
            return

        if check_name == "null_check":
            self.__validate_simple_check(
                check,
                yml_file,
                logger,
            )
            return

        if check_name == "custom_check":
            self.__validate_custom_check(
                check,
                yml_file,
                logger,
            )

    # =========================================================
    # Range check
    # =========================================================

    def __validate_range_check(
        self,
        check: dict[str, object],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate range_check."""

        allowed_parameters: set[str] = {
            "name",
            "range",
            "threshold",
        }

        self.__validate_no_unknown_parameters(
            check,
            allowed_parameters,
            yml_file,
            logger,
        )

        if "range" not in check:
            logger.warning(
                "range is mandatory for range_check: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_RANGE_MISSING,
            )

        range_data = self.__as_string_mapping(
            check["range"],
            ValidationErrors.DATA_QUALITY_RANGE_INVALID,
        )

        allowed_range_parameters: set[str] = {
            "from_inc",
            "to_exc",
            "spark_timestamp_format",
        }

        self.__validate_no_unknown_parameters(
            range_data,
            allowed_range_parameters,
            yml_file,
            logger,
        )

        # -----------------------------------------------------
        # from_inc
        # -----------------------------------------------------

        if "from_inc" not in range_data:
            logger.warning(
                "range.from_inc is mandatory: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_RANGE_FROM_INC_MISSING,
            )

        from_inc_value = range_data["from_inc"]

        if not isinstance(from_inc_value, str):
            logger.warning(
                "range.from_inc must be a string: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_RANGE_FROM_INC_INVALID,
            )

        from_inc = from_inc_value.strip()

        if not from_inc:
            logger.warning(
                "range.from_inc cannot be blank: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_RANGE_FROM_INC_INVALID,
            )

        # -----------------------------------------------------
        # to_exc
        # -----------------------------------------------------

        if "to_exc" not in range_data:
            logger.warning(
                "range.to_exc is mandatory: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_RANGE_TO_EXC_MISSING,
            )

        to_exc_value = range_data["to_exc"]

        if not isinstance(to_exc_value, str):
            logger.warning(
                "range.to_exc must be a string: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_RANGE_TO_EXC_INVALID,
            )

        to_exc = to_exc_value.strip()

        if not to_exc:
            logger.warning(
                "range.to_exc cannot be blank: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_RANGE_TO_EXC_INVALID,
            )

        # -----------------------------------------------------
        # spark_timestamp_format
        # -----------------------------------------------------

        if self.__is_date_value(from_inc) or self.__is_date_value(to_exc):
            if "spark_timestamp_format" not in range_data:
                logger.warning(
                    "spark_timestamp_format is mandatory for date values: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.DATA_QUALITY_RANGE_TIMESTAMP_FORMAT_MISSING,
                )

            timestamp_format_value = range_data["spark_timestamp_format"]

            if not isinstance(timestamp_format_value, str):
                logger.warning(
                    "spark_timestamp_format must be a string: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.DATA_QUALITY_RANGE_TIMESTAMP_FORMAT_INVALID,
                )

            if not timestamp_format_value.strip():
                logger.warning(
                    "spark_timestamp_format cannot be blank: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.DATA_QUALITY_RANGE_TIMESTAMP_FORMAT_INVALID,
                )

        # -----------------------------------------------------
        # threshold
        # -----------------------------------------------------

        if "threshold" in check:
            self.__validate_threshold(
                check["threshold"],
                yml_file,
                logger,
            )

    # =========================================================
    # Simple checks
    # =========================================================

    def __validate_simple_check(
        self,
        check: dict[str, object],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate duplicate, not_blank and null checks."""

        allowed_parameters: set[str] = {
            "name",
            "threshold",
        }

        self.__validate_no_unknown_parameters(
            check,
            allowed_parameters,
            yml_file,
            logger,
        )

        if "threshold" in check:
            self.__validate_threshold(
                check["threshold"],
                yml_file,
                logger,
            )

    # =========================================================
    # Custom check
    # =========================================================

    def __validate_custom_check(
        self,
        check: dict[str, object],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate custom_check."""

        allowed_parameters: set[str] = {
            "name",
            "sql_query_full_dataset",
            "sql_query_fail_dataset",
            "threshold",
        }

        self.__validate_no_unknown_parameters(
            check,
            allowed_parameters,
            yml_file,
            logger,
        )

        # -----------------------------------------------------
        # sql_query_full_dataset
        # -----------------------------------------------------

        if "sql_query_full_dataset" not in check:
            logger.warning(
                "sql_query_full_dataset is mandatory for custom_check: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CUSTOM_SQL_QUERY_FULL_DATASET_MISSING,
            )

        sql_query_full_dataset_value = check["sql_query_full_dataset"]

        if not isinstance(sql_query_full_dataset_value, str):
            logger.warning(
                "sql_query_full_dataset must be a string: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CUSTOM_SQL_QUERY_FULL_DATASET_INVALID,
            )

        if not sql_query_full_dataset_value.strip():
            logger.warning(
                "sql_query_full_dataset cannot be blank: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CUSTOM_SQL_QUERY_FULL_DATASET_INVALID,
            )

        # -----------------------------------------------------
        # sql_query_fail_dataset
        # -----------------------------------------------------

        if "sql_query_fail_dataset" not in check:
            logger.warning(
                "sql_query_fail_dataset is mandatory for custom_check: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CUSTOM_SQL_QUERY_FAIL_DATASET_MISSING,
            )

        sql_query_fail_dataset_value = check["sql_query_fail_dataset"]

        if not isinstance(sql_query_fail_dataset_value, str):
            logger.warning(
                "sql_query_fail_dataset must be a string: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CUSTOM_SQL_QUERY_FAIL_DATASET_INVALID,
            )

        if not sql_query_fail_dataset_value.strip():
            logger.warning(
                "sql_query_fail_dataset cannot be blank: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CUSTOM_SQL_QUERY_FAIL_DATASET_INVALID,
            )

        # -----------------------------------------------------
        # threshold
        # -----------------------------------------------------

        if "threshold" in check:
            self.__validate_threshold(
                check["threshold"],
                yml_file,
                logger,
            )

    # =========================================================
    # Threshold
    # =========================================================

    def __validate_threshold(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate a threshold value."""

        if isinstance(value, bool):
            logger.warning(
                "threshold must be a number less than 1: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_THRESHOLD_INVALID,
            )

        if not isinstance(value, (int, float)):
            logger.warning(
                "threshold must be a number less than 1: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_THRESHOLD_INVALID,
            )

        threshold: float = float(value)

        if threshold >= 1:
            logger.warning(
                "threshold must be less than 1: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_THRESHOLD_OUT_OF_RANGE,
            )

        if threshold < 0:
            logger.warning(
                "threshold cannot be negative: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_THRESHOLD_OUT_OF_RANGE,
            )

    # =========================================================
    # Unknown parameters
    # =========================================================

    def __validate_no_unknown_parameters(
        self,
        values: dict[str, object],
        allowed_parameters: set[str],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Reject parameters that are not explicitly supported."""

        for parameter_name in values.keys():
            if parameter_name not in allowed_parameters:
                logger.warning(
                    "Unknown parameter '%s': %s",
                    parameter_name,
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.DATA_QUALITY_CHECK_PARAMETER_INVALID,
                )

    # =========================================================
    # Date detection
    # =========================================================

    @staticmethod
    def __is_date_value(
        value: str,
    ) -> bool:
        """Return whether a value represents a date or timestamp."""

        try:
            datetime.fromisoformat(value)
            return True
        except ValueError:
            pass

        try:
            date.fromisoformat(value)
            return True
        except ValueError:
            return False

    # =========================================================
    # YAML mapping conversion
    # =========================================================

    @staticmethod
    def __as_string_mapping(
        value: object,
        error_definition: ErrorDefinition,
    ) -> dict[str, object]:
        """Convert a YAML mapping into a string-keyed mapping."""

        if not isinstance(value, dict):
            raise ValidationError(error_definition)

        mapping = cast(dict[object, object], value)
        result: dict[str, object] = {}

        for key_value, item_value in mapping.items():
            if not isinstance(key_value, str):
                raise ValidationError(error_definition)

            result[key_value] = item_value

        return result
