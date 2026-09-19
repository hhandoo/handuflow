"""Load manifest definitions for HanduFLOW."""

from __future__ import annotations

from dataclasses import dataclass
from pyspark.sql import DataFrame


@dataclass(slots=True)
class TransferConfig:
    source_data_frame: DataFrame
    staging_layer_identifier: str
    is_source_changed: bool
