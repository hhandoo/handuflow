"""Load manifest definitions for HanduFLOW."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class SchemaField:
    """Schema definition for a feed field."""

    name: str
    type: str
    nullable: bool = True
    metadata: dict[Any, Any] = {}
