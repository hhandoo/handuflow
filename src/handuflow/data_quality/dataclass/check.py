from dataclasses import dataclass


@dataclass
class CheckDC:
    name: str
    check_range: dict[str, int | float | str] | None = None
    spark_timestamp_format: str | None = None
    sql_query_pass: str | None = None
    sql_query_fail: str | None = None
    threshold: float | None = None

    def __str__(self) -> str:
        return (
            f"\n\n"
            f"name                          = {self.name}\n"
            f"check_range                   = {self.check_range}\n"
            f"spark_timestamp_format        = {self.spark_timestamp_format}\n"
            f"sql_query_pass                = {self.sql_query_pass}\n"
            f"sql_query_fail                = {self.sql_query_fail}\n"
            f"threshold                     = {self.threshold}\n"
        )
