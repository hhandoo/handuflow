"""Validation for feed configuration YAML files."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from ...configurator.dataclasses.context import ConfigurationContext
from ...exceptions.base import HanduflowError
from ...exceptions.domains.validation import ValidationError
from ...exceptions.errors.validation import ValidationErrors
from ...storage import StoragePath
from ..base import Validation
from ..dataclasses import ValidationResult

FEED_CONFIGURATION_DIR = "feed_configuration"
YML_SUFFIX = ".yml"

FEED_META_KEYS = ("unique_identifier", "upstream_identifier", "downstream_identifier")
LOAD_DETAILS_KEYS = ("type",)
SOURCE_TARGET_KEYS = ("type", "format", "schema", "table")
FEED_SPECS_KEYS = (
    "primary_key",
    "composite_key",
    "partition_columns",
    "optimize_command",
    "custom_selection",
    "enforce_schema",
)
OPTIMIZE_COMMAND_KEYS = ("enabled", "where", "zorder_by")
ENFORCE_SCHEMA_KEYS = ("type", "fields")
FIELD_KEYS = ("name", "type", "nullable", "metadata")
CUSTOM_SELECTION_KEYS = ("enabled", "sql_file")


class FeedConfigurationValidation(Validation):
    """Validate feed configuration YAML files under feed_configuration."""

    @property
    def name(self) -> str:
        return "feed_configuration_validation"

    @property
    def key(self) -> int:
        return 2

    def validate(self, configuration_context: ConfigurationContext) -> ValidationResult:
        logger = configuration_context.logging.logger
        provider = configuration_context.storage_manager.provider
        root = configuration_context.storage_path

        try:
            return self._run_validation(logger, provider, root)
        except HanduflowError:
            raise
        except Exception as exc:
            error = ValidationError(
                ValidationErrors.VALIDATION_UNKNOWN,
                validation_name=self.name,
                cause=exc,
            )
            self._log_validation_error(logger, error)
            raise error from exc

    def _run_validation(
        self,
        logger: logging.Logger,
        provider,
        root: StoragePath,
    ) -> ValidationResult:
        violations: list[str] = []
        feed_config_path = StoragePath(f"{root.uri}/{FEED_CONFIGURATION_DIR}")

        if not provider.exists(feed_config_path):
            raise self._build_error(
                ValidationErrors.FEED_CONFIGURATION_DIR_MISSING,
                logger=logger,
                path=feed_config_path.uri,
            )

        if not provider.is_directory(feed_config_path):
            raise self._build_error(
                ValidationErrors.FEED_CONFIGURATION_DIR_NOT_DIRECTORY,
                logger=logger,
                path=feed_config_path.uri,
            )

        yml_files = self._collect_yml_files(provider, feed_config_path)

        for yml_file in yml_files:
            file_violations = self._validate_yml_file(yml_file, provider, logger)
            if file_violations:
                violations.extend(file_violations)
            else:
                logger.info("%s is valid", yml_file.uri)

        if violations:
            raise self._build_error(
                ValidationErrors.FEED_CONFIGURATION_VALIDATION_FAILED,
                logger=logger,
                violations=violations,
            )

        return ValidationResult(
            self.key,
            self.name,
            True,
            "Feed configuration YAML files are valid.",
        )

    def _validate_yml_file(
        self,
        yml_file: StoragePath,
        provider,
        logger: logging.Logger,
    ) -> list[str]:
        file_label = yml_file.uri

        try:
            raw_content = provider.read(yml_file).decode()
        except (OSError, UnicodeError) as exc:
            error = ValidationError(
                ValidationErrors.FEED_CONFIGURATION_FILE_READ_FAILED,
                validation_name=self.name,
                path=file_label,
                cause=exc,
            )
            self._log_file_invalid(logger, file_label, error)
            return [self._format_violation(error)]

        try:
            document = yaml.safe_load(raw_content)
        except yaml.YAMLError as exc:
            error = ValidationError(
                ValidationErrors.FEED_CONFIGURATION_INVALID_YML,
                validation_name=self.name,
                path=file_label,
                cause=exc,
            )
            self._log_file_invalid(logger, file_label, error)
            return [self._format_violation(error)]

        if not isinstance(document, dict):
            error = ValidationError(
                ValidationErrors.FEED_CONFIGURATION_INVALID_STRUCTURE,
                validation_name=self.name,
                path=file_label,
                reason="yml root must be a mapping",
            )
            self._log_file_invalid(logger, file_label, error)
            return [self._format_violation(error)]

        structure_violations = self._validate_feed_document(document, file_label)
        if structure_violations:
            error = ValidationError(
                ValidationErrors.FEED_CONFIGURATION_INVALID_STRUCTURE,
                validation_name=self.name,
                path=file_label,
                violations=structure_violations,
            )
            self._log_file_invalid(logger, file_label, error, structure_violations)
            return structure_violations

        return []

    def _build_error(
        self,
        error_definition,
        *,
        logger: logging.Logger,
        **context: object,
    ) -> ValidationError:
        error = ValidationError(
            error_definition,
            validation_name=self.name,
            **context,
        )
        self._log_validation_error(logger, error)
        return error

    @staticmethod
    def _format_violation(error: ValidationError) -> str:
        details = error.context.get("reason") or error.context.get("violations")
        if details:
            return f"[{error.code}] {error.message}: {details}"
        if error.cause:
            return f"[{error.code}] {error.message}: {error.cause}"
        path = error.context.get("path")
        if path:
            return f"[{error.code}] {path}: {error.message}"
        return f"[{error.code}] {error.message}"

    @staticmethod
    def _log_validation_error(logger: logging.Logger, error: ValidationError) -> None:
        logger.error("[%s] %s", error.code, error.message)
        for key, value in error.context.items():
            if key == "validation_name":
                continue
            if key == "violations" and isinstance(value, list):
                for violation in value:
                    logger.error("  %s", violation)
                continue
            logger.error("  %s: %s", key, value)
        if error.cause:
            logger.error("  cause: %s", error.cause)

    @staticmethod
    def _log_file_invalid(
        logger: logging.Logger,
        file_label: str,
        error: ValidationError,
        violations: list[str] | None = None,
    ) -> None:
        logger.error("%s is invalid: [%s] %s", file_label, error.code, error.message)
        if violations:
            for violation in violations:
                logger.error("  %s", violation)
            return

        reason = error.context.get("reason")
        if reason:
            logger.error("  %s", reason)
        if error.cause:
            logger.error("  cause: %s", error.cause)

    def _collect_yml_files(self, provider, path: StoragePath) -> list[StoragePath]:
        yml_files: list[StoragePath] = []

        for entry in provider.list(path):
            if provider.is_directory(entry):
                yml_files.extend(self._collect_yml_files(provider, entry))
                continue

            if provider.is_file(entry) and Path(entry.uri).suffix.lower() == YML_SUFFIX:
                yml_files.append(entry)

        return yml_files

    def _validate_feed_document(
        self,
        document: dict[str, Any],
        file_label: str,
    ) -> list[str]:
        violations: list[str] = []
        required_sections = (
            "feed_meta",
            "load_details",
            "source",
            "target",
            "feed_specs",
        )

        for section in required_sections:
            if section not in document:
                violations.append(f"{file_label}: missing required section '{section}'")

        if "feed_meta" in document:
            violations.extend(
                self._validate_mapping_section(
                    document["feed_meta"],
                    section_name="feed_meta",
                    required_keys=FEED_META_KEYS,
                    string_keys=FEED_META_KEYS,
                    file_label=file_label,
                )
            )

        if "load_details" in document:
            violations.extend(
                self._validate_mapping_section(
                    document["load_details"],
                    section_name="load_details",
                    required_keys=LOAD_DETAILS_KEYS,
                    string_keys=LOAD_DETAILS_KEYS,
                    file_label=file_label,
                )
            )

        for section in ("source", "target"):
            if section in document:
                violations.extend(
                    self._validate_mapping_section(
                        document[section],
                        section_name=section,
                        required_keys=SOURCE_TARGET_KEYS,
                        string_keys=SOURCE_TARGET_KEYS,
                        file_label=file_label,
                    )
                )

        if "feed_specs" in document:
            violations.extend(
                self._validate_feed_specs(
                    document["feed_specs"],
                    file_label=file_label,
                )
            )

        return violations

    def _validate_feed_specs(
        self,
        feed_specs: Any,
        *,
        file_label: str,
    ) -> list[str]:
        violations: list[str] = []
        section_name = "feed_specs"

        if not isinstance(feed_specs, dict):
            return [f"{file_label}: {section_name} must be a mapping"]

        for key in FEED_SPECS_KEYS:
            if key not in feed_specs:
                violations.append(
                    f"{file_label}: missing required key '{section_name}.{key}'"
                )

        if "primary_key" in feed_specs:
            violations.extend(
                self._validate_string(
                    feed_specs["primary_key"],
                    f"{section_name}.primary_key",
                    file_label,
                )
            )

        if "composite_key" in feed_specs:
            violations.extend(
                self._validate_string_list(
                    feed_specs["composite_key"],
                    f"{section_name}.composite_key",
                    file_label,
                )
            )

        if "partition_columns" in feed_specs:
            violations.extend(
                self._validate_string_list(
                    feed_specs["partition_columns"],
                    f"{section_name}.partition_columns",
                    file_label,
                )
            )

        if "optimize_command" in feed_specs:
            violations.extend(
                self._validate_optimize_command(
                    feed_specs["optimize_command"],
                    file_label=file_label,
                )
            )

        if "custom_selection" in feed_specs:
            violations.extend(
                self._validate_custom_selection(
                    feed_specs["custom_selection"],
                    file_label=file_label,
                )
            )

        if "enforce_schema" in feed_specs:
            violations.extend(
                self._validate_enforce_schema(
                    feed_specs["enforce_schema"],
                    file_label=file_label,
                )
            )

        return violations

    def _validate_optimize_command(
        self,
        optimize_command: Any,
        *,
        file_label: str,
    ) -> list[str]:
        violations: list[str] = []
        section_name = "feed_specs.optimize_command"

        if not isinstance(optimize_command, dict):
            return [f"{file_label}: {section_name} must be a mapping"]

        for key in OPTIMIZE_COMMAND_KEYS:
            if key not in optimize_command:
                violations.append(
                    f"{file_label}: missing required key '{section_name}.{key}'"
                )

        if "enabled" in optimize_command and not isinstance(optimize_command["enabled"], bool):
            violations.append(
                f"{file_label}: {section_name}.enabled must be a boolean"
            )

        if "where" in optimize_command:
            where_clause = optimize_command["where"]
            if not isinstance(where_clause, dict):
                violations.append(f"{file_label}: {section_name}.where must be a mapping")
            else:
                for key, value in where_clause.items():
                    if not isinstance(key, str):
                        violations.append(
                            f"{file_label}: {section_name}.where keys must be strings"
                        )
                    if not isinstance(value, (str, int, float, bool)):
                        violations.append(
                            f"{file_label}: {section_name}.where['{key}'] must be a scalar value"
                        )

        if "zorder_by" in optimize_command:
            violations.extend(
                self._validate_string_list(
                    optimize_command["zorder_by"],
                    f"{section_name}.zorder_by",
                    file_label,
                )
            )

        return violations

    def _validate_custom_selection(
        self,
        custom_selection: Any,
        *,
        file_label: str,
    ) -> list[str]:
        violations: list[str] = []
        section_name = "feed_specs.custom_selection"

        if not isinstance(custom_selection, list):
            return [f"{file_label}: {section_name} must be a list"]

        for index, item in enumerate(custom_selection):
            item_path = f"{section_name}[{index}]"

            if not isinstance(item, dict):
                violations.append(f"{file_label}: {item_path} must be a mapping")
                continue

            if not item:
                violations.append(f"{file_label}: {item_path} must not be empty")
                continue

            unknown_keys = set(item) - set(CUSTOM_SELECTION_KEYS)
            if unknown_keys:
                violations.append(
                    f"{file_label}: {item_path} contains unsupported keys: "
                    f"{', '.join(sorted(unknown_keys))}"
                )

            if "enabled" in item and not isinstance(item["enabled"], bool):
                violations.append(f"{file_label}: {item_path}.enabled must be a boolean")

            if "sql_file" in item:
                violations.extend(
                    self._validate_string(item["sql_file"], f"{item_path}.sql_file", file_label)
                )

        return violations

    def _validate_enforce_schema(
        self,
        enforce_schema: Any,
        *,
        file_label: str,
    ) -> list[str]:
        violations: list[str] = []
        section_name = "feed_specs.enforce_schema"

        if not isinstance(enforce_schema, dict):
            return [f"{file_label}: {section_name} must be a mapping"]

        for key in ENFORCE_SCHEMA_KEYS:
            if key not in enforce_schema:
                violations.append(
                    f"{file_label}: missing required key '{section_name}.{key}'"
                )

        if "type" in enforce_schema:
            violations.extend(
                self._validate_string(enforce_schema["type"], f"{section_name}.type", file_label)
            )

        if "fields" in enforce_schema:
            fields = enforce_schema["fields"]
            if not isinstance(fields, list):
                violations.append(f"{file_label}: {section_name}.fields must be a list")
            else:
                for index, field in enumerate(fields):
                    field_path = f"{section_name}.fields[{index}]"
                    violations.extend(
                        self._validate_enforce_schema_field(field, field_path, file_label)
                    )

        return violations

    def _validate_enforce_schema_field(
        self,
        field: Any,
        field_path: str,
        file_label: str,
    ) -> list[str]:
        violations: list[str] = []

        if not isinstance(field, dict):
            return [f"{file_label}: {field_path} must be a mapping"]

        for key in FIELD_KEYS:
            if key not in field:
                violations.append(f"{file_label}: missing required key '{field_path}.{key}'")

        if "name" in field:
            violations.extend(self._validate_string(field["name"], f"{field_path}.name", file_label))

        if "type" in field:
            violations.extend(self._validate_string(field["type"], f"{field_path}.type", file_label))

        if "nullable" in field and not isinstance(field["nullable"], bool):
            violations.append(f"{file_label}: {field_path}.nullable must be a boolean")

        if "metadata" in field and not isinstance(field["metadata"], dict):
            violations.append(f"{file_label}: {field_path}.metadata must be a mapping")

        return violations

    def _validate_mapping_section(
        self,
        section: Any,
        *,
        section_name: str,
        required_keys: tuple[str, ...],
        string_keys: tuple[str, ...],
        file_label: str,
    ) -> list[str]:
        violations: list[str] = []

        if not isinstance(section, dict):
            return [f"{file_label}: {section_name} must be a mapping"]

        for key in required_keys:
            if key not in section:
                violations.append(
                    f"{file_label}: missing required key '{section_name}.{key}'"
                )

        for key in string_keys:
            if key in section:
                violations.extend(
                    self._validate_string(section[key], f"{section_name}.{key}", file_label)
                )

        return violations

    @staticmethod
    def _validate_string(value: Any, path: str, file_label: str) -> list[str]:
        if isinstance(value, str):
            return []
        return [f"{file_label}: {path} must be a string"]

    @staticmethod
    def _validate_string_list(value: Any, path: str, file_label: str) -> list[str]:
        if not isinstance(value, list):
            return [f"{file_label}: {path} must be a list"]

        violations: list[str] = []
        for index, item in enumerate(value):
            if not isinstance(item, str):
                violations.append(
                    f"{file_label}: {path}[{index}] must be a string"
                )
        return violations
