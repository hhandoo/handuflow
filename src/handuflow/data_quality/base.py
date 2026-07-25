from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from pyspark.sql import DataFrame

from ..platform.configurator.dataclasses.context import ConfigurationContext
from ..platform.exceptions.base import HanduflowError
from ..platform.exceptions.domains.data_quality import DataQualityError
from ..platform.exceptions.errors.data_quality import DataQualityErrors
from .dataclass import CheckObj
from .dataclass.result import CheckResult


class BaseDataQualityCheck(ABC):

    def __init__(self, check_obj: CheckObj, context: ConfigurationContext):
        self.check_obj = check_obj
        self.context = context

    @abstractmethod
    def validate(self) -> CheckResult:
        pass

    def _generate_test_table_df(self) -> DataFrame | None:
        spark = self.context.spark_config.spark
        logger = self.context.logging.logger

        table_names = [
            getattr(self.check_obj, "full_table_path", None),
            getattr(self.check_obj, "table_path", None),
        ]
        resolved_table_names = list(dict.fromkeys(filter(None, table_names)))


        for table in resolved_table_names:
            if spark.catalog.tableExists(table):
                return spark.table(table)
        self._raise_data_quality_error(
            logger,
            DataQualityErrors.TABLE_NOT_FOUND,
            table_names=resolved_table_names,
            check_identifier=self.check_obj.check_identifier,
        )

        return None


    def _generate_test_table_df_by_query(self) -> DataFrame | None:
        spark = self.context.spark_config.spark
        logger = self.context.logging.logger

        try:
            return spark.sql(self.check_obj.sql_query)
        except Exception as e:
            self._raise_data_quality_error(
                logger,
                DataQualityErrors.TABLE_NOT_FOUND,
                cause=e,
                check_identifier=self.check_obj.check_identifier,
            )

            return None

    @staticmethod
    def _raise_data_quality_error(
        logger: logging.Logger,
        error_definition,
        *,
        cause: Exception | None = None,
        **context: Any,
    ) -> None:
        error = DataQualityError(error_definition, cause=cause, **context)
        logger.error("[%s] %s", error.code, error.message)
        for key, value in context.items():
            logger.error("  %s: %s", key, value)
        if cause:
            logger.error("  cause: %s", cause)
        raise error

    def _handle_unexpected_error(self, exc: Exception) -> None:
        if isinstance(exc, HanduflowError):
            raise exc

        self._raise_data_quality_error(
            self.context.logging.logger,
            DataQualityErrors.DATA_QUALITY_UNKNOWN,
            check_identifier=self.check_obj.check_identifier,
            cause=exc,
        )
