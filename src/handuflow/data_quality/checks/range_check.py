from __future__ import annotations

from pyspark.sql import functions as F

from ..base import BaseDataQualityCheck
from ..dataclass import CheckResult
from ...platform.exceptions.errors.data_quality import DataQualityErrors


class RangeCheck(BaseDataQualityCheck):
    """Validate that the values in a specified column fall within a defined range."""

    def _validate(self) -> CheckResult:

        column = self.check_obj.column
        table_name = self.check_obj.table_path
        dataframe = self._generate_test_table_df()

        if column not in dataframe.columns:
            self._raise_data_quality_error(
                self._logger,
                DataQualityErrors.COLUMN_NOT_FOUND,
                check_identifier=self.check_obj.check_group_identifier,
                table_name=table_name,
                column=column,
            )

        check_range = self.check_range or {}
        spark_timestamp_format = self.check_obj.checks[0].spark_timestamp_format
        from_inc = check_range.get("from_inc", None)
        to_exc = check_range.get("to_exc", None)
        total_rows = dataframe.count()

        if spark_timestamp_format is not None:
            condition = (
                F.to_timestamp(F.col(column), spark_timestamp_format)
                >= F.to_timestamp(F.lit(from_inc), spark_timestamp_format)
            ) & (
                F.to_timestamp(F.col(column), spark_timestamp_format)
                < F.to_timestamp(F.lit(to_exc), spark_timestamp_format)
            )
            failed_rows = dataframe.filter(~condition).count()
        else:

            if from_inc is None or to_exc is None:
                self._raise_data_quality_error(
                    self._logger,
                    DataQualityErrors.INVALID_CHECK_CONFIGURATION,
                    check_identifier=self.check_obj.check_group_identifier,
                    message="Both 'from_inc' and 'to_exc' must be specified.",
                )

            if type(from_inc) is not type(to_exc):
                self._raise_data_quality_error(
                    self._logger,
                    DataQualityErrors.INVALID_CHECK_CONFIGURATION,
                    check_identifier=self.check_obj.check_group_identifier,
                    message=(
                        "'from_inc' and 'to_exc' must be of the same type. "
                        f"Received {type(from_inc).__name__} and {type(to_exc).__name__}."
                    ),
                )

            condition = (F.col(column) >= F.lit(from_inc)) & (
                F.col(column) < F.lit(to_exc)
            )
            failed_rows = dataframe.filter(~condition).count()
        return self._build_result(total_rows=total_rows, failed_rows=failed_rows)
