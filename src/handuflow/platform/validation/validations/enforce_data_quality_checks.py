"""Data quality checks validation for HanduFLOW."""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import cast

from ...configurator.dataclasses.context import ConfigurationContext
from ...exceptions.definition import ErrorDefinition
from ...exceptions.errors.validation import ValidationErrors
from ...storage import StoragePath
from ...storage.base import StorageProvider
from ..dataclasses import ValidationResult
from ._common import FeedConfigurationValidation, require_mapping

VALID_RUN_TYPES: frozenset[str] = frozenset(
    {
        "PRE_LOAD",
        "POST_LOAD",
    }
)

VALID_CHECK_NAMES: frozenset[str] = frozenset(
    {
        "range_check",
        "duplicate_check",
        "not_blank_check",
        "null_check",
        "custom_check",
    }
)

_SIMPLE_CHECKS: frozenset[str] = frozenset(
    {
        "duplicate_check",
        "not_blank_check",
        "null_check",
    }
)


class EnforceDataQualityChecks(FeedConfigurationValidation):
    """Validate data_quality_checks in HanduFLOW feed configuration files."""

    @property
    def name(self) -> str:
        return "enforce_data_quality_checks"

    @property
    def key(self) -> int:
        return 8

    def validate(
        self,
        configuration_context: ConfigurationContext,
    ) -> ValidationResult:
        """Validate data_quality_checks in all feed configuration YAML files."""

        return self._run_feed_configuration_validation(
            configuration_context,
            scope_label="data quality checks",
            success_message="Data quality checks are valid.",
            unexpected_error_message=(
                "Unexpected error during data quality checks validation."
            ),
            validate_file=self.__validate_file,
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

        root_data = require_mapping(
            self._load_yaml_document(
                provider,
                yml_file,
                logger,
            ),
            ValidationErrors.FEED_CONFIGURATION_INVALID_YML,
            require_string_keys=True,
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

        if not isinstance(data_quality_checks_value, list) or not data_quality_checks_value:
            logger.warning(
                "data_quality_checks must be a non-empty list: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECKS_INVALID,
            )

        check_group_identifiers: set[str] = set()

        for check_group_value in cast(list[object], data_quality_checks_value):
            check_group = require_mapping(
                check_group_value,
                ValidationErrors.DATA_QUALITY_CHECK_GROUP_INVALID,
                require_string_keys=True,
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

        check_group_identifier = self.__require_non_blank_string(
            check_group.get("check_group_identifier"),
            logger,
            yml_file,
            "check_group_identifier must be a string: %s",
            ValidationErrors.DATA_QUALITY_CHECK_GROUP_IDENTIFIER_INVALID,
            missing_error=ValidationErrors.DATA_QUALITY_CHECK_GROUP_IDENTIFIER_MISSING,
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

        self.__require_non_blank_string(
            check_group.get("description"),
            logger,
            yml_file,
            "description must be a string: %s",
            ValidationErrors.DATA_QUALITY_CHECK_DESCRIPTION_INVALID,
            missing_error=ValidationErrors.DATA_QUALITY_CHECK_DESCRIPTION_MISSING,
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

        self.__require_non_blank_string(
            check_group.get("column"),
            logger,
            yml_file,
            "column must be a string: %s",
            ValidationErrors.DATA_QUALITY_CHECK_COLUMN_INVALID,
            missing_error=ValidationErrors.DATA_QUALITY_CHECK_COLUMN_MISSING,
        )

        if "checks" not in check_group:
            logger.warning(
                "checks is missing: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECKS_LIST_MISSING,
            )

        checks_value = check_group["checks"]

        if not isinstance(checks_value, list) or not checks_value:
            logger.warning(
                "checks must be a non-empty list: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECKS_LIST_INVALID,
            )

        for check_value in cast(list[object], checks_value):
            check = require_mapping(
                check_value,
                ValidationErrors.DATA_QUALITY_CHECK_INVALID,
                require_string_keys=True,
            )

            self.__validate_check(
                check,
                yml_file,
                logger,
            )

    def __validate_dependency_datasets(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate optional dependency_datasets."""

        if value is None:
            return

        if isinstance(value, str):
            if not value.strip():
                return

            logger.warning(
                "dependency_datasets must be null, blank, or a list: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_DEPENDENCY_DATASETS_INVALID,
            )

        if not isinstance(value, list):
            logger.warning(
                "dependency_datasets must be null, blank, or a list: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_DEPENDENCY_DATASETS_INVALID,
            )

        if not value:
            return

        for dataset_value in cast(list[object], value):
            if not isinstance(dataset_value, str) or not dataset_value.strip():
                logger.warning(
                    "dependency_datasets cannot contain blank values: %s",
                    yml_file.uri,
                )

                self._raise_validation_error(
                    ValidationErrors.DATA_QUALITY_DEPENDENCY_DATASETS_INVALID,
                )

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

        if check_name in _SIMPLE_CHECKS:
            self.__validate_simple_check(
                check,
                yml_file,
                logger,
            )
            return

        self.__validate_custom_check(
            check,
            yml_file,
            logger,
        )

    def __validate_range_check(
        self,
        check: dict[str, object],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate range_check."""

        allowed_parameters = frozenset(
            {
                "name",
                "range",
                "threshold",
            }
        )

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

        range_data = require_mapping(
            check["range"],
            ValidationErrors.DATA_QUALITY_RANGE_INVALID,
            require_string_keys=True,
        )

        allowed_range_parameters = frozenset(
            {
                "from_inc",
                "to_exc",
                "spark_timestamp_format",
            }
        )

        self.__validate_no_unknown_parameters(
            range_data,
            allowed_range_parameters,
            yml_file,
            logger,
        )

        from_inc = self.__require_non_blank_string(
            range_data.get("from_inc"),
            logger,
            yml_file,
            "range.from_inc must be a string: %s",
            ValidationErrors.DATA_QUALITY_RANGE_FROM_INC_INVALID,
            missing_error=ValidationErrors.DATA_QUALITY_RANGE_FROM_INC_MISSING,
        )

        to_exc = self.__require_non_blank_string(
            range_data.get("to_exc"),
            logger,
            yml_file,
            "range.to_exc must be a string: %s",
            ValidationErrors.DATA_QUALITY_RANGE_TO_EXC_INVALID,
            missing_error=ValidationErrors.DATA_QUALITY_RANGE_TO_EXC_MISSING,
        )

        if self.__is_date_value(from_inc) or self.__is_date_value(to_exc):
            self.__require_non_blank_string(
                range_data.get("spark_timestamp_format"),
                logger,
                yml_file,
                "spark_timestamp_format must be a string: %s",
                ValidationErrors.DATA_QUALITY_RANGE_TIMESTAMP_FORMAT_INVALID,
                missing_error=ValidationErrors.DATA_QUALITY_RANGE_TIMESTAMP_FORMAT_MISSING,
            )

        if "threshold" in check:
            self.__validate_threshold(
                check["threshold"],
                yml_file,
                logger,
            )

    def __validate_simple_check(
        self,
        check: dict[str, object],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate duplicate, not_blank and null checks."""

        allowed_parameters = frozenset(
            {
                "name",
                "threshold",
            }
        )

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

    def __validate_custom_check(
        self,
        check: dict[str, object],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate custom_check."""

        allowed_parameters = frozenset(
            {
                "name",
                "sql_query_full_dataset",
                "sql_query_fail_dataset",
                "threshold",
            }
        )

        self.__validate_no_unknown_parameters(
            check,
            allowed_parameters,
            yml_file,
            logger,
        )

        self.__require_non_blank_string(
            check.get("sql_query_full_dataset"),
            logger,
            yml_file,
            "sql_query_full_dataset must be a string: %s",
            ValidationErrors.DATA_QUALITY_CUSTOM_SQL_QUERY_FULL_DATASET_INVALID,
            missing_error=ValidationErrors.DATA_QUALITY_CUSTOM_SQL_QUERY_FULL_DATASET_MISSING,
        )

        self.__require_non_blank_string(
            check.get("sql_query_fail_dataset"),
            logger,
            yml_file,
            "sql_query_fail_dataset must be a string: %s",
            ValidationErrors.DATA_QUALITY_CUSTOM_SQL_QUERY_FAIL_DATASET_INVALID,
            missing_error=ValidationErrors.DATA_QUALITY_CUSTOM_SQL_QUERY_FAIL_DATASET_MISSING,
        )

        if "threshold" in check:
            self.__validate_threshold(
                check["threshold"],
                yml_file,
                logger,
            )

    def __validate_threshold(
        self,
        value: object,
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Validate a threshold value."""

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            logger.warning(
                "threshold must be a number less than 1: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_THRESHOLD_INVALID,
            )

        threshold = float(value)

        if threshold < 0 or threshold >= 1:
            logger.warning(
                "threshold must be between 0 and 1: %s",
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_THRESHOLD_OUT_OF_RANGE,
            )

    def __validate_no_unknown_parameters(
        self,
        values: dict[str, object],
        allowed_parameters: frozenset[str],
        yml_file: StoragePath,
        logger: logging.Logger,
    ) -> None:
        """Reject parameters that are not explicitly supported."""

        for parameter_name in values.keys() - allowed_parameters:
            logger.warning(
                "Unknown parameter '%s': %s",
                parameter_name,
                yml_file.uri,
            )

            self._raise_validation_error(
                ValidationErrors.DATA_QUALITY_CHECK_PARAMETER_INVALID,
            )

    def __require_non_blank_string(
        self,
        value: object,
        logger: logging.Logger,
        yml_file: StoragePath,
        invalid_message: str,
        invalid_error: ErrorDefinition,
        *,
        missing_error: ErrorDefinition,
    ) -> str:
        """Validate a required non-blank string field."""

        if value is None:
            logger.warning(
                invalid_message,
                yml_file.uri,
            )

            self._raise_validation_error(missing_error)

        if not isinstance(value, str):
            logger.warning(
                invalid_message,
                yml_file.uri,
            )

            self._raise_validation_error(invalid_error)

        stripped = value.strip()

        if not stripped:
            logger.warning(
                invalid_message,
                yml_file.uri,
            )

            self._raise_validation_error(invalid_error)

        return stripped

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
