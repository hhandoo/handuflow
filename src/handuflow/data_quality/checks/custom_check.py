from __future__ import annotations

from ..base import BaseDataQualityCheck
from ..dataclass import CheckResult


class CustomCheck(BaseDataQualityCheck):
    """Validate that custom values in a column are within configured limits."""

    def _validate(self) -> CheckResult:
        p_dataframe = self._generate_positive_test_table_df_by_query()
        n_dataframe = self._generate_negative_test_table_df_by_query()
        total_rows = p_dataframe.count()
        failed_rows = n_dataframe.count()
        if total_rows == 0:
            return self._build_result(total_rows=0, failed_rows=0)
        return self._build_result(total_rows=total_rows, failed_rows=failed_rows)
