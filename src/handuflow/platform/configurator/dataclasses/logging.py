import logging
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LoggingConfiguration:

    type: str
    log_format: str
    log_directory_name: str
    log_file_name: str
    backup_count: int
    max_bytes: int
    default_log_level: int
    log_retention_days: int
    logger: logging.Logger