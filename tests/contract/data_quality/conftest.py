"""Pytest fixtures for data quality contract tests."""

from __future__ import annotations
from collections.abc import Iterator

import pytest
from pyspark.sql import SparkSession
from pyspark.sql import Row
from _pytest.tmpdir import TempPathFactory
from pathlib import Path
from handuflow.platform.configurator import SystemConfigurator
from handuflow.platform.configurator.dataclasses.context import ConfigurationContext


@pytest.fixture(scope="session")
def spark(
    tmp_path_factory: TempPathFactory,
) -> Iterator[SparkSession]:
    root: Path = tmp_path_factory.mktemp("spark")

    warehouse: Path = root / "spark-warehouse"
    metastore: Path = root / "metastore_db"

    spark = (
        SparkSession.builder.master("local[2]")
        .appName("HanduFLOW Data Quality Tests")
        .enableHiveSupport()
        .config(
            "spark.sql.warehouse.dir",
            warehouse.as_uri(),
        )
        .config(
            "javax.jdo.option.ConnectionURL",
            f"jdbc:derby:;databaseName={metastore};create=true",
        )
        .config(
            "derby.system.home",
            str(root),
        )
        .getOrCreate()
    )

    yield spark

    spark.stop()


@pytest.fixture
def configuration_context(
    spark: SparkSession,
) -> ConfigurationContext:

    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee (event_ts STRING)""")  # type: ignore

    rows = [
        Row(event_ts="2026-06-30 23:59:59.999+05:30"),
        Row(event_ts="2026-07-01 00:00:00.000+05:30"),
        Row(event_ts="2026-07-05 10:15:30.123+05:30"),
        Row(event_ts="2026-07-10 18:45:12.456+05:30"),
        Row(event_ts="2026-07-15 12:00:00.789+05:30"),
        Row(event_ts="2026-07-20 23:59:59.999+05:30"),
        Row(event_ts="2026-07-30 23:59:59.999+05:30"),
        Row(event_ts="2026-08-01 00:00:00.000+05:30"),
        Row(event_ts=None),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)

    df.write.mode("append").insertInto("demo.employee", overwrite=True)

    spark.sql(""" CREATE TABLE IF NOT EXISTS employee1 (event_ts STRING)""")  # type: ignore

    rows = [
        Row(event_ts="2026-06-30 23:59:59.999+05:30"),
        Row(event_ts="2026-07-01 00:00:00.000+05:30"),
        Row(event_ts="2026-07-05 10:15:30.123+05:30"),
        Row(event_ts="2026-07-10 18:45:12.456+05:30"),
        Row(event_ts="2026-07-15 12:00:00.789+05:30"),
        Row(event_ts="2026-07-20 23:59:59.999+05:30"),
        Row(event_ts="2026-07-30 23:59:59.999+05:30"),
        Row(event_ts="2026-08-01 00:00:00.000+05:30"),
        Row(event_ts="2026-08-01 00:00:00.000+05:30"),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)

    df.write.mode("append").insertInto("demo.employee1", overwrite=True)

    TEST_HANDUFLOW_DIR = (
        Path(__file__).resolve().parents[2] / "test_handuflow_dir"  # tests/
    )

    configuration = SystemConfigurator(str(TEST_HANDUFLOW_DIR), spark)
    configuration.configure()
    return configuration.get_configuration_context()
