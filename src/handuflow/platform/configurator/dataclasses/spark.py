
from dataclasses import dataclass
from pyspark.sql import SparkSession


@dataclass(frozen=True, slots=True)
class SparkConfiguration:

    spark: SparkSession