from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CustomSelection:
    """Custom SQL selection configuration."""

    enabled: bool = False
    sql_file: str | None = None
