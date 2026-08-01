from handuflow.data_quality.manager import DataQualityManager
from handuflow.data_quality.dataclass.result import CheckResult
from handuflow.platform.configurator.dataclasses.context import ConfigurationContext


def test_null_check_passes(
    configuration_context: ConfigurationContext,
) -> None:
    """
    Verify that the null check passes when the target column
    contains no null values.
    """
    manager = DataQualityManager(configuration_context)
    results: list[CheckResult] = manager.run("PRE_LOAD")

    is_passed_arr: list[bool] = []
    for res in results:
        if (
            res.table_name == "`demo`.`employee`"
            and res.check_name == "null_check"
            and res.passed_rows == 8
            and res.failed_rows == 1
            and res.is_passed == False
        ):
            is_passed_arr.append(True)
        elif (
            res.table_name == "`demo`.`employee1`"
            and res.check_name == "null_check"
            and res.passed_rows == 9
            and res.failed_rows == 0
            and res.is_passed == True
        ):
            is_passed_arr.append(True)
        else:
            is_passed_arr.append(False)

    configuration_context.logging.logger.info(
        f"Null Check Results: {results}, Arr: {is_passed_arr}"
    )
    assert all(is_passed_arr)
