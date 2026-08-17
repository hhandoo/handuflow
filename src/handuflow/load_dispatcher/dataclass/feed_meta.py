from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FeedMeta:
    unique_identifier: str
    vacuum_hours: int = 168
    upstream_identifier: str = ""
    downstream_identifier: str = ""
