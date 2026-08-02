# models/result.py

from dataclasses import dataclass


@dataclass
class CheckResult:
    check_group_identifier: str
    description: str
    run_type: str
    check_name: str
    column: str
    table_name: str
    total_rows: int
    passed_rows: int
    failed_rows: int
    pass_pct: float
    fail_pct: float
    threshold_pct: float
    is_passed: bool
