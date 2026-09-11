"""Load manifest definitions for HanduFLOW."""

from __future__ import annotations

from dataclasses import dataclass, field
from .optimize_command import OptimizeCommand
from .custom_selection import CustomSelection
from .enforce_schema import EnforceSchema


@dataclass(slots=True)
class FeedSpecs:
    """Feed-specific loading specifications."""

    primary_key: str | None = None
    composite_key: list[str] = field(default_factory=list)
    partition_columns: list[str] = field(default_factory=list)

    optimize_command: OptimizeCommand | None = None

    custom_selection: CustomSelection | None = None

    enforce_schema: EnforceSchema | None = None
