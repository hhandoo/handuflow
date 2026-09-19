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
            .withColumn("__x_load_type", F.lit("FULL_LOAD"))
            .withColumn("__x_ingestion_date", F.current_timestamp())
        )

    def _build_staging_layer(self):
        super()._build_staging_layer()
        staging_table_name = self.transfer_config.staging_layer_identifier
        raw_incoming_df = self.transfer_config.source_data_frame
        decorated_incoming_df = self.add_staging_metadata(
            df=raw_incoming_df, run_id=self.configuration_context.run_id
        )

        self.spark_session.sql(f"DROP TABLE IF EXISTS {staging_table_name};")
        print(staging_table_name)

        decorated_incoming_df.show(truncate=False)
        decorated_incoming_df.write.format("delta").mode("overwrite").saveAsTable(
            staging_table_name
        )

    def execute(self) -> Any:
        """Replace the target with the source dataset."""
        self._build_staging_layer()
