"""Load manifest definitions for HanduFLOW."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Address:
    type: str
    format: str
    schema: str
    table: str
