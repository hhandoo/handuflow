"""Negative tests for EnforceMasterConfig."""

from __future__ import annotations

from collections.abc import Callable

from handuflow.platform.configurator.dataclasses.context import ConfigurationContext
from handuflow.platform.validation.validations.enforce_master_config import (
    EnforceMasterConfig,
)


def test_enforce_master_config_positive(
    enforce_master_config: EnforceMasterConfig,
    positive_configuration_context: ConfigurationContext,
    assert_validation_passes: Callable[..., None],
) -> None:
    """Master config validation should pass for a valid config.ini."""

    assert_validation_passes(
        enforce_master_config,
        positive_configuration_context,
    )


def test_invalid_system_name(
    enforce_master_config: EnforceMasterConfig,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Invalid system_name values should fail master config validation."""

    assert_validation_raises(
        enforce_master_config,
        make_validation_context("invalid_system_name"),
        error_code="HF-VALIDATION-015",
    )


def test_missing_logging_section(
    enforce_master_config: EnforceMasterConfig,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Missing LOGGING section should fail master config validation."""

    assert_validation_raises(
        enforce_master_config,
        make_validation_context("missing_logging_section"),
        error_code="HF-VALIDATION-017",
    )
