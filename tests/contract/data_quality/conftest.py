"""Global pytest configuration."""

from __future__ import annotations
import pytest
from handuflow.platform.configurator.dataclasses.context import ConfigurationContext
from handuflow.data_quality.manager import DataQualityManager
from handuflow.data_quality.dataclass.result import CheckResult
from pyspark.sql import SparkSession
from pyspark.sql import Row


@pytest.fixture(scope="session")
def results(
    configuration_context: ConfigurationContext,
    spark: SparkSession,
) -> list[CheckResult]:

    ######################################## NULL CHECK ######################################
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

    # table 2
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

    # table 3

    spark.sql(""" CREATE TABLE IF NOT EXISTS employee2 (event_ts STRING)""")  # type: ignore
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
        Row(event_ts=None),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee2", overwrite=True)

    # table 4

    spark.sql(""" CREATE TABLE IF NOT EXISTS employee3 (event_ts STRING)""")  # type: ignore
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
        Row(event_ts=None),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee3", overwrite=True)

    ################################################################################################

    ######################################## DUPLICATE CHECK ########################################
    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee4 (event_ts STRING)""")  # type: ignore
    rows = [
        Row(event_ts="2026-06-30 23:59:59.999+05:30"),
        Row(event_ts="2026-07-01 00:01:00.000+05:30"),
        Row(event_ts="2026-07-05 10:15:30.123+05:30"),
        Row(event_ts="2026-07-10 18:45:12.456+05:30"),
        Row(event_ts="2026-07-15 12:01:10.789+05:30"),
        Row(event_ts="2026-07-20 23:59:59.999+05:30"),
        Row(event_ts="2026-07-30 23:59:59.999+05:30"),
        Row(event_ts="2026-08-01 00:00:00.000+05:30"),
        Row(event_ts="2026-08-01 00:00:00.000+05:30"),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee4", overwrite=True)

    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee5 (event_ts STRING)""")  # type: ignore
    rows = [
        Row(event_ts="2026-06-30 23:59:59.999+05:30"),
        Row(event_ts="2026-07-01 00:01:00.000+05:30"),
        Row(event_ts="2026-07-05 10:15:30.123+05:30"),
        Row(event_ts="2026-07-10 18:45:12.456+05:30"),
        Row(event_ts="2026-07-15 12:01:10.789+05:30"),
        Row(event_ts="2026-07-20 23:59:59.999+05:30"),
        Row(event_ts="2026-07-30 23:59:59.999+05:30"),
        Row(event_ts="2026-08-01 00:00:00.000+05:30"),
        Row(event_ts="2026-08-01 00:10:00.000+05:30"),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee5", overwrite=True)

    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee6 (event_ts STRING)""")  # type: ignore
    rows = [
        Row(event_ts="2026-06-30 23:59:59.999+05:30"),
        Row(event_ts="2026-07-01 00:01:00.000+05:30"),
        Row(event_ts="2026-07-05 10:15:30.123+05:30"),
        Row(event_ts="2026-07-10 18:45:12.456+05:30"),
        Row(event_ts="2026-07-15 12:01:10.789+05:30"),
        Row(event_ts="2026-07-20 23:59:59.999+05:30"),
        Row(event_ts="2026-07-30 23:59:59.999+05:30"),
        Row(event_ts="2026-08-01 00:00:00.000+05:30"),
        Row(event_ts="2026-08-01 00:10:00.000+05:30"),
        Row(event_ts="2026-08-01 00:10:00.000+05:30"),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee6", overwrite=True)

    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee7 (event_ts STRING)""")  # type: ignore
    rows = [
        Row(event_ts="2026-06-30 23:59:59.999+05:30"),
        Row(event_ts="2026-07-01 00:01:00.000+05:30"),
        Row(event_ts="2026-07-05 10:15:30.123+05:30"),
        Row(event_ts="2026-07-10 18:45:12.456+05:30"),
        Row(event_ts="2026-07-15 12:01:10.789+05:30"),
        Row(event_ts="2026-07-20 23:59:59.999+05:30"),
        Row(event_ts="2026-08-01 00:00:10.000+05:30"),
        Row(event_ts="2026-08-01 00:01:00.000+05:30"),
        Row(event_ts="2026-08-01 00:10:01.000+05:30"),
        Row(event_ts="2026-08-01 00:10:10.000+05:30"),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee7", overwrite=True)

    #################################################################################################

    ##################################Not blank check ###############################################

    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee8 (event_ts STRING)""")  # type: ignore
    rows = [
        Row(event_ts="2026-06-30 23:59:59.999+05:30"),
        Row(event_ts="2026-07-01 00:01:00.000+05:30"),
        Row(event_ts="2026-07-05 10:15:30.123+05:30"),
        Row(event_ts="2026-07-10 18:45:12.456+05:30"),
        Row(event_ts="2026-07-15 12:01:10.789+05:30"),
        Row(event_ts="2026-07-20 23:59:59.999+05:30"),
        Row(event_ts="2026-07-25 09:30:00.000+05:30"),
        Row(event_ts="2026-07-30 23:59:59.999+05:30"),
        Row(event_ts="2026-08-01 00:00:00.000+05:30"),
        Row(event_ts="2026-08-01 00:10:00.000+05:30"),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee8", overwrite=True)

    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee9 (event_ts STRING)""")  # type: ignore
    rows = [
        Row(event_ts="2026-06-30 23:59:59.999+05:30"),
        Row(event_ts="2026-07-01 00:01:00.000+05:30"),
        Row(event_ts="2026-07-05 10:15:30.123+05:30"),
        Row(event_ts="2026-07-10 18:45:12.456+05:30"),
        Row(event_ts=""),
        Row(event_ts="2026-07-20 23:59:59.999+05:30"),
        Row(event_ts="2026-07-25 09:30:00.000+05:30"),
        Row(event_ts="2026-07-30 23:59:59.999+05:30"),
        Row(event_ts="2026-08-01 00:00:00.000+05:30"),
        Row(event_ts="2026-08-01 00:10:00.000+05:30"),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee9", overwrite=True)

    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee10 (event_ts STRING)""")  # type: ignore
    rows = [
        Row(event_ts="2026-06-30 23:59:59.999+05:30"),
        Row(event_ts="2026-07-01 00:01:00.000+05:30"),
        Row(event_ts="2026-07-05 10:15:30.123+05:30"),
        Row(event_ts="2026-07-10 18:45:12.456+05:30"),
        Row(event_ts="2026-07-15 12:01:10.789+05:30"),
        Row(event_ts="2026-07-20 23:59:59.999+05:30"),
        Row(event_ts="2026-07-25 09:30:00.000+05:30"),
        Row(event_ts="2026-07-30 23:59:59.999+05:30"),
        Row(event_ts="2026-08-01 00:00:00.000+05:30"),
        Row(event_ts=""),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee10", overwrite=True)

    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee11 (event_ts STRING)""")  # type: ignore
    rows = [
        Row(event_ts="2026-06-30 23:59:59.999+05:30"),
        Row(event_ts="2026-07-01 00:01:00.000+05:30"),
        Row(event_ts="2026-07-05 10:15:30.123+05:30"),
        Row(event_ts="2026-07-10 18:45:12.456+05:30"),
        Row(event_ts=""),
        Row(event_ts="2026-07-20 23:59:59.999+05:30"),
        Row(event_ts="2026-07-25 09:30:00.000+05:30"),
        Row(event_ts="2026-07-30 23:59:59.999+05:30"),
        Row(event_ts=""),
        Row(event_ts="2026-08-01 00:10:00.000+05:30"),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee11", overwrite=True)

    #########################################################################################################

    ##################################Range check ###############################################

    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee12 (event_ts STRING, age INT, name STRING, salary DOUBLE)""")  # type: ignore
    rows = [
        Row(event_ts="2026-07-01 00:00:00.000+05:30", age=10, name="john", salary=1.0),
        Row(
            event_ts="2026-07-02 00:00:00.000+05:30", age=20, name="john1", salary=10.0
        ),
        Row(
            event_ts="2026-07-03 00:00:00.000+05:30",
            age=30,
            name="john11",
            salary=100.0,
        ),
        Row(
            event_ts="2026-07-04 00:00:00.000+05:30",
            age=40,
            name="john111",
            salary=1000.0,
        ),
        Row(
            event_ts="2026-07-05 00:00:00.000+05:30",
            age=50,
            name="john2",
            salary=2000.0,
        ),
        Row(
            event_ts="2026-07-06 00:00:00.000+05:30",
            age=60,
            name="john22",
            salary=5000.0,
        ),
        Row(
            event_ts="2026-07-07 00:00:00.000+05:30",
            age=70,
            name="john3",
            salary=10000.0,
        ),
        Row(
            event_ts="2026-07-08 00:00:00.000+05:30",
            age=80,
            name="john33",
            salary=20000.0,
        ),
        Row(
            event_ts="2026-07-09 00:00:00.000+05:30",
            age=90,
            name="john4",
            salary=50000.0,
        ),
        Row(
            event_ts="2026-07-31 23:59:59.999+05:30",
            age=99,
            name="johnzzz",
            salary=99999.0,
        ),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee12", overwrite=True)

    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee13 (event_ts STRING, age INT, name STRING, salary DOUBLE)""")  # type: ignore
    rows = [
        # event_ts fails
        Row(
            event_ts="2026-08-01 00:00:00.000+05:30", age=20, name="john1", salary=10.0
        ),
        # age fails
        Row(
            event_ts="2026-07-02 00:00:00.000+05:30", age=100, name="john2", salary=20.0
        ),
        # name fails
        Row(event_ts="2026-07-03 00:00:00.000+05:30", age=30, name="kate", salary=30.0),
        # salary fails
        Row(
            event_ts="2026-07-04 00:00:00.000+05:30",
            age=40,
            name="john3",
            salary=100000.0,
        ),
        Row(
            event_ts="2026-07-05 00:00:00.000+05:30", age=50, name="john4", salary=40.0
        ),
        Row(
            event_ts="2026-07-06 00:00:00.000+05:30", age=60, name="john5", salary=50.0
        ),
        Row(
            event_ts="2026-07-07 00:00:00.000+05:30", age=70, name="john6", salary=60.0
        ),
        Row(
            event_ts="2026-07-08 00:00:00.000+05:30", age=80, name="john7", salary=70.0
        ),
        Row(
            event_ts="2026-07-09 00:00:00.000+05:30", age=90, name="john8", salary=80.0
        ),
        Row(
            event_ts="2026-07-31 23:59:59.999+05:30", age=99, name="john9", salary=90.0
        ),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee13", overwrite=True)

    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee14 (event_ts STRING, age INT, name STRING, salary DOUBLE)""")  # type: ignore
    rows = [
        # event_ts failures
        Row(
            event_ts="2026-06-30 23:59:59.999+05:30", age=20, name="john1", salary=10.0
        ),
        Row(
            event_ts="2026-08-01 00:00:00.000+05:30", age=30, name="john2", salary=20.0
        ),
        # age failures
        Row(event_ts="2026-07-03 00:00:00.000+05:30", age=9, name="john3", salary=30.0),
        Row(
            event_ts="2026-07-04 00:00:00.000+05:30", age=100, name="john4", salary=40.0
        ),
        # name failures
        Row(event_ts="2026-07-05 00:00:00.000+05:30", age=50, name="adam", salary=50.0),
        Row(event_ts="2026-07-06 00:00:00.000+05:30", age=60, name="kate", salary=60.0),
        # salary failures
        Row(event_ts="2026-07-07 00:00:00.000+05:30", age=70, name="john5", salary=0.5),
        Row(
            event_ts="2026-07-08 00:00:00.000+05:30",
            age=80,
            name="john6",
            salary=100000.0,
        ),
        # passing rows
        Row(
            event_ts="2026-07-09 00:00:00.000+05:30", age=90, name="john7", salary=70.0
        ),
        Row(
            event_ts="2026-07-31 23:59:59.999+05:30", age=99, name="john8", salary=80.0
        ),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee14", overwrite=True)

    spark.sql("CREATE DATABASE IF NOT EXISTS demo")  # type: ignore
    spark.sql("USE demo")  # type: ignore
    spark.sql(""" CREATE TABLE IF NOT EXISTS employee15 (event_ts STRING, age INT, name STRING, salary DOUBLE)""")  # type: ignore
    rows = [
        Row(
            event_ts="2026-08-01 00:00:00.000+05:30", age=20, name="john1", salary=10.0
        ),
        Row(
            event_ts="2026-07-02 00:00:00.000+05:30", age=100, name="john2", salary=20.0
        ),
        Row(event_ts="2026-07-03 00:00:00.000+05:30", age=30, name="kate", salary=30.0),
        Row(
            event_ts="2026-07-04 00:00:00.000+05:30",
            age=40,
            name="john3",
            salary=100000.0,
        ),
        Row(
            event_ts="2026-07-05 00:00:00.000+05:30", age=50, name="john4", salary=40.0
        ),
        Row(
            event_ts="2026-07-06 00:00:00.000+05:30", age=60, name="john5", salary=50.0
        ),
        Row(
            event_ts="2026-07-07 00:00:00.000+05:30", age=70, name="john6", salary=60.0
        ),
        Row(
            event_ts="2026-07-08 00:00:00.000+05:30", age=80, name="john7", salary=70.0
        ),
        Row(
            event_ts="2026-07-09 00:00:00.000+05:30", age=90, name="john8", salary=80.0
        ),
        Row(
            event_ts="2026-07-31 23:59:59.999+05:30", age=99, name="john9", salary=90.0
        ),
    ]
    df = spark.createDataFrame(rows)  # type: ignore
    df.show(truncate=False)
    df.write.mode("append").insertInto("demo.employee15", overwrite=True)

    #########################################################################################################

    manager = DataQualityManager(configuration_context)
    results: list[CheckResult] = manager.run("PRE_LOAD")
    return results
