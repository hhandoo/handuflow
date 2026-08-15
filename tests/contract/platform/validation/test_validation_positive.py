"""Positive validation contract tests."""

from __future__ import annotations

from collections.abc import Callable

from handuflow.platform.configurator.dataclasses.context import ConfigurationContext
from handuflow.platform.validation.base import Validation
from handuflow.platform.validation.validation_runner import ValidationRunner


def test_validation_runner_passes_for_positive_handuflow_dir(
    validation_runner: ValidationRunner,
) -> None:
    """All registered validations should pass for the positive fixture directory."""

    results = validation_runner.run()

    assert len(results) == 7
    assert all(result.passed for result in results)


def test_each_validation_passes_for_positive_handuflow_dir(
    validation_rule: Validation,
    positive_configuration_context: ConfigurationContext,
    assert_validation_passes: Callable[..., None],
) -> None:
    """Each validation rule should pass independently on the positive fixture."""

    assert_validation_passes(validation_rule, positive_configuration_context)
