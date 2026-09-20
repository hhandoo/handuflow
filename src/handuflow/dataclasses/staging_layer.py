from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StagingLayerConfiguration:
    catalog: str | None
    namespace: tuple[str, ...]
    table_prefix: str
    table_suffix: str
    format: str

    @property
    def staging_layer_namespace(self) -> str:
        """Return the fully qualified staging namespace identifier."""

        parts: tuple[str, ...] = ()

        if self.catalog is not None:
            parts += (self.catalog,)

        parts += self.namespace
        return ".".join(f"`{part}`" for part in parts)

    def get_table_identifier(
        self,
        current_table_schema_str: str,
        current_table_name: str,
    ) -> str:
        """Return the fully qualified staging table identifier."""

        table_name = (
            f"{self.staging_layer_namespace}."
            f"`{self.table_prefix}"
            f"{current_table_schema_str}__"
            f"{current_table_name}"
            f"{self.table_suffix}`"
        )

        return table_name
