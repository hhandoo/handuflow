from __future__ import annotations

from dataclasses import dataclass
from .schema_field import SchemaField


@dataclass(slots=True)
class EnforceSchema:
    """Schema enforcement configuration."""

    type: str
    fields: list[SchemaField] = []
