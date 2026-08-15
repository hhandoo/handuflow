"""Negative tests for EnforceDataQualityChecks."""

from __future__ import annotations

from collections.abc import Callable

from handuflow.platform.configurator.dataclasses.context import ConfigurationContext
from handuflow.platform.validation.validations.enforce_data_quality_checks import (
    EnforceDataQualityChecks,
)


def test_enforce_data_quality_checks_positive(
    enforce_data_quality_checks: EnforceDataQualityChecks,
    positive_configuration_context: ConfigurationContext,
    assert_validation_passes: Callable[..., None],
) -> None:
    """Data quality checks validation should pass for valid feed YAML files."""

    assert_validation_passes(
        enforce_data_quality_checks,
        positive_configuration_context,
    )


def test_missing_data_quality_checks(
    enforce_data_quality_checks: EnforceDataQualityChecks,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Missing data_quality_checks section should fail validation."""

    assert_validation_raises(
        enforce_data_quality_checks,
        make_validation_context("missing_data_quality_checks"),
        error_code="HF-VALIDATION-029",
    )


def test_invalid_run_type(
    enforce_data_quality_checks: EnforceDataQualityChecks,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Invalid run_type values should fail validation."""

    assert_validation_raises(
        enforce_data_quality_checks,
        make_validation_context("invalid_run_type"),
        error_code="HF-VALIDATION-038",
    )


def test_invalid_dependency_datasets(
    enforce_data_quality_checks: EnforceDataQualityChecks,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Non-list dependency_datasets values should fail validation."""

    assert_validation_raises(
        enforce_data_quality_checks,
        make_validation_context("invalid_dependency_datasets"),
        error_code="HF-VALIDATION-039",
    )
