from __future__ import annotations

from dataclasses import dataclass

from .check import CheckDC


@dataclass
class CheckObj:
    full_table_path: str
    table_path: str
    check_identifier: str
    run_type: str
    check_type: str
    dependency_datasets: list[str]
    column: str
    checks: list[CheckDC]
    threshold: float | None = None
    sql_query: str | None = None

    def __str__(self) -> str:
        checks = (
            "\n".join(f"    {check}" for check in self.checks)
            if self.checks
            else "    <none>"
        )

        return (
            f"\n"
            f"  full_table_path     = {self.full_table_path}\n"
            f"  table_path          = {self.table_path}\n"
            f"  check_identifier    = {self.check_identifier}\n"
            f"  run_type            = {self.run_type}\n"
            f"  check_type          = {self.check_type}\n"
            f"  column              = {self.column}\n"
            f"  dependency_datasets = {self.dependency_datasets}\n"
            f"  threshold           = {self.threshold}\n"
            f"  sql_query           = {self.sql_query}\n"
            f"  checks:\n"
            f"{checks}\n"
        )