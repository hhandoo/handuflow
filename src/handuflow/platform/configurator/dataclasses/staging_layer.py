from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StagingLayerConfiguration:
    type: str
    schema: str
    table_prefix: str
    table_suffix: str
    format: str

    def get_table_identifier(
        self, current_table_schema: str, current_table_name: str
    ) -> str:
        """Return the fully qualified staging table identifier."""

        table_name = f"{self.table_prefix}{current_table_schema}__{current_table_name}{self.table_suffix}"

        if self.type == "hive_metastore":
            return f"`{self.schema}`.`{table_name}`"

        return f"`{self.type}`.`{self.schema}`.`{table_name}`"
