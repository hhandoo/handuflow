from pyspark.sql import SparkSession
# from handuflow import SystemConfigurator
# from handuflow import ValidationRunner
from handuflow import Orchestrator

spark = SparkSession.builder.appName("Spark Test").master("local[*]").getOrCreate()

# my_configurator = SystemConfigurator(r"C:\Users\hando\PycharmProjects\handuflow\sandbox\handuflow_dir", spark)
# my_configurator.configure()
# context = my_configurator.get_configuration_context()
#
#
# my_validationRunner = ValidationRunner(context)
#
# results = my_validationRunner.run()
#
#
#
# for r in results:
#     print(r)



orchestrator = Orchestrator(spark, r"C:\Users\hando\PycharmProjects\handuflow\sandbox\handuflow_dir")

orchestrator.run()