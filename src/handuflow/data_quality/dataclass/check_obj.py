from __future__ import annotations
from dataclasses import dataclass

from .check import CheckDC


@dataclass
class CheckObj:
    full_file_path: str
    feed_identifier: str
    full_table_path: str
    table_path: str
    check_group_identifier: str
    run_type: str
    dependency_datasets: list[str]
    column: str
    checks: list[CheckDC]
    threshold: float | None = None
    sql_query: str | None = None

    def __str__(self) -> str:

        check_list = ""
        idx = 1
        for check in self.checks:
            check_list += f"[{idx}] {check.name}\n"
            idx +=1


        return (
            f"\n"
            f"full_file_path            = {self.full_file_path}\n"
            f"feed_identifier           = {self.feed_identifier}\n"
            f"full_table_path           = {self.full_table_path}\n"
            f"table_path                = {self.table_path}\n"
            f"check_group_identifier    = {self.check_group_identifier}\n"
            f"run_type                  = {self.run_type}\n"
            f"column                    = {self.column}\n"
            f"dependency_datasets       = {self.dependency_datasets}\n"
            f"threshold                 = {self.threshold}\n"
            f"sql_query                 = {self.sql_query}\n"
            f"Checklist:\n"
            f"{check_list}\n"
        )