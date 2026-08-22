"""Negative tests for EnforceFeedMeta."""

from __future__ import annotations

from collections.abc import Callable

from handuflow.platform.configurator.dataclasses.context import ConfigurationContext
from handuflow.platform.validation.validations.enforce_feed_meta import EnforceFeedMeta


def test_enforce_feed_meta_positive(
    enforce_feed_meta: EnforceFeedMeta,
    positive_configuration_context: ConfigurationContext,
    assert_validation_passes: Callable[..., None],
) -> None:
    """Feed metadata validation should pass for valid feed YAML files."""

    assert_validation_passes(
        enforce_feed_meta,
        positive_configuration_context,
    )


def test_missing_feed_meta(
    enforce_feed_meta: EnforceFeedMeta,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Missing feed_meta section should fail validation."""

    assert_validation_raises(
        enforce_feed_meta,
        make_validation_context("missing_feed_meta"),
        error_code="HF-VALIDATION-023",
    )


def test_vacuum_hours_out_of_range(
    enforce_feed_meta: EnforceFeedMeta,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Out-of-range vacuum_hours should fail validation."""

    assert_validation_raises(
        enforce_feed_meta,
        make_validation_context("vacuum_hours_out_of_range"),
        error_code="HF-VALIDATION-028",
    )


def test_invalid_batch_key(
    enforce_feed_meta: EnforceFeedMeta,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Invalid batch_key should fail validation."""

    assert_validation_raises(
        enforce_feed_meta,
        make_validation_context("invalid_batch_key"),
        error_code="HF-VALIDATION-062",
    )


def test_invalid_upstream_identifier(
    enforce_feed_meta: EnforceFeedMeta,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Invalid upstream_identifier should fail validation."""

    assert_validation_raises(
        enforce_feed_meta,
        make_validation_context("invalid_upstream_identifier"),
        error_code="HF-VALIDATION-063",
    )
