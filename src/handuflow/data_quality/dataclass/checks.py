# context.py

from dataclasses import dataclass
from .check import CheckDC

@dataclass
class Checks:
    check_identifier: str
    run_type: str
    check_type: str
    dependency_datasets: list
    column: str
    check: CheckDC
    threshold: float = None
    sql_query: str = None
