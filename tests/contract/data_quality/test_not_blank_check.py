from handuflow.data_quality.dataclass.result import CheckResult
from handuflow.platform.configurator.dataclasses.context import ConfigurationContext


def test_not_blank_check(
    configuration_context: ConfigurationContext,
    results: list[CheckResult],
) -> None:
    """
    Verify that the not blank check produces the expected results.
    """

    is_passed_arr: list[bool] = []

    for res in results:

        if res.table_name == "`demo`.`employee8`":
            is_passed_arr.append(
                res.check_name == "not_blank_check"
                and res.passed_rows == 10
                and res.failed_rows == 0
                and res.is_passed
            )

        elif res.table_name == "`demo`.`employee9`":
            is_passed_arr.append(
                res.check_name == "not_blank_check"
                and res.passed_rows == 9
                and res.failed_rows == 1
                and not res.is_passed
            )

        elif res.table_name == "`demo`.`employee10`":
            is_passed_arr.append(
                res.check_name == "not_blank_check"
                and res.passed_rows == 9
                and res.failed_rows == 1
                and res.is_passed
                and res.threshold_pct == 10.0
            )

        elif res.table_name == "`demo`.`employee11`":
            is_passed_arr.append(
                res.check_name == "not_blank_check"
                and res.passed_rows == 8
                and res.failed_rows == 2
                and not res.is_passed
                and res.threshold_pct == 10.0
            )

    configuration_context.logging.logger.info(
        "Check Arr: %s",
        is_passed_arr,
    )

    assert len(is_passed_arr) == 4
    assert all(is_passed_arr)
