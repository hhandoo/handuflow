from __future__ import annotations

from pyspark.sql import functions as F

from ..base import BaseDataQualityCheck
from ..dataclass import CheckResult
from ...platform.exceptions.errors.data_quality import DataQualityErrors

NULL_CHECK_NAMES = {"null", "null_check"}


class NullCheck(BaseDataQualityCheck):
    """Validate that null values in a column are within configured limits."""

    def validate(self) -> CheckResult:
        logger = self.context.logging.logger
        column = self.check_obj.column
        table_name = self.check_obj.table_path
        null_check_config = self._get_null_check_config()

        try:
            return self._run_null_check(
                logger,
                column,
                table_name,
                null_check_config,
            )
        except Exception as exc:
            self._handle_unexpected_error(exc)

    def _run_null_check(
        self,
        logger,
        column: str,
        table_name: str,
        null_check_config,
    ) -> CheckResult:
        logger.info(
            "Running null check '%s' on column '%s' in table '%s'",
            self.check_obj.check_identifier,
            column,
            table_name,
        )

        dataframe = self._generate_test_table_df()

        if column not in dataframe.columns:
            self._raise_data_quality_error(
                logger,
                DataQualityErrors.COLUMN_NOT_FOUND,
                check_identifier=self.check_obj.check_identifier,
                table_name=table_name,
                column=column,
            )

        total_rows = dataframe.count()

        if total_rows == 0:
            logger.info(
                "Null check '%s' on column '%s' in table '%s' : PASSED (empty table)",
                self.check_obj.check_identifier,
                column,
                table_name,
            )
            return self._build_result(
                total_rows=0,
                failed_rows=0,
                is_passed=True,
            )

        failed_rows = dataframe.filter(F.col(column).isNull()).count()
        pass_pct = ((total_rows - failed_rows) / total_rows) * 100
        fail_pct = (failed_rows / total_rows) * 100
        is_passed = self._is_within_limits(failed_rows, fail_pct, null_check_config)

        if is_passed:
            logger.info(
                "Null check '%s' on column '%s' in table '%s' : PASSED "
                "(%d failed row(s), %.2f%% fail rate)",
                self.check_obj.check_identifier,
                column,
                table_name,
                failed_rows,
                fail_pct,
            )
        else:
            logger.error(
                "Null check '%s' on column '%s' in table '%s' : FAILED "
                "(%d failed row(s), %.2f%% fail rate)",
                self.check_obj.check_identifier,
                column,
                table_name,
                failed_rows,
                fail_pct,
            )

        return self._build_result(
            total_rows=total_rows,
            failed_rows=failed_rows,
            is_passed=is_passed,
        )

    def _get_null_check_config(self):
        for check in self.check_obj.checks:
            if check.name in NULL_CHECK_NAMES:
                return check
        return None

    def _is_within_limits(
        self,
        failed_rows: int,
        fail_pct: float,
        null_check_config,
    ) -> bool:
        threshold = self.check_obj.threshold
        if threshold is not None:
            return (fail_pct / 100) <= threshold

        if null_check_config and null_check_config.check_range is not None:
            return failed_rows in null_check_config.check_range

        return failed_rows == 0

    def _build_result(
        self,
        *,
        total_rows: int,
        failed_rows: int,
        is_passed: bool,
    ) -> CheckResult:
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
            is_passed=is_passed,
        )
