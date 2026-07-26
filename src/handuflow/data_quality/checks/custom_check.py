from __future__ import annotations

from ..base import BaseDataQualityCheck
from ..dataclass import CheckResult


class CustomCheck(BaseDataQualityCheck):
    """Validate that custom values in a column are within configured limits."""

    def validate(self) -> CheckResult:
        table_name = self.check_obj.table_path

        self._logger.info(
            "Running custom check '%s' on table '%s'",
            self.check_obj.check_identifier,
            table_name,
        )

        dataframe = self._generate_test_table_df_by_query()
        total_rows = dataframe.count()

        if total_rows == 0:
            return self._build_result(total_rows=0, failed_rows=0)

        return self._build_result(total_rows=total_rows, failed_rows=total_rows)
