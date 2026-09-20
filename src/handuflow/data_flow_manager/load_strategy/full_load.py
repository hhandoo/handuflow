"""Full load strategy."""

from __future__ import annotations

from typing import Any

from .base import LoadStrategy
from ..dataclass.load_manifest import LoadManifest
from ...platform.configurator import ConfigurationContext


from pyspark.sql import functions as F
from pyspark.sql import DataFrame


class FullLoadStrategy(LoadStrategy):
    """Strategy for performing a full load."""

    def __init__(
        self, load_manifest: LoadManifest, configuration_context: ConfigurationContext
    ) -> None:
        super().__init__(
            load_manifest=load_manifest, configuration_context=configuration_context
        )
        self.load_manifest = load_manifest
        self.transfer_config = self._generate_transfer_config(
            self.load_manifest.source_address, self.load_manifest.target_address
        )

        self.__load_type = "FULL_LOAD"

    def add_staging_metadata(self, df: DataFrame, run_id: str) -> DataFrame:
        """Add HanduFLOW enterprise staging metadata columns to a DataFrame."""

        return (
            df.withColumn("__x_run_id", F.lit(run_id))
            .withColumn(
                "__x_row_hash",
                F.sha2(
                    F.to_json(
                        F.struct(*[F.col(column_name) for column_name in df.columns])
                    ),
                    256,
                ),
            )
            .withColumn("__x_load_type", F.lit(self.__load_type))
            .withColumn("__x_ingestion_date", F.current_timestamp())
        )

    def _build_staging_layer(self) -> str:
        super()._build_staging_layer()
        staging_table_name = self.transfer_config.staging_layer_identifier
        raw_incoming_df = self.transfer_config.source_data_frame
        decorated_incoming_df = self.add_staging_metadata(
            df=raw_incoming_df, run_id=self.configuration_context.run_id
        )

        self.spark_session.sql(  # pyright: ignore[reportUnknownMemberType]
            f"DROP TABLE IF EXISTS {staging_table_name};"
        )
        decorated_incoming_df.write.format("delta").mode("overwrite").saveAsTable(
            staging_table_name
        )

        return staging_table_name

    def execute(self) -> Any:
        """Replace the target with the source dataset."""

        if self.transfer_config.is_source_changed:
            source_version = self._read_delta_version(self.load_manifest.source_address)
            incoming_table_name = self._build_staging_layer()
            target_table = self._target_prep()
            incoming_df = self.spark_session.table(incoming_table_name)

            incoming_df.write.format("delta").mode("overwrite").saveAsTable(
                target_table.table_identifier
            )

            self._set_table_property(
                target_table, "handuflow.sourceVersion", str(source_version)
            )
            self._set_table_property(
                target_table, "handuflow.loadType", self.__load_type
            )
        else:
            print("The source is unchanged")
