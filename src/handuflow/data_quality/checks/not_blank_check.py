from __future__ import annotations

from pyspark.sql import functions as F

from ..base import BaseDataQualityCheck
from ..dataclass import CheckResult
from ...platform.exceptions.errors.data_quality import DataQualityErrors


class NotBlankCheck(BaseDataQualityCheck):
    """Validate that blank values in a column are within configured limits."""

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
        failed_rows = dataframe.filter(
            F.trim(F.col(column)) == ""
        ).count()
        return self._build_result(total_rows=total_rows, failed_rows=failed_rows)
