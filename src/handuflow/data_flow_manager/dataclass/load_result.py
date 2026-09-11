"""Load result definitions for HanduFLOW."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class LoadResult:
    """Standardized result returned by a load strategy."""

    success: bool

    load_type: str

    started_at: datetime
    completed_at: datetime

    records_read: int = 0
    records_written: int = 0
    records_updated: int = 0
    records_inserted: int = 0
    records_deleted: int = 0
    records_rejected: int = 0

    error_message: str | None = None

    @property
    def duration_seconds(self) -> float:
        """Return the total load execution duration in seconds."""
        return (self.completed_at - self.started_at).total_seconds()
