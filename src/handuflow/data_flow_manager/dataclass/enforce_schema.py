from __future__ import annotations

from dataclasses import dataclass, field
from .schema_field import SchemaField


@dataclass(slots=True)
class EnforceSchema:
    """Schema enforcement configuration."""

    type: str
    fields: list[SchemaField] = field(default_factory=lambda: list[SchemaField]())
