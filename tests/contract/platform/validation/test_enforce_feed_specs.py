"""Negative tests for EnforceFeedSpecs."""

from __future__ import annotations

from collections.abc import Callable

from handuflow.platform.configurator.dataclasses.context import ConfigurationContext
from handuflow.platform.validation.validations.enforce_feed_specs import EnforceFeedSpecs


def test_enforce_feed_specs_positive(
    enforce_feed_specs: EnforceFeedSpecs,
    positive_configuration_context: ConfigurationContext,
    assert_validation_passes: Callable[..., None],
) -> None:
    """Feed specs validation should pass for valid feed YAML files."""

    assert_validation_passes(
        enforce_feed_specs,
        positive_configuration_context,
    )


def test_missing_feed_specs(
    enforce_feed_specs: EnforceFeedSpecs,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Missing feed_specs section should fail validation."""

    assert_validation_raises(
        enforce_feed_specs,
        make_validation_context("missing_feed_specs"),
        error_code="HF-VALIDATION-039",
    )
