import yaml

from typing import Type, cast, Any
from .dataclass import  CheckDC, CheckObj, CheckResult
from ..platform.configurator.dataclasses.context import ConfigurationContext
from .checks import *
from .base import BaseDataQualityCheck

CHECK_REGISTRY: dict[str, Type[BaseDataQualityCheck]] = {
    "custom_check": CustomCheck,
    "null_check": NullCheck,
    "not_blank_check": NotBlankCheck,
    "duplicate_check": DuplicateCheck,
}
class DataQualityManager:
    def __init__(self, config_context : ConfigurationContext):
        self.config_context = config_context
        self.list_of_feed_ymls = config_context.list_of_feed_ymls
    def __load_checks(self) -> list[CheckObj]:
        parsed_data_quality_checks: list[CheckObj] = []
        for current_feed in self.list_of_feed_ymls:
            with open(current_feed.uri, encoding="utf-8") as feed_file:
                config = cast(dict[str, Any] | None, yaml.safe_load(feed_file))
            if not isinstance(config, dict):
                continue
            data_quality_checks_raw = config.get("data_quality_checks")
            source_raw = config.get("source")
            feed_meta_raw = config.get("feed_meta")
            if not isinstance(source_raw, dict) or not isinstance(feed_meta_raw, dict) or not isinstance(data_quality_checks_raw, list):
                continue
            source = cast(dict[str, Any], source_raw)
            feed_meta = cast(dict[str, Any], feed_meta_raw)
            data_quality_checks = cast(dict[str, Any], data_quality_checks_raw)
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
            for dq_check in data_quality_checks:
                dq_check = cast(dict[str, Any], dq_check)
                checklist: list[CheckDC] = []

                for m_check in dq_check.get("checks", []):
                    checklist.append(
                        CheckDC(
                            name=m_check.get("name", ""), 
                            check_range=m_check.get("check_range", {})
                        )
                    )
                parsed_data_quality_checks.append(
                    CheckObj(
                        full_file_path=current_feed.uri,
                        feed_identifier=feed_identifier,
                        full_table_path=full_table_path,
                        table_path=table_path,
                        check_group_identifier=dq_check.get("check_group_identifier", ""),
                        run_type=dq_check.get("run_type", ""),
                        dependency_datasets= [] if dq_check.get("dependency_datasets", []) is None else dq_check.get("dependency_datasets", []),
                        column=dq_check.get("column", ""),
                        checks=checklist,
                        threshold=dq_check.get("threshold", ""),
                        sql_query=dq_check.get("sql_query", ""),
                    )
                )
        return parsed_data_quality_checks
    
    def run(self, run_type: str = "PRE_LOAD") -> list[CheckResult]:
        data_quality_manifest = self.__load_checks()
        results: list[CheckResult] = []
        for feed in data_quality_manifest:
            if feed.run_type == run_type :
                self.config_context.logging.logger.info(
                    f"Parsing check group configuration for [{feed.check_group_identifier}]..."
                )
                self.config_context.logging.logger.info(feed)
                self.config_context.logging.logger.info(
                    f"Dependency Datasets Specified: "
                    f"{feed.dependency_datasets} "
                    f"({len(feed.dependency_datasets)})"
                )
                for dataset in feed.dependency_datasets:
                    if not self.config_context.spark_config.spark.catalog.tableExists(dataset):
                        break
                for check in feed.checks:
                    check_cls = CHECK_REGISTRY.get(check.name)
                    if check_cls is None:
                        continue
                    validator = check_cls(feed, check.name, self.config_context)
                    result = validator.validate()
                    results.append(result)
        return results

