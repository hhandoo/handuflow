import yaml
from typing import Type, cast, Any

from .checks import *
from .dataclass import CheckDC, CheckObj, CheckResult
from ..platform.configurator.dataclasses.context import ConfigurationContext
from .base import BaseDataQualityCheck
from ..platform.exceptions.domains.data_quality import DataQualityError
from ..platform.exceptions.errors.data_quality import DataQualityErrors

CHECK_REGISTRY: dict[str, Type[BaseDataQualityCheck]] = {
    "custom_check": CustomCheck,
    "null_check": NullCheck,
    "not_blank_check": NotBlankCheck,
    "duplicate_check": DuplicateCheck,
    "range_check": RangeCheck,
}


class DataQualityManager:
    def __init__(self, config_context: ConfigurationContext):
        self.config_context = config_context
        self.list_of_feed_ymls = config_context.list_of_feed_ymls

    def __load_checks(self) -> list[CheckObj]:
        logger = self.config_context.logging.logger
        logger.info("Parsing data quality configuration...")
        parsed_data_quality_checks: list[CheckObj] = []
        for current_feed in self.list_of_feed_ymls:
            logger.info(
                "Parsing feed configuration [%s]...",
                current_feed.uri,
            )
            try:
                with open(current_feed.uri, encoding="utf-8") as feed_file:
                    config = cast(
                        dict[str, Any] | None,
                        yaml.safe_load(feed_file),
                    )
            except FileNotFoundError as ex:
                raise DataQualityError(
                    DataQualityErrors.YML_FILE_NOT_FOUND,
                    file_path=current_feed.uri,
                ) from ex
            except yaml.YAMLError as ex:
                raise DataQualityError(
                    DataQualityErrors.INVALID_YAML,
                    file_path=current_feed.uri,
                ) from ex
            if not isinstance(config, dict):
                raise DataQualityError(
                    DataQualityErrors.INVALID_CONFIGURATION,
                    file_path=current_feed.uri,
                )
            source_raw = config.get("source")
            if not isinstance(source_raw, dict):
                raise DataQualityError(
                    DataQualityErrors.INVALID_FEED_SOURCE_CONFIGURATION,
                    file_path=current_feed.uri,
                )
            feed_meta_raw = config.get("feed_meta")
            if not isinstance(feed_meta_raw, dict):
                raise DataQualityError(
                    DataQualityErrors.INVALID_FEED_METADATA,
                    file_path=current_feed.uri,
                )
            data_quality_checks_raw = config.get("data_quality_checks")
            if not isinstance(data_quality_checks_raw, list):
                raise DataQualityError(
                    DataQualityErrors.CHECK_CONFIGURATION_PARSE_ERROR,
                    file_path=current_feed.uri,
                )
            source = cast(dict[str, Any], source_raw)
            feed_meta = cast(dict[str, Any], feed_meta_raw)
            data_quality_checks = cast(
                list[dict[str, Any]],
                data_quality_checks_raw,
            )
            source_type = source.get("type")
            source_schema = source.get("schema")
            source_table = source.get("table")
            feed_identifier = feed_meta.get("unique_identifier")
            if not isinstance(source_type, str) or not source_type:
                raise DataQualityError(
                    DataQualityErrors.INVALID_FEED_SOURCE_CONFIGURATION,
                    file_path=current_feed.uri,
                    field="source.type",
                )
            if not isinstance(source_schema, str) or not source_schema:
                raise DataQualityError(
                    DataQualityErrors.INVALID_FEED_METADATA,
                    file_path=current_feed.uri,
                    field="source.schema",
                )
            if not isinstance(source_table, str) or not source_table:
                raise DataQualityError(
                    DataQualityErrors.INVALID_FEED_SOURCE_CONFIGURATION,
                    file_path=current_feed.uri,
                    field="source.table",
                )
            if not isinstance(feed_identifier, str) or not feed_identifier:
                raise DataQualityError(
                    DataQualityErrors.INVALID_FEED_METADATA,
                    file_path=current_feed.uri,
                    field="feed_meta.unique_identifier",
                )
            full_table_path = f"`{source_type}`.`{source_schema}`.`{source_table}`"
            table_path = f"`{source_schema}`.`{source_table}`"
            logger.info(
                "Found [%d] check group(s) for feed [%s].",
                len(data_quality_checks),
                feed_identifier,
            )
            for dq_check in data_quality_checks:
                check_group_identifier = dq_check.get("check_group_identifier")

                if (
                    not isinstance(check_group_identifier, str)
                    or not check_group_identifier
                ):
                    raise DataQualityError(
                        DataQualityErrors.INVALID_CHECK_CONFIGURATION,
                        file_path=current_feed.uri,
                        field="check_group_identifier",
                    )
                raw_checks = dq_check.get("checks", [])
                checklist: list[CheckDC] = []
                for raw_check in raw_checks:

                    if not isinstance(raw_check, dict):
                        raise DataQualityError(
                            DataQualityErrors.INVALID_CHECK_CONFIGURATION,
                            file_path=current_feed.uri,
                            check_group=check_group_identifier,
                        )

                    raw_check = cast(dict[str, Any], raw_check)
                    checklist.append(
                        CheckDC(
                            name=raw_check.get("name", ""),
                            check_range=raw_check.get("range", {}),
                            spark_timestamp_format=raw_check.get(
                                "spark_timestamp_format", None
                            ),
                            sql_query_pass=raw_check.get("sql_query_pass", None),
                            sql_query_fail=raw_check.get("sql_query_fail", None),
                            threshold=raw_check.get("threshold", None),
                        )
                    )

                dependency_datasets = dq_check.get("dependency_datasets")

                if dependency_datasets is None:
                    dependency_datasets = []

                if not isinstance(dependency_datasets, list):
                    raise DataQualityError(
                        DataQualityErrors.INVALID_DEPENDENCY_DATASET,
                        file_path=current_feed.uri,
                        check_group=check_group_identifier,
                    )

                parsed_data_quality_checks.append(
                    CheckObj(
                        full_file_path=current_feed.uri,
                        feed_identifier=feed_identifier,
                        full_table_path=full_table_path,
                        table_path=table_path,
                        check_group_identifier=dq_check.get(
                            "check_group_identifier", ""
                        ),
                        description=dq_check.get("description", ""),
                        run_type=dq_check.get("run_type", ""),
                        dependency_datasets=(
                            []
                            if dq_check.get("dependency_datasets", []) is None
                            else dq_check.get("dependency_datasets", [])
                        ),
                        column=dq_check.get("column", ""),
                        checks=checklist,
                    )
                )

            logger.info(
                "Successfully parsed feed [%s].",
                feed_identifier,
            )

        logger.info(
            "Loaded [%d] data quality check group(s).",
            len(parsed_data_quality_checks),
        )
        return parsed_data_quality_checks

    def run(self, run_type: str = "PRE_LOAD") -> list[CheckResult]:
        logger = self.config_context.logging.logger
        logger.info(f"Starting data quality execution. Run type: [{run_type}]")

        try:
            logger.info(f"Reading data quality checks from all YML files...")
            data_quality_manifest = self.__load_checks()
        except Exception:
            logger.error(
                f"Something went wrong while reading data quality checks YML files."
            )
            raise DataQualityError(
                DataQualityErrors.COLUMN_NOT_FOUND,
                table_name="customers",
                column_name="email",
            )
        logger.info(f"Loaded [{len(data_quality_manifest)}] data quality check groups.")
        results: list[CheckResult] = []
        for feed in data_quality_manifest:
            if feed.run_type != run_type:
                logger.debug(
                    "Skipping check group [%s]. Run type [%s] does not match [%s].",
                    feed.check_group_identifier,
                    feed.run_type,
                    run_type,
                )
                continue
            logger.info(
                "Processing check group [%s].",
                feed.check_group_identifier,
            )
            logger.debug("Configuration:\n%s", feed)
            logger.info(
                "Dependency datasets: %s",
                feed.dependency_datasets,
            )
            dependency_missing = False
            for dataset in feed.dependency_datasets:
                if not self.config_context.spark_config.spark.catalog.tableExists(
                    dataset
                ):
                    logger.error(
                        "Dependency dataset [%s] does not exist.",
                        dataset,
                    )
                    dependency_missing = True
            if dependency_missing:
                logger.warning(
                    "Skipping check group [%s] because dependency datasets are missing.",
                    feed.check_group_identifier,
                )
                continue
            for check in feed.checks:
                logger.debug("Check Details:%s", check)
                check_cls = CHECK_REGISTRY.get(check.name)
                if check_cls is None:
                    logger.error(
                        "No validator registered for check [%s].",
                        check.name,
                    )
                    continue
                try:
                    validator = check_cls(
                        feed,
                        check.name,
                        check.check_range,
                        check.spark_timestamp_format,
                        check.sql_query_pass,
                        check.sql_query_fail,
                        check.threshold,
                        self.config_context,
                    )
                    result = validator.validate()
                    results.append(result)
                    logger.info(
                        "Check [%s] completed successfully.",
                        check.name,
                    )
                except Exception:
                    logger.exception(
                        "Check [%s] in group [%s] failed.",
                        check.name,
                        feed.check_group_identifier,
                    )
                    raise
        logger.info(
            f"[{run_type}] Data quality execution completed. Generated [%d] results.",
            len(results),
        )
        return results
