"""Negative tests for EnforceSourceAndTarget."""

from __future__ import annotations

from collections.abc import Callable

from handuflow.platform.configurator.dataclasses.context import ConfigurationContext
from handuflow.platform.validation.validations.enforce_source_and_target import (
    EnforceSourceAndTarget,
)


def test_enforce_source_and_target_positive(
    enforce_source_and_target: EnforceSourceAndTarget,
    positive_configuration_context: ConfigurationContext,
    assert_validation_passes: Callable[..., None],
) -> None:
    """Source and target validation should pass for valid feed YAML files."""

    assert_validation_passes(
        enforce_source_and_target,
        positive_configuration_context,
    )


def test_missing_source(
    enforce_source_and_target: EnforceSourceAndTarget,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Missing source section should fail validation."""

    assert_validation_raises(
        enforce_source_and_target,
        make_validation_context("missing_source"),
        error_code="HF-VALIDATION-033",
    )


def test_blank_target_table(
    enforce_source_and_target: EnforceSourceAndTarget,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Blank target.table values should fail validation."""

    assert_validation_raises(
        enforce_source_and_target,
        make_validation_context("blank_target_table"),
        error_code="HF-VALIDATION-038",
    )
