from pyspark.sql import SparkSession
from handuflow import SystemConfigurator

spark = SparkSession.builder.appName("Spark Test").master("local[*]").getOrCreate()

my_configurator = SystemConfigurator(r"C:\Users\hando\PycharmProjects\handuflow\sandbox\handuflow_dir", spark)
my_configurator.configure()
context = my_configurator.get_configuration_context()



print(context)



