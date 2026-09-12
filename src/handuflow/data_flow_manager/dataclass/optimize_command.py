"""Load manifest definitions for HanduFLOW."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class OptimizeCommand:
    """Optimization configuration for a feed."""

    enabled: bool = False
    where: list[dict[str, str]] = field(default_factory=lambda: list[dict[str, str]]())
    zorder_by: list[str] = field(default_factory=lambda: list[str]())
