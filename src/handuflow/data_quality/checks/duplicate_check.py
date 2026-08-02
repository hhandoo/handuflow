from __future__ import annotations

from pyspark.sql import functions as F

from ..base import BaseDataQualityCheck
from ..dataclass import CheckResult
from ...platform.exceptions.errors.data_quality import DataQualityErrors


class DuplicateCheck(BaseDataQualityCheck):
    """Validate that there are no duplicate values in the specified column."""

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

        total_rows = dataframe.count()

        duplicate_values = (
            dataframe.groupBy(column).count().filter(F.col("count") > 1).select(column)
        )

        failed_rows = dataframe.join(
            duplicate_values,
            on=column,
            how="inner",
        ).count()

        return self._build_result(
            total_rows=total_rows,
            failed_rows=failed_rows,
        )
