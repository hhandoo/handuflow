# models/result.py

from dataclasses import dataclass
from typing import Any


@dataclass
class CheckResult:
    unique_check_name: str
    table_name: str
    total_rows: int
    passed_rows: int
    failed_rows: int
    pass_pct: float
    fail_pct: float
    threshold: float
    is_passed: bool