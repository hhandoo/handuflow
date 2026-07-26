from __future__ import annotations

from pyspark.sql import functions as F

from ..base import BaseDataQualityCheck
from ..dataclass import CheckResult
from ...platform.exceptions.errors.data_quality import DataQualityErrors


class NullCheck(BaseDataQualityCheck):
    """Validate that null values in a column are within configured limits."""

    def validate(self) -> CheckResult:
        column = self.check_obj.column
        table_name = self.check_obj.table_path

        self._logger.info(
            "Running null check '%s' on column '%s' in table '%s'",
            self.check_obj.check_identifier,
            column,
            table_name,
        )
        dataframe = self._generate_test_table_df()
        if column not in dataframe.columns:
            self._raise_data_quality_error(
                self._logger,
                DataQualityErrors.COLUMN_NOT_FOUND,
                check_identifier=self.check_obj.check_identifier,
                table_name=table_name,
                column=column,
            )

        total_rows = dataframe.count()
        failed_rows = dataframe.filter(F.col(column).isNull()).count()
        if total_rows == 0:
            self._logger.info(
                "Null check '%s' on column '%s' in table '%s' : PASSED (empty table)",
                self.check_obj.check_identifier,
                column,
                table_name,
            )

        return self._build_result(total_rows=total_rows, failed_rows=failed_rows)
