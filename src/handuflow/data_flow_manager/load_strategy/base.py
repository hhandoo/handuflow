"""Base class for HanduFLOW load strategies."""

from __future__ import annotations
from typing import Any
from abc import ABC, abstractmethod
from ..dataclass.load_manifest import LoadManifest
from ..dataclass.transfer_config import TransferConfig
from ..dataclass.load_result import LoadResult
from ...dataclasses.address import Address
from ..dataclass.enforce_schema import EnforceSchema
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType
from ...platform.configurator import ConfigurationContext
from delta.tables import DeltaTable


class LoadStrategy(ABC):
    """Abstract base class for all load strategies."""

    def __init__(
        self, load_manifest: LoadManifest, configuration_context: ConfigurationContext
    ) -> None:
        self.load_manifest = load_manifest
        self.configuration_context = configuration_context
        self.spark_session: SparkSession = configuration_context.spark_config.spark

    def _set_table_property(
        self,
        table: Address,
        key: str,
        value: str,
    ) -> bool:
        """Set a property on a Delta table if it exists."""

        if self._read_delta_version(table) == -1:
            return False

        self.spark_session.sql(  # pyright: ignore[reportUnknownMemberType]
            f""" 
            ALTER TABLE {table.table_identifier}
            SET TBLPROPERTIES (
                '{key}' = '{value}'
            )
            """
        )  # pyright: ignore[reportUnknownMemberType]

        return True

    def _get_table_property(
        self,
        table: Address,
        key: str,
    ) -> str | None:
        """Get a property from a Delta table if it exists."""

        if self._read_delta_version(table) == -1:
            return None

        properties_df = (
            self.spark_session.sql(  # pyright: ignore[reportUnknownMemberType]
                f"SHOW TBLPROPERTIES {table.table_identifier} ('{key}')"
            )
        )

        row = properties_df.first()

        if row is None:
            return None

        return str(row["value"])

    def _to_spark_schema_json(self, schema: EnforceSchema) -> dict[str, Any]:
        """Convert an EnforceSchema to Spark StructType JSON representation."""

        return {
            "type": schema.type,
            "fields": [
                {
                    "name": field.name,
                    "type": field.type,
                    "nullable": field.nullable,
                    "metadata": field.metadata,
                }
                for field in schema.fields
            ],
        }

    def _generate_source_data_frame(self) -> DataFrame:
        """Generate a DataFrame from the source address."""
        custom_selection = self.load_manifest.feed_specs.custom_selection
        if custom_selection is None or not custom_selection.enabled:
            return self.spark_session.table(
                self.load_manifest.source_address.table_identifier
            )

        sql_file = custom_selection.sql_file
        if sql_file is None:
            raise ValueError("Custom selection SQL file must be configured.")

        elif self.load_manifest.feed_specs.enforce_schema is not None:
            schema_json = self._to_spark_schema_json(
                self.load_manifest.feed_specs.enforce_schema
            )
            return self.spark_session.read.schema(
                StructType.fromJson(schema_json)
            ).table(self.load_manifest.source_address.table_identifier)

        return self.spark_session.table(
            self.load_manifest.source_address.table_identifier
        )

    def _detect_source_target_change(
        self,
        source_address: Address,
        target_address: Address,
    ) -> bool:
        """Detect if the source data has changed since the last load."""
        source_version = self._read_delta_version(source_address)

        target_version = self._get_table_property(
            target_address, "handuflow.sourceVersion"
        )

        if target_version is not None:
            return str(source_version) != target_version
        else:
            return True

    def _generate_transfer_config(
        self, source_address: Address, target_address: Address
    ) -> TransferConfig:
        """Perform any necessary activities before executing the load."""
        return TransferConfig(
            source_data_frame=self._generate_source_data_frame(),
            staging_layer_identifier=self.configuration_context.staging_layer.get_table_identifier(
                target_address.namespace_str,
                target_address.name,
            ),
            is_source_changed=self._detect_source_target_change(
                source_address, target_address
            ),
        )

    @abstractmethod
    def execute(self) -> LoadResult:
        raise NotImplementedError

    def _target_prep(self) -> Address:

        print(self.load_manifest.target_address.namespace_identifier)
        self.spark_session.sql(  # pyright: ignore[reportUnknownMemberType]
            f"CREATE SCHEMA IF NOT EXISTS {self.load_manifest.target_address.namespace_identifier};"
        )

        return self.load_manifest.target_address

    @abstractmethod
    def _build_staging_layer(self) -> str:
        self.spark_session.sql(  # pyright: ignore[reportUnknownMemberType]
            f"CREATE SCHEMA IF NOT EXISTS {self.configuration_context.staging_layer.staging_layer_namespace};"
        )

    def _enforce_vacuum_on_table(self, table_address: Address):
        """Enforce the configured Delta vacuum retention on the target dataset."""
        vacuum_hours = self.load_manifest.feed_meta.vacuum_hours
        table_identifier = table_address.table_identifier
        self.spark_session.sql(  # pyright: ignore[reportUnknownMemberType]
            sqlQuery=f"VACUUM {table_identifier} RETAIN {vacuum_hours} HOURS"
        )

    def _address_to_dataframe(self, table_address: Address) -> DataFrame:
        """Read source data from a catalog table."""
        table_identifier = table_address.table_identifier
        return self.spark_session.read.format(table_address.format).table(
            table_identifier
        )

    def _read_delta_version(self, table: Address) -> int:
        """Read the latest Delta table version."""

        if table.format.lower() != "delta":
            return -1

        try:
            delta_table = DeltaTable.forName(
                self.spark_session,
                table.table_identifier,
            )

            latest_version = delta_table.history(1).select("version").first()

            if latest_version is None:
                return -1

            return int(latest_version["version"])

        except Exception:
            return -1

    def _optimize_table(self, table: Address) -> None:
        """Optimize the target Delta table."""

        optimize_command = self.load_manifest.feed_specs.optimize_command

        if optimize_command is None or not optimize_command.enabled:
            return

        if table.format != "delta":
            raise ValueError(
                f"OPTIMIZE is only supported for Delta tables. "
                f"Got format={table.format!r}."
            )

        command = f"OPTIMIZE {table.table_identifier}"

        if optimize_command.where:
            conditions = [
                f"`{column}` = '{value}'"
                for condition in optimize_command.where
                for column, value in condition.items()
            ]

            command += f" WHERE {' AND '.join(conditions)}"

        if optimize_command.zorder_by:
            columns = ", ".join(f"`{column}`" for column in optimize_command.zorder_by)

            command += f" ZORDER BY ({columns})"

        self.spark_session.sql(command)  # pyright: ignore[reportUnknownMemberType]

    def _enforce_partitioning(self, table: Address) -> None:
        """Enforce the configured partitioning on a Delta table."""

        if table.format != "delta":
            raise ValueError(
                f"Partitioning is only supported for Delta tables. "
                f"Got format={table.format}."
            )
        requested_partition_columns = self.load_manifest.feed_specs.partition_columns
        if len(requested_partition_columns) != len(set(requested_partition_columns)):
            raise ValueError("Partition columns must be unique.")
        if any(not column.strip() for column in requested_partition_columns):
            raise ValueError("Partition columns must not contain empty column names.")

        table_identifier = table.table_identifier
        detail_df = self.spark_session.sql(  # pyright: ignore[reportUnknownMemberType]
            f"DESCRIBE DETAIL {table_identifier}"
        )
        detail = detail_df.select("partitionColumns").first()
        if detail is None:
            raise ValueError(
                f"Unable to retrieve table details for {table_identifier}."
            )
        current_partition_columns = list(detail["partitionColumns"])
        # No partitioning change is required.
        if current_partition_columns == requested_partition_columns:
            return
        # Build the PARTITIONED BY clause only when partitioning
        # has been requested. An empty list means unpartitioned.
        partition_clause = ""
        if requested_partition_columns:
            columns = ", ".join(f"`{column}`" for column in requested_partition_columns)
            partition_clause = f"PARTITIONED BY ({columns})"

        sql_str = f"""  
            CREATE OR REPLACE TABLE {table_identifier} 
            USING DELTA
            {partition_clause}
            AS
            SELECT *
            FROM {table_identifier}
            """

        self.spark_session.sql(sql_str)  # pyright: ignore[reportUnknownMemberType]
