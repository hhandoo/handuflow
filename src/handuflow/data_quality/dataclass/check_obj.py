# context.py

from dataclasses import dataclass
from .check import CheckDC

@dataclass
class CheckObj:
    full_table_path: str
    table_path: str
    check_identifier: str
    run_type: str
    check_type: str
    dependency_datasets: list
    column: str
    checks: list[CheckDC]
    threshold: float = None
    sql_query: str = None
