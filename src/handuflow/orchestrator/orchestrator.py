

# internal
from handuflow import __version__

from handuflow import ConfigurationContext
from handuflow import SystemConfigurator

from handuflow import ValidationRunner
from handuflow import ValidationResult



# external
from pyspark.sql import SparkSession



class Orchestrator:

    def __init__(self, spark_session: SparkSession, handu_flow_directory_path: str):
        self.spark_session = spark_session
        self.handu_flow_directory_path = handu_flow_directory_path


    def run(self):
        config_context = self.__get_configuration_context()
        config_context.logging.logger.info(f"Welcome to HanduFLOW [v{__version__}]: Framework for Lakehouse Workflows and Orchestration.")
        config_context.logging.logger.info(
            f"Performing system validation..."
        )
        validation_result, all_passed = self.__run_validation(config_context)

        if all_passed:
            config_context.logging.logger.info(f"System validation completed and no issues have been detected.")
        else:
            config_context.logging.logger.error(f"System validation failed, please check the configuration and try again, terminating workflow.")

        config_context.logging.logger.info(f"Thank you for using HanduFLOW [v{__version__}].")

    @staticmethod
    def __run_validation(configuration_context: ConfigurationContext) -> (list[ValidationResult], bool):
        validation_runner = ValidationRunner(configuration_context)
        return validation_runner.run(), validation_runner.all_passed()

    def __get_configuration_context(self) -> ConfigurationContext:
        configuration = SystemConfigurator(self.handu_flow_directory_path, self.spark_session,)
        configuration.configure()
        return  configuration.get_configuration_context()