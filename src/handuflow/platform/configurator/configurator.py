"""System configurator for HanduFLOW.

Reads framework configuration, configures storage and logging, and exposes
the initialized runtime services for a HanduFLOW application directory.
"""

# System
import sys
import uuid
import logging
import configparser
from datetime import datetime

# Internal
from handuflow.platform.logging import StorageRotatingFileHandler, StorageFileHandler
from handuflow.platform.storage import StorageManager, StorageProvider, StoragePath

## Exception Handling
from handuflow.platform.exceptions.domains.configuration import ConfigurationError
from handuflow.platform.exceptions.base import HanduflowError
from handuflow.platform.exceptions.errors.configuration import ConfigurationErrors

class SystemConfigurator:
    def __init__(self, handu_flow_directory_path: str):
        self.logger = None

        if not handu_flow_directory_path:
            raise ConfigurationError(
                ConfigurationErrors.MISSING_HANDUFLOW_DIRECTORY,
                parameter="handu_flow_directory_path",
            )

        self.my_storage_manager = StorageManager()
        self.base_directory = StoragePath(handu_flow_directory_path)
        self.config = configparser.ConfigParser(interpolation=None)
        self.run_id = str(uuid.uuid4())


    def set_storage_provider(self, custom_storage_provider: StorageProvider):
        self.my_storage_manager.set_provider(custom_storage_provider)


    def configure(self) -> None:
        try:
            self.read_configuration()
        except ConfigurationError:
            raise
        except HanduflowError:
            raise
        except (OSError, UnicodeError, configparser.Error) as exc:
            raise ConfigurationError(
                ConfigurationErrors.READ_CONFIGURATION_ERROR,
                path=f"{self.base_directory.uri}/config.ini",
                cause=exc,
            ) from exc

        try:
            self.logger = self.configure_logger()
        except ConfigurationError:
            raise
        except HanduflowError:
            raise
        except (KeyError, TypeError, ValueError, OSError, configparser.Error) as exc:
            raise ConfigurationError(
                ConfigurationErrors.LOGGER_ERROR,
                cause=exc,
            ) from exc

    def get_configuration_context(self):
        # print(self.config['LOGGING']['log_format'])
        #
        # print(self.config, self.run_id)
        self.logger.info('test test')



    def configure_logger(self) -> logging.Logger:
        logging_section = self.config["LOGGING"]
        log_directory = StoragePath(
            f"{self.base_directory.uri}/{logging_section['log_directory_name']}"
        )
        storage = self.my_storage_manager.provider
        log_format = (
            logging_section.get("log_format")
            or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        formatter = logging.Formatter(log_format)

        if logging_section["type"] == "rotating":
            log_path = StoragePath(
                f"{log_directory.uri}/{logging_section['log_file_name']}.log"
            )
            file_handler = StorageRotatingFileHandler(
                log_path,
                storage,
                int(logging_section["max_bytes"]),
                int(logging_section["backup_count"]),
            )
        else:
            file_handler = StorageFileHandler(
                log_directory,
                logging_section["log_file_name"],
                self.run_id,
                storage,
                log_retention_days=int(logging_section["log_retention_days"]),
                run_date=datetime.now(),
            )

        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        logger = logging.getLogger(self.config["DEFAULT"]["system_name"])
        logger.setLevel(int(logging_section["default_log_level"]))
        logger.handlers.clear()
        logger.propagate = False
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger


    def read_configuration(self):
        config_bytes = self.my_storage_manager.provider.read(StoragePath(f"{self.base_directory.uri}/config.ini"))
        self.config.read_string(config_bytes.decode())
