from handuflow.data_quality.dataclass.result import CheckResult
from handuflow.platform.configurator.dataclasses.context import ConfigurationContext


def test_duplicate_check(
    configuration_context: ConfigurationContext, results: list[CheckResult]
) -> None:
    """
    Verify that the duplicate check passes when the target column
    contains no null values.
    """
    is_passed_arr: list[bool] = []
    for res in results:
        if res.table_name == "`demo`.`employee4`":
            if (
                res.check_name == "duplicate_check"
                and res.passed_rows == 7
                and res.failed_rows == 2
                and not res.is_passed
            ):
                is_passed_arr.append(True)
            else:
                is_passed_arr.append(False)

        elif res.table_name == "`demo`.`employee5`":
            if (
                res.check_name == "duplicate_check"
                and res.passed_rows == 9
                and res.failed_rows == 0
                and res.is_passed
            ):
                is_passed_arr.append(True)
            else:
                is_passed_arr.append(False)

        elif res.table_name == "`demo`.`employee6`":
            if (
                res.check_name == "duplicate_check"
                and res.passed_rows == 8
                and res.failed_rows == 2
                and not res.is_passed
            ):
                is_passed_arr.append(True)
            else:
                is_passed_arr.append(False)

        elif res.table_name == "`demo`.`employee7`":
            if (
                res.check_name == "duplicate_check"
                and res.passed_rows == 10
                and res.failed_rows == 0
                and res.is_passed
            ):
                is_passed_arr.append(True)
            else:
                is_passed_arr.append(False)

    configuration_context.logging.logger.info(f"Check Arr: {is_passed_arr}")
    assert len(is_passed_arr) == 4
    assert all(is_passed_arr)
