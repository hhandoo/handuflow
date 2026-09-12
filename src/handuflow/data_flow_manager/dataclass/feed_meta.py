from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class FeedMeta:
    unique_identifier: str
    vacuum_hours: int = 168
    depends_on: list[str] = field(default_factory=lambda: list[str]())
    pipeline: str | None = None
