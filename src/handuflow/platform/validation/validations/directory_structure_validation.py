"""Validation for HanduFLOW directory and feed configuration structure."""

from __future__ import annotations

import logging
from pathlib import Path

from ...configurator.dataclasses.context import ConfigurationContext
from ...exceptions.domains.validation import ValidationError
from ...exceptions.errors.validation import ValidationErrors
from ...storage import StoragePath
from ..base import Validation
from ..dataclasses import ValidationResult

FEED_CONFIGURATION_DIR = "feed_configuration"
FEED_LOOKUP_FILE = "__feed_lookup"
YML_SUFFIX = ".yml"


class DirectoryStructureValidation(Validation):
    """Validate HanduFLOW directory layout and feed configuration structure."""

    @property
    def name(self) -> str:
        return "directory_structure_validation"

    @property
    def key(self) -> int:
        return 1

    def validate(self, configuration_context: ConfigurationContext) -> ValidationResult:
        logger = configuration_context.logging.logger
        provider = configuration_context.storage_manager.provider
        root = configuration_context.storage_path
        violations: list[str] = []

        logger.info("Starting directory structure validation for %s", root.uri)

        ignored_directories = {configuration_context.logging.log_directory_name}
        logger.info(
            "Checking that all file and directory names are lowercase "
            "(ignoring directories: %s)",
            ", ".join(sorted(ignored_directories)),
        )
        lowercase_violations = self._validate_lowercase_names(
            provider,
            root,
            logger,
            ignored_directories,
        )
        violations.extend(lowercase_violations)
        logger.info(
            "Lowercase name check completed with %d violation(s)",
            len(lowercase_violations),
        )

        logger.info("Checking feed configuration directory structure")
        feed_violations = self._validate_feed_configuration(provider, root, logger)
        violations.extend(feed_violations)
        logger.info(
            "Feed configuration check completed with %d violation(s)",
            len(feed_violations),
        )

        if violations:
            logger.error(
                "Directory structure validation failed with %d total violation(s)",
                len(violations),
            )
            raise ValidationError(
                ValidationErrors.VALIDATION_FAILED,
                validation_name=self.name,
                violations=violations,
            )

        logger.info("Directory structure validation completed successfully")
        return ValidationResult(
            self.key,
            self.name,
            True,
            "HanduFLOW directory structure is valid.",
        )

    def _validate_lowercase_names(
        self,
        provider,
        root: StoragePath,
        logger: logging.Logger,
        ignored_directories: set[str],
    ) -> list[str]:
        violations: list[str] = []
        checked_count = 0

        for entry in self._iter_entries(provider, root, ignored_directories, logger):
            checked_count += 1
            entry_name = Path(entry.uri).name
            logger.info("Checking lowercase name for entry: %s", entry.uri)

            if entry_name != entry_name.lower():
                message = f"Name must be lowercase: {entry.uri}"
                logger.info("Lowercase name violation found: %s", message)
                violations.append(message)

        logger.info("Checked %d entries for lowercase naming", checked_count)
        return violations

    def _validate_feed_configuration(
        self,
        provider,
        root: StoragePath,
        logger: logging.Logger,
    ) -> list[str]:
        violations: list[str] = []
        feed_config_path = StoragePath(f"{root.uri}/{FEED_CONFIGURATION_DIR}")

        logger.info("Checking for required directory: %s", feed_config_path.uri)

        if not provider.exists(feed_config_path):
            message = f"Missing required directory: {FEED_CONFIGURATION_DIR}"
            logger.info("Feed configuration violation found: %s", message)
            violations.append(message)
            return violations

        if not provider.is_directory(feed_config_path):
            message = f"{FEED_CONFIGURATION_DIR} must be a directory"
            logger.info("Feed configuration violation found: %s", message)
            violations.append(message)
            return violations

        logger.info(
            "Validating feed lookup files under %s",
            feed_config_path.uri,
        )

        directory_count = 0
        for directory in self._iter_directories(provider, feed_config_path):
            directory_count += 1
            logger.info("Checking feed lookup requirement for directory: %s", directory.uri)
            directory_violations = self._validate_feed_lookup_for_directory(
                provider,
                directory,
                logger,
            )
            violations.extend(directory_violations)

        logger.info(
            "Checked %d directories under feed_configuration",
            directory_count,
        )
        return violations

    @staticmethod
    def _validate_feed_lookup_for_directory(
        provider,
        directory: StoragePath,
        logger: logging.Logger,
    ) -> list[str]:
        children = list(provider.list(directory))

        yml_files = [
            child
            for child in children
            if provider.is_file(child)
            and Path(child.uri).suffix.lower() == YML_SUFFIX
        ]

        if not yml_files:
            logger.info(
                "Skipping directory with no yml files: %s",
                directory.uri,
            )
            return []

        yml_file_names = [Path(path.uri).name for path in yml_files]
        logger.info(
            "Directory %s contains %d yml file(s): %s",
            directory.uri,
            len(yml_files),
            ", ".join(yml_file_names),
        )
        logger.info(
            "Checking for required feed lookup file %s in %s",
            FEED_LOOKUP_FILE,
            directory.uri,
        )

        has_feed_lookup = any(
            provider.is_file(child) and Path(child.uri).name == FEED_LOOKUP_FILE
            for child in children
        )
        if has_feed_lookup:
            logger.info(
                "Feed lookup file found for directory: %s",
                directory.uri,
            )
            return []

        message = (
            "Directory contains yml files but is missing "
            f"{FEED_LOOKUP_FILE}: {directory.uri}"
        )
        logger.info("Feed lookup violation found: %s", message)
        return [message]

    def _iter_entries(
        self,
        provider,
        path: StoragePath,
        ignored_directories: set[str],
        logger: logging.Logger,
    ):
        if not provider.exists(path) or not provider.is_directory(path):
            return

        for child in provider.list(path):
            if (
                provider.is_directory(child)
                and Path(child.uri).name in ignored_directories
            ):
                logger.info("Skipping ignored directory: %s", child.uri)
                continue

            yield child
            if provider.is_directory(child):
                yield from self._iter_entries(
                    provider,
                    child,
                    ignored_directories,
                    logger,
                )

    def _iter_directories(self, provider, path: StoragePath):
        if not provider.is_directory(path):
            return

        yield path

        for child in provider.list(path):
            if provider.is_directory(child):
                yield from self._iter_directories(provider, child)
