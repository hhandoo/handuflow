from __future__ import annotations

from ..base import BaseDataQualityCheck
from ..dataclass import CheckResult
from ...platform.exceptions.errors.data_quality import DataQualityErrors



class CustomCheck(BaseDataQualityCheck):
    """Validate that custom values in a column are within configured limits."""

    def validate(self) -> CheckResult:
        logger = self.context.logging.logger
        table_name = self.check_obj.table_path
        logger.info(f"Running custom check '{self.check_obj.check_identifier}' on table '{table_name}'.")

        dataframe = self._generate_test_table_df_by_query()

        if dataframe:
            total_rows = dataframe.count()

            if total_rows > 0:
                return self._build_result(
                    total_rows=total_rows,
                    failed_rows=total_rows
                )
            else:
                return self._build_result(
                    total_rows=0,
                    failed_rows=0
                )
        else:
            self._raise_data_quality_error(
                logger,
                DataQualityErrors.TABLE_NOT_FOUND,
                check_identifier=self.check_obj.check_identifier,
                table_name=table_name
            )

            return self._build_result(
                total_rows=0,
                failed_rows=0
            )



    def _build_result(
        self,
        total_rows: int,
        failed_rows: int
    ) -> CheckResult:
        pass_pct = ((total_rows - failed_rows) / total_rows) * 100 if total_rows else 0.0
        fail_pct = (failed_rows / total_rows) * 100 if total_rows else 0.0
        threshold = self.check_obj.threshold if self.check_obj.threshold is not None else 0.0

        is_passed = False

        if fail_pct <= threshold:
            is_passed = True


        return CheckResult(
            unique_check_name=self.check_obj.check_identifier,
            table_name=self.check_obj.table_path,
            total_rows=total_rows,
            passed_rows=total_rows - failed_rows,
            failed_rows=failed_rows,
            pass_pct=pass_pct,
            fail_pct=fail_pct,
            threshold=threshold,
            is_passed=is_passed,
        )
