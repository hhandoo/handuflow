"""Negative tests for EnforceHFDirStructure."""

from __future__ import annotations

from collections.abc import Callable

from handuflow.platform.configurator.dataclasses.context import ConfigurationContext
from handuflow.platform.validation.validations.enforce_HFdir_structure import (
    EnforceHFDirStructure,
)


def test_enforce_hfdir_structure_positive(
    enforce_hfdir_structure: EnforceHFDirStructure,
    positive_configuration_context: ConfigurationContext,
    assert_validation_passes: Callable[..., None],
) -> None:
    """Directory structure validation should pass for a valid HanduFLOW directory."""

    assert_validation_passes(
        enforce_hfdir_structure,
        positive_configuration_context,
    )


def test_missing_config_ini(
    enforce_hfdir_structure: EnforceHFDirStructure,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Missing config.ini should fail directory structure validation."""

    assert_validation_raises(
        enforce_hfdir_structure,
        make_validation_context("missing_config_ini"),
        error_code="HF-VALIDATION-003",
    )


def test_missing_feed_configuration(
    enforce_hfdir_structure: EnforceHFDirStructure,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Missing feed_configuration directory should fail validation."""

    assert_validation_raises(
        enforce_hfdir_structure,
        make_validation_context("missing_feed_configuration"),
        error_code="HF-VALIDATION-008",
    )


def test_invalid_directory_name(
    enforce_hfdir_structure: EnforceHFDirStructure,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Non snake_case directory names should fail validation."""

    assert_validation_raises(
        enforce_hfdir_structure,
        make_validation_context("invalid_directory_name"),
        error_code="HF-VALIDATION-012",
    )


def test_leaf_without_yml(
    enforce_hfdir_structure: EnforceHFDirStructure,
    make_validation_context: Callable[[str], ConfigurationContext],
    assert_validation_raises: Callable[..., None],
) -> None:
    """Leaf directories without YAML files should fail validation."""

    assert_validation_raises(
        enforce_hfdir_structure,
        make_validation_context("leaf_without_yml"),
        error_code="HF-VALIDATION-011",
    )
