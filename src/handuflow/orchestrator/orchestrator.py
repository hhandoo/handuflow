from handuflow._version import __version__

from ..data_quality import DataQualityManager
from ..platform.configurator import SystemConfigurator
from ..platform.configurator.dataclasses.context import ConfigurationContext
from ..platform.validation import ValidationResult, ValidationRunner
from pyspark.sql import SparkSession


class Orchestrator:

    def __init__(self, spark_session: SparkSession, handu_flow_directory_path: str):
        self.spark_session = spark_session
        self.handu_flow_directory_path = handu_flow_directory_path

    def run(self):
        config_context = self.__get_configuration_context()
        config_context.logging.logger.info(
            f"Welcome to HanduFLOW [v{__version__}]: Framework for Lakehouse Workflows and Orchestration."
        )
        config_context.logging.logger.info(
            "Performing system validation..."
        )
        # validation_result, all_passed = self.__run_validation(config_context)
        #
        # if all_passed:
        #     config_context.logging.logger.info(
        #         "System validation completed and no issues have been detected."
        #     )
        # else:
        #     config_context.logging.logger.error(
        #         "System validation failed, please check the configuration and try again, "
        #         "terminating workflow."
        #     )

        pre_load_results_list = self.__enforce_data_quality(configuration_context = config_context, run_type = "PRE_LOAD")

        print(pre_load_results_list)

        config_context.logging.logger.info(f"Thank you for using HanduFLOW [v{__version__}].")

    @staticmethod
    def __run_validation(
        configuration_context: ConfigurationContext,
    ) -> tuple[list[ValidationResult], bool]:
        validation_runner = ValidationRunner(configuration_context)
        results = validation_runner.run()
        return results, all(result.passed for result in results)

    def __get_configuration_context(self) -> ConfigurationContext:
        configuration = SystemConfigurator(self.handu_flow_directory_path, self.spark_session)
        configuration.configure()
        return configuration.get_configuration_context()

    @staticmethod
    def __enforce_data_quality(configuration_context: ConfigurationContext, run_type: str):
        my_data_quality_manager = DataQualityManager(configuration_context)
        return my_data_quality_manager.run(run_type)
