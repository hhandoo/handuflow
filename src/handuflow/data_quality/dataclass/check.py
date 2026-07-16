from dataclasses import dataclass


@dataclass
class CheckDC:
    name: str
    check_range: range = None
