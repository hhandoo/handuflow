"""Load manifest definitions for HanduFLOW."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Address:
    type: str
    format: str
    schema: str
    table: str

    @property
    def table_identifier(self) -> str:
        """Return the fully qualified table identifier."""

        if self.type == "hive_metastore":
            return f"`{self.schema}`.`{self.table}`"

        return f"`{self.type}`.`{self.schema}`.`{self.table}`"
