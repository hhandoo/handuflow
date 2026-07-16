# models/result.py

from dataclasses import dataclass
from typing import Any


@dataclass
class CheckResult:
    check_name: str
    status: str
    message: str
    details: Any = None