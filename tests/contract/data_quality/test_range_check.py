from handuflow.data_quality.dataclass.result import CheckResult
from handuflow.platform.configurator.dataclasses.context import ConfigurationContext


def test_range_check(
    configuration_context: ConfigurationContext,
    results: list[CheckResult],
) -> None:
    """
    Verify that the null check produces the expected results.
    """

    is_passed_arr: list[bool] = []

    for res in results:

        if res.table_name == "`demo`.`employee12`":

            if res.column == "event_ts":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 10
                    and res.failed_rows == 0
                    and res.is_passed
                )

            if res.column == "age":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 10
                    and res.failed_rows == 0
                    and res.is_passed
                )

            if res.column == "name":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 10
                    and res.failed_rows == 0
                    and res.is_passed
                )

            if res.column == "salary":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 10
                    and res.failed_rows == 0
                    and res.is_passed
                )

        if res.table_name == "`demo`.`employee13`":

            if res.column == "event_ts":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 9
                    and res.failed_rows == 1
                    and not res.is_passed
                )

            if res.column == "age":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 9
                    and res.failed_rows == 1
                    and not res.is_passed
                )

            if res.column == "name":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 9
                    and res.failed_rows == 1
                    and not res.is_passed
                )

            if res.column == "salary":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 9
                    and res.failed_rows == 1
                    and not res.is_passed
                )

        if res.table_name == "`demo`.`employee14`":

            if res.column == "event_ts":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 8
                    and res.failed_rows == 2
                    and not res.is_passed
                )

            if res.column == "age":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 8
                    and res.failed_rows == 2
                    and not res.is_passed
                )

            if res.column == "name":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 8
                    and res.failed_rows == 2
                    and not res.is_passed
                )

            if res.column == "salary":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 8
                    and res.failed_rows == 2
                    and not res.is_passed
                )

        if res.table_name == "`demo`.`employee15`":

            if res.column == "event_ts":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 9
                    and res.failed_rows == 1
                    and res.is_passed
                )

            if res.column == "age":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 9
                    and res.failed_rows == 1
                    and res.is_passed
                )

            if res.column == "name":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 9
                    and res.failed_rows == 1
                    and res.is_passed
                )

            if res.column == "salary":
                print(res)
                is_passed_arr.append(
                    res.check_name == "range_check"
                    and res.passed_rows == 9
                    and res.failed_rows == 1
                    and res.is_passed
                )

    configuration_context.logging.logger.info(
        "Check Arr: %s",
        is_passed_arr,
    )

    assert len(is_passed_arr) == 16
    assert all(is_passed_arr)
