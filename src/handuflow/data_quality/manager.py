import yaml

from .dataclass import CheckDC, CheckObj, CheckResult
from ..platform.configurator.dataclasses.context import ConfigurationContext
from .checks import *

CHECK_REGISTRY = {
    "custom_check": CustomCheck,
    "null_check": NullCheck,
    "not_blank_check": NotBlankCheck,
}

class DataQualityManager:

    def __init__(self, config_context : ConfigurationContext):
        self.config_context = config_context
        self.list_of_feed_ymls = config_context.list_of_feed_ymls


    def __load_checks(self) -> list:
        data_quality_manifest = []

        for current_feed in self.list_of_feed_ymls:
            with open(current_feed.uri, encoding="utf-8") as feed_file:
                config = yaml.safe_load(feed_file)

            if not isinstance(config, dict):
                continue

            data_quality_checks = config.get("data_quality_checks") or []
            if not data_quality_checks:
                continue

            source = config.get("source")
            feed_meta = config.get("feed_meta")
            if not isinstance(source, dict) or not isinstance(feed_meta, dict):
                continue

            source_type = source.get("type")
            source_schema = source.get("schema")
            source_table = source.get("table")
            feed_identifier = feed_meta.get("unique_identifier")
            if (
                not isinstance(source_type, str)
                or not isinstance(source_schema, str)
                or not isinstance(source_table, str)
                or not isinstance(feed_identifier, str)
                or not source_type
                or not source_schema
                or not source_table
                or not feed_identifier
            ):
                continue

            full_table_path = f"`{source_type}`.`{source_schema}`.`{source_table}`"
            table_path = f"`{source_schema}`.`{source_table}`"
            parsed_data_quality_checks: list[CheckObj] = []

            for dq_check in data_quality_checks:
                if not isinstance(dq_check, dict):
                    continue

                check_identifier = dq_check.get("check_identifier")
                run_type = dq_check.get("run_type")
                check_type = dq_check.get("check_type")
                if (
                    not isinstance(check_identifier, str)
                    or not isinstance(run_type, str)
                    or not isinstance(check_type, str)
                    or not check_identifier
                    or not run_type
                    or not check_type
                ):
                    continue

                checklist: list[CheckDC] = []
                for m_check in dq_check.get("checks") or []:
                    if not isinstance(m_check, dict):
                        continue

                    check_name = m_check.get("name")
                    if not isinstance(check_name, str) or not check_name:
                        continue

                    check_range = None
                    m_range = m_check.get("range")
                    if (
                        isinstance(m_range, list)
                        and len(m_range) >= 2
                        and isinstance(m_range[0], dict)
                        and isinstance(m_range[1], dict)
                    ):
                        range_start = m_range[0].get("from_inc")
                        range_end = m_range[1].get("to_exc")
                        if isinstance(range_start, int) and isinstance(range_end, int):
                            check_range = range(range_start, range_end)

                    checklist.append(CheckDC(name=check_name, check_range=check_range))

                raw_dependencies = dq_check.get("dependency_datasets")
                dependency_datasets: list[str] = []
                if isinstance(raw_dependencies, list):
                    dependency_datasets = [
                        dataset
                        for dataset in raw_dependencies
                        if isinstance(dataset, str)
                    ]

                raw_column = dq_check.get("column")
                column = raw_column if isinstance(raw_column, str) else ""

                raw_threshold = dq_check.get("threshold")
                threshold: float | None
                if isinstance(raw_threshold, (int, float)):
                    threshold = float(raw_threshold)
                else:
                    threshold = None

                raw_sql_query = dq_check.get("sql_query")
                sql_query = raw_sql_query if isinstance(raw_sql_query, str) else None

                parsed_data_quality_checks.append(
                    CheckObj(
                        full_table_path=full_table_path,
                        table_path=table_path,
                        check_identifier=check_identifier,
                        run_type=run_type,
                        check_type=check_type,
                        dependency_datasets=dependency_datasets,
                        column=column,
                        checks=checklist,
                        threshold=threshold,
                        sql_query=sql_query,
                    )
                )

            if parsed_data_quality_checks:
                data_quality_manifest.append(
                    {
                        "full_file_path": current_feed.uri,
                        "feed_identifier": feed_identifier,
                        "parsed_data_quality_checks": parsed_data_quality_checks,
                    }
                )
        return data_quality_manifest



    def run(self, run_type: str = 'PRE_LOAD') -> list[CheckResult]:
        data_quality_list_parsed = self.__load_checks()
        results = []

        for current_feed__checkObj in data_quality_list_parsed:
            for checks_obj in current_feed__checkObj['parsed_data_quality_checks']:
                if checks_obj.run_type == run_type:
                    self.config_context.logging.logger.info(f"Running check : [ {checks_obj.check_identifier} ]")
                    self.config_context.logging.logger.info(checks_obj)
                    self.config_context.logging.logger.info(f"Dependency Datasets Specified: {checks_obj.dependency_datasets}, ({len(checks_obj.dependency_datasets)})")


                    dep_ds_not_exist = False
                    if len(checks_obj.dependency_datasets) != 0:

                        for mds in checks_obj.dependency_datasets:
                            if not self.config_context.spark_config.spark.catalog.tableExists(mds):
                                dep_ds_not_exist = True


                    checks_to_be_performed = checks_obj.checks

                    for current_check in checks_to_be_performed:
                        check_class = CHECK_REGISTRY[current_check.name](checks_obj, self.config_context)

                        res = check_class.validate()

                        print(res)




        return results

