from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, NoReturn

from pyspark.sql import DataFrame, SparkSession
from ..platform.configurator.dataclasses.context import ConfigurationContext
from ..platform.exceptions.base import HanduflowError
from ..platform.exceptions.definition import ErrorDefinition
from ..platform.exceptions.domains.data_quality import DataQualityError
from ..platform.exceptions.errors.data_quality import DataQualityErrors
from .dataclass import CheckObj
from .dataclass.result import CheckResult


class BaseDataQualityCheck(ABC):
    """Shared behavior for data quality check implementations."""

    def __init__(self, check_obj: CheckObj, context: ConfigurationContext) -> None:
        self.check_obj = check_obj
        self.context = context

    @property
    def _logger(self) -> logging.Logger:
        return self.context.logging.logger

    @property
    def _spark(self) -> SparkSession:
        return self.context.spark_config.spark

    @abstractmethod
    def validate(self) -> CheckResult:
        """Run the check and return a structured result."""

    @staticmethod
    def _parse_table_identifiers(table_reference: str) -> list[str]:
        reference = table_reference.strip()
        if not reference:
            return []

        if "`" in reference:
            return [
                part.strip().strip("`")
                for part in reference.split(".")
                if part.strip().strip("`")
            ]

        return [part.strip() for part in reference.split(".") if part.strip()]

    @staticmethod
    def _format_table_reference(parts: list[str], *, quoted: bool) -> str:
        if quoted:
            return ".".join(f"`{part}`" for part in parts)
        return ".".join(parts)

    def _resolve_table_names(self) -> list[str]:
        environment = self.context.default.environment.strip().lower()
        candidates: list[str] = []
        seen: set[str] = set()

        def add(name: str) -> None:
            if name and name not in seen:
                seen.add(name)
                candidates.append(name)

        full_parts = self._parse_table_identifiers(self.check_obj.full_table_path)
        table_parts = self._parse_table_identifiers(self.check_obj.table_path)
        schema_table_parts = table_parts[-2:] if len(table_parts) >= 2 else []
        catalog_schema_table_parts = full_parts if len(full_parts) == 3 else []

        if environment == "local":
            if schema_table_parts:
                add(self._format_table_reference(schema_table_parts, quoted=False))
                add(self._format_table_reference(schema_table_parts, quoted=True))
            if catalog_schema_table_parts:
                add(self._format_table_reference(catalog_schema_table_parts[-2:], quoted=False))
                add(self._format_table_reference(catalog_schema_table_parts[-2:], quoted=True))
            if catalog_schema_table_parts:
                add(self._format_table_reference(catalog_schema_table_parts, quoted=False))
                add(self._format_table_reference(catalog_schema_table_parts, quoted=True))
        else:
            if catalog_schema_table_parts:
                add(self._format_table_reference(catalog_schema_table_parts, quoted=True))
                add(self._format_table_reference(catalog_schema_table_parts, quoted=False))
            if schema_table_parts:
                add(self._format_table_reference(schema_table_parts, quoted=True))
                add(self._format_table_reference(schema_table_parts, quoted=False))

        add(self.check_obj.full_table_path)
        add(self.check_obj.table_path)

        return candidates

    def _generate_test_table_df(self) -> DataFrame:
        table_names = self._resolve_table_names()
        for table_name in table_names:
            if self._spark.catalog.tableExists(table_name):
                self._logger.debug(
                    "Resolved table '%s' for check '%s' in '%s' environment.",
                    table_name,
                    self.check_obj.check_identifier,
                    self.context.default.environment,
                )
                return self._spark.table(table_name)

        self._raise_data_quality_error(
            self._logger,
            DataQualityErrors.TABLE_NOT_FOUND,
            table_names=table_names,
            check_identifier=self.check_obj.check_identifier,
            environment=self.context.default.environment,
        )

    def _generate_test_table_df_by_query(self) -> DataFrame:
        sql_query = self.check_obj.sql_query
        if not isinstance(sql_query, str) or not sql_query:
            self._raise_data_quality_error(
                self._logger,
                DataQualityErrors.SQL_QUERY_ERROR,
                check_identifier=self.check_obj.check_identifier,
            )

        try:
            dfff = self._spark.sql(sql_query) # pyright: ignore[reportUnknownMemberType]
            return dfff
        except Exception as exc:
            self._raise_data_quality_error(
                self._logger,
                DataQualityErrors.SQL_QUERY_ERROR,
                cause=exc,
                check_identifier=self.check_obj.check_identifier,
            )

    def _build_result(self, *, total_rows: int, failed_rows: int) -> CheckResult:
        passed_rows = total_rows - failed_rows
        pass_pct = (passed_rows / total_rows) * 100 if total_rows else 0.0
        fail_pct = (failed_rows / total_rows) * 100 if total_rows else 0.0
        threshold = self.check_obj.threshold if self.check_obj.threshold is not None else 0.0

        return CheckResult(
            unique_check_name=self.check_obj.check_identifier,
            table_name=self.check_obj.table_path,
            total_rows=total_rows,
            passed_rows=passed_rows,
            failed_rows=failed_rows,
            pass_pct=pass_pct,
            fail_pct=fail_pct,
            threshold=threshold,
            is_passed=fail_pct <= threshold,
        )

    @staticmethod
    def _raise_data_quality_error(
        logger: logging.Logger,
        error_definition: ErrorDefinition,
        *,
        cause: Exception | None = None,
        **context: Any,
    ) -> NoReturn:
        error = DataQualityError(error_definition, cause=cause, **context)
        logger.error("[%s] %s", error.code, error.message)
        for key, value in context.items():
            logger.error("  %s: %s", key, value)
        if cause:
            logger.error("  cause: %s", cause)
        raise error

    def handle_unexpected_error(self, exc: Exception) -> NoReturn:
        if isinstance(exc, HanduflowError):
            raise exc

        self._raise_data_quality_error(
            self._logger,
            DataQualityErrors.DATA_QUALITY_UNKNOWN,
            check_identifier=self.check_obj.check_identifier,
            cause=exc,
        )
