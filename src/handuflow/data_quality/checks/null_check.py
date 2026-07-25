from __future__ import annotations

from pyspark.sql import functions as F

from ..base import BaseDataQualityCheck
from ..dataclass import CheckResult
from ...platform.exceptions.errors.data_quality import DataQualityErrors



class NullCheck(BaseDataQualityCheck):
    """Validate that null values in a column are within configured limits."""

    def validate(self) -> CheckResult:
        logger = self.context.logging.logger
        column = self.check_obj.column
        table_name = self.check_obj.table_path

        logger.info(f"Running null check on column {column} in table {table_name}")

        logger.info(
            "Running null check '%s' on column '%s' in table '%s' : PASSED (empty table)",
            self.check_obj.check_identifier,
            column,
            table_name,
        )

        dataframe = self._generate_test_table_df()

        if dataframe:
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
                    failed_rows=0
                )

            failed_rows = dataframe.filter(F.col(column).isNull()).count()


            return self._build_result(
                total_rows=total_rows,
                failed_rows=failed_rows
            )



        else:
            self._raise_data_quality_error(
                logger,
                DataQualityErrors.TABLE_NOT_FOUND,
                check_identifier=self.check_obj.check_identifier,
                table_name=table_name,
                column=column,
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
        passed_rows = total_rows - failed_rows
        pass_pct = (passed_rows / total_rows) * 100 if total_rows else 0.0
        fail_pct = (failed_rows / total_rows) * 100 if total_rows else 0.0
        threshold = self.check_obj.threshold if self.check_obj.threshold is not None else 0.0

        is_passed = False

        if fail_pct <= threshold:
            is_passed = True

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
