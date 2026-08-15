"""Pytest fixtures for HanduFLOW validation contract tests."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from pathlib import Path

import pytest
from pyspark.sql import SparkSession

from handuflow.platform.configurator.dataclasses.context import ConfigurationContext
from handuflow.platform.configurator.dataclasses.default import DefaultConfiguration
from handuflow.platform.configurator.dataclasses.logging import LoggingConfiguration
from handuflow.platform.configurator.dataclasses.spark import SparkConfiguration
from handuflow.platform.exceptions.domains.validation import ValidationError
from handuflow.platform.storage import StorageManager, StoragePath
from handuflow.platform.storage.providers.local import LocalStorageProvider
from handuflow.platform.validation.base import Validation
from handuflow.platform.validation.validation_runner import ValidationRunner
from handuflow.platform.validation.validations import VALIDATIONS
from handuflow.platform.validation.validations.enforce_HFdir_structure import (
    EnforceHFDirStructure,
)
from handuflow.platform.validation.validations.enforce_data_quality_checks import (
    EnforceDataQualityChecks,
)
from handuflow.platform.validation.validations.enforce_feed_meta import EnforceFeedMeta
from handuflow.platform.validation.validations.enforce_feed_specs import EnforceFeedSpecs
from handuflow.platform.validation.validations.enforce_load_details import (
    EnforceLoadDetails,
)
from handuflow.platform.validation.validations.enforce_master_config import (
    EnforceMasterConfig,
)
from handuflow.platform.validation.validations.enforce_source_and_target import (
    EnforceSourceAndTarget,
)

TEST_ROOT = Path(__file__).resolve().parents[3]
VALIDATION_FIXTURES_ROOT = TEST_ROOT / "validation_handuflow_dirs"
POSITIVE_HANDUFLOW_DIR = VALIDATION_FIXTURES_ROOT / "positive"
NEGATIVE_HANDUFLOW_DIR = VALIDATION_FIXTURES_ROOT / "negative"


def build_validation_test_context(
    handuflow_dir: Path,
    spark: SparkSession,
) -> ConfigurationContext:
    """Build a configuration context for validation contract tests."""

    storage_manager = StorageManager()
    storage_manager.set_provider(LocalStorageProvider())

    logger = logging.getLogger(f"validation-test-{handuflow_dir.name}")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return ConfigurationContext(
        run_id=str(uuid.uuid4()),
        default=DefaultConfiguration(
            system_name="HanduFLOWTEST",
            environment="local",
        ),
        logging=LoggingConfiguration(
            type="standard",
            log_format="%(message)s",
            log_directory_name="logs",
            log_file_name="hf_log",
            backup_count=5,
            max_bytes=1048576,
            default_log_level=10,
            log_retention_days=7,
            logger=logger,
        ),
        storage_path=StoragePath(str(handuflow_dir.resolve())),
        storage_manager=storage_manager,
        spark_config=SparkConfiguration(spark=spark),
        list_of_feed_ymls=[],
    )


@pytest.fixture(scope="session")
def positive_handuflow_dir() -> Path:
    """Return the positive validation fixture directory."""

    return POSITIVE_HANDUFLOW_DIR


@pytest.fixture(scope="session")
def negative_handuflow_dir() -> Path:
    """Return the root directory for negative validation fixtures."""

    return NEGATIVE_HANDUFLOW_DIR


@pytest.fixture(scope="session")
def positive_configuration_context(
    spark: SparkSession,
    positive_handuflow_dir: Path,
) -> ConfigurationContext:
    """Return a configured context for the positive HanduFLOW directory."""

    return build_validation_test_context(positive_handuflow_dir, spark)


@pytest.fixture
def make_validation_context(
    spark: SparkSession,
    negative_handuflow_dir: Path,
) -> Callable[[str], ConfigurationContext]:
    """Build a configuration context for a named negative fixture."""

    def _factory(scenario: str) -> ConfigurationContext:
        return build_validation_test_context(
            negative_handuflow_dir / scenario,
            spark,
        )

    return _factory


@pytest.fixture
def validation_runner(
    positive_configuration_context: ConfigurationContext,
) -> ValidationRunner:
    """Return a validation runner bound to the positive fixture."""

    return ValidationRunner(positive_configuration_context)


@pytest.fixture(
    params=VALIDATIONS,
    ids=lambda validation: validation.name,
)
def validation_rule(request: pytest.FixtureRequest) -> Validation:
    """Yield each registered validation rule."""

    return request.param


@pytest.fixture
def enforce_hfdir_structure() -> EnforceHFDirStructure:
    return EnforceHFDirStructure()


@pytest.fixture
def enforce_master_config() -> EnforceMasterConfig:
    return EnforceMasterConfig()


@pytest.fixture
def enforce_feed_meta() -> EnforceFeedMeta:
    return EnforceFeedMeta()


@pytest.fixture
def enforce_load_details() -> EnforceLoadDetails:
    return EnforceLoadDetails()


@pytest.fixture
def enforce_source_and_target() -> EnforceSourceAndTarget:
    return EnforceSourceAndTarget()


@pytest.fixture
def enforce_feed_specs() -> EnforceFeedSpecs:
    return EnforceFeedSpecs()


@pytest.fixture
def enforce_data_quality_checks() -> EnforceDataQualityChecks:
    return EnforceDataQualityChecks()


@pytest.fixture
def assert_validation_passes() -> Callable[..., None]:
    """Return a helper that asserts a validation rule completes successfully."""

    def _assert(
        validation: Validation,
        configuration_context: ConfigurationContext,
    ) -> None:
        result = validation.validate(configuration_context)

        assert result.passed is True
        assert result.validation_key == validation.key
        assert result.validation_name == validation.name

    return _assert


@pytest.fixture
def assert_validation_raises() -> Callable[..., None]:
    """Return a helper that asserts a validation rule raises ValidationError."""

    def _assert(
        validation: Validation,
        configuration_context: ConfigurationContext,
        *,
        error_code: str,
    ) -> None:
        with pytest.raises(ValidationError) as exc_info:
            validation.validate(configuration_context)

        assert exc_info.value.code == error_code

    return _assert
