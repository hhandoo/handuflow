import os

# os.environ["HADOOP_HOME"] = r"C:\hadoop-3.3.6"
# os.environ["PATH"] = r"C:\hadoop-3.3.6\bin;" + os.environ["PATH"]


from pyspark.sql import SparkSession
from pyspark.sql import Row

# from handuflow import SystemConfigurator
# from handuflow import ValidationRunner
from handuflow import Orchestrator

spark = (
    SparkSession.builder.appName("Spark Test")
    .master("local[*]")
    .enableHiveSupport()
    .getOrCreate()
)
print(spark.conf.get("spark.sql.warehouse.dir"))
spark.sql("CREATE DATABASE IF NOT EXISTS demo")
spark.sql("USE demo")
spark.sql("""
CREATE TABLE IF NOT EXISTS employee (
    id INT,
    name STRING,
    age INT,
    salary DOUBLE,
    event_ts STRING
)
""")


rows = [
    Row(
        id=1,
        name="Alice",
        age=25,
        salary=55000.0,
        event_ts="2026-06-30 23:59:59.999+05:30",  # ❌ before range
    ),
    Row(
        id=2,
        name="Bob",
        age=31,
        salary=62000.0,
        event_ts="2026-07-01 00:00:00.000+05:30",  # ✅ lower bound (inclusive)
    ),
    Row(
        id=3,
        name="Charlie",
        age=28,
        salary=58000.0,
        event_ts="2026-07-05 10:15:30.123+05:30",  # ✅
    ),
    Row(
        id=4,
        name="David",
        age=35,
        salary=71000.0,
        event_ts="2026-07-10 18:45:12.456+05:30",  # ✅
    ),
    Row(
        id=5,
        name="Emma",
        age=None,
        salary=54000.0,
        event_ts="2026-07-15 12:00:00.789+05:30",  # ✅
    ),
    Row(
        id=6,
        name="Frank",
        age=40,
        salary=85000.0,
        event_ts="2026-07-20 23:59:59.999+05:30",  # ✅
    ),
    Row(
        id=7,
        name="Grace",
        age=29,
        salary=60000.0,
        event_ts="2026-07-30 23:59:59.999+05:30",  # ✅ last valid value
    ),
    Row(
        id=9,
        name="Ivy",
        age=10,
        salary=52000.0,
        event_ts="2026-08-01 00:00:00.000+05:30",  # ❌ after range
    ),
    Row(
        id=10,
        name="Jack",
        age=11,
        salary=79000.0,
        event_ts=None,  # ❌ null
    ),
]
df = spark.createDataFrame(rows)
df.show(truncate=False)

df.write.mode("append").insertInto("demo.employee", overwrite=True)


# my_configurator = SystemConfigurator(r"C:\Users\hando\PycharmProjects\handuflow\sandbox\handuflow_dir", spark)
# my_configurator.configure()
# context = my_configurator.get_configuration_context()
# my_validationRunner = ValidationRunner(context)
# results = my_validationRunner.run()
# for r in results:
#     print(r)

# orchestrator = Orchestrator(spark, r"C:\Users\hando\PycharmProjects\handuflow\sandbox\handuflow_dir")

dir_path = os.path.dirname(__file__)
orchestrator = Orchestrator(spark, os.path.join(dir_path, "handuflow_dir"))

orchestrator.run()
