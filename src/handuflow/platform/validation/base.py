from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import NoReturn

from ..configurator.dataclasses.context import ConfigurationContext
from ..exceptions.definition import ErrorDefinition
from ..exceptions.domains.validation import ValidationError
from ..storage import StoragePath
from ..storage.base import StorageProvider
from .dataclasses import ValidationResult

SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class Validation(ABC):
    """Abstract base class for HanduFLOW validation rules."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stable identifier for this validation."""

    @property
    @abstractmethod
    def key(self) -> int:
        """Return the stable identifier key for this validation."""

    @abstractmethod
    def validate(
        self,
        configuration_context: ConfigurationContext,
    ) -> ValidationResult:
        """Execute the validation and return its outcome."""

    @staticmethod
    def _raise_validation_error(
        error: ErrorDefinition,
    ) -> NoReturn:
        """Raise a validation error."""

        raise ValidationError(error)

    @staticmethod
    def _directory_exists(
        provider: StorageProvider,
        path: StoragePath,
    ) -> bool:
        return provider.exists(path) and provider.is_directory(path)

    @staticmethod
    def _file_exists(
        provider: StorageProvider,
        path: StoragePath,
    ) -> bool:
        return provider.exists(path) and not provider.is_directory(path)

    @staticmethod
    def _path_name(
        path: StoragePath,
    ) -> str:
        return Path(path.uri).name

    @staticmethod
    def _read_text(
        provider: StorageProvider,
        path: StoragePath,
        encoding: str = "utf-8",
    ) -> str:
        return provider.read(path).decode(encoding)

    @staticmethod
    def _has_suffix(
        path: StoragePath,
        suffix: str,
    ) -> bool:
        return Path(path.uri).suffix.lower() == suffix.lower()

    def _recursive_directory_lookup(
        self,
        provider: StorageProvider,
        path: StoragePath,
        ignored_directories: set[str] | None = None,
        logger: logging.Logger | None = None,
    ) -> list[StoragePath]:

        ignored_directories = ignored_directories or set()

        if not self._directory_exists(provider, path):
            return []

        directories: list[StoragePath] = []

        for child in provider.list(path):

            if not provider.is_directory(child):
                continue

            directory_name = self._path_name(child)

            if directory_name in ignored_directories:
                if logger:
                    logger.info(
                        "Skipping ignored directory: %s",
                        child.uri,
                    )
                continue

            directories.append(child)

            directories.extend(
                self._recursive_directory_lookup(
                    provider,
                    child,
                    ignored_directories,
                    logger,
                )
            )

        return directories

    def _recursive_file_lookup(
        self,
        provider: StorageProvider,
        path: StoragePath,
        ignored_directories: set[str] | None = None,
        ignored_files: set[str] | None = None,
        logger: logging.Logger | None = None,
    ) -> list[StoragePath]:

        ignored_directories = ignored_directories or set()
        ignored_files = ignored_files or set()

        if not self._directory_exists(provider, path):
            return []

        files: list[StoragePath] = []

        for child in provider.list(path):

            child_name = self._path_name(child)

            if provider.is_directory(child):

                if child_name in ignored_directories:
                    if logger:
                        logger.info(
                            "Skipping ignored directory: %s",
                            child.uri,
                        )
                    continue

                files.extend(
                    self._recursive_file_lookup(
                        provider,
                        child,
                        ignored_directories,
                        ignored_files,
                        logger,
                    )
                )

                continue

            if child_name in ignored_files:
                if logger:
                    logger.info(
                        "Skipping ignored file: %s",
                        child.uri,
                    )
                continue

            files.append(child)

        return files

    @staticmethod
    def _is_snake_case(
        name: str,
    ) -> bool:
        return SNAKE_CASE_PATTERN.fullmatch(name) is not None

    @classmethod
    def _is_snake_case_directory(
        cls,
        path: StoragePath,
    ) -> bool:
        return cls._is_snake_case(
            Path(path.uri).name,
        )

    @classmethod
    def _is_snake_case_file(
        cls,
        path: StoragePath,
    ) -> bool:
        return cls._is_snake_case(
            Path(path.uri).stem,
        )
