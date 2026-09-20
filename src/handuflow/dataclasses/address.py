"""Load manifest definitions for HanduFLOW."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Address:
    catalog: str | None
    namespace: tuple[str, ...]
    name: str
    format: str

    @property
    def identifier_names(self) -> tuple[str, ...]:
        """Return the individual names of the fully qualified identifier."""

        names: tuple[str, ...] = ()

        if self.catalog is not None:
            names += (self.catalog,)

        names += self.namespace
        names += (self.name,)

        return names

    @property
    def namespace_str(self) -> str:
        """Return the namespace as a dot-separated string."""

        return "".join(
            character
            for part in self.namespace
            for character in part
            if character.isalnum()
        )

    @property
    def namespace_identifier(self) -> str:
        """Return the fully qualified table identifier."""
        return ".".join(f"`{part}`" for part in self.namespace)

    @property
    def table_identifier(self) -> str:
        """Return the fully qualified table identifier."""

        return ".".join(f"`{part}`" for part in self.identifier_names)
