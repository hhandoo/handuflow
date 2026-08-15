"""Negative tests for EnforceLoadDetails."""

from __future__ import annotations

from collections.abc import Callable

from handuflow.platform.configurator.dataclasses.context import ConfigurationContext
from handuflow.platform.validation.validations.enforce_load_details import (
    EnforceLoadDetails,
)


def test_enforce_load_details_positive(
    enforce_load_details: EnforceLoadDetails,
    positive_configuration_context: ConfigurationContext,
    assert_validation_passes: Callable[..., None],
) -> None:
    """Load details validation should pass for valid feed YAML files."""

    assert_validation_passes(
        enforce_load_details,
        positive_configuration_context,
    )


def test_missing_load_details(
    enforce_load_details: EnforceLoadDetails,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Missing load_details section should fail validation."""

    assert_validation_raises(
        enforce_load_details,
        make_validation_context("missing_load_details"),
        error_code="HF-VALIDATION-029",
    )


def test_invalid_load_type(
    enforce_load_details: EnforceLoadDetails,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Invalid load_details.type values should fail validation."""

    assert_validation_raises(
        enforce_load_details,
        make_validation_context("invalid_load_type"),
        error_code="HF-VALIDATION-032",
    )
