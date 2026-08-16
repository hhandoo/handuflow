"""Built-in HanduFLOW validation rules."""

from __future__ import annotations

from .base import LoadStrategy
from .append_load import AppendLoadStrategy
from .full_load import FullLoadStrategy
from .incremental_cdc import IncrementalCDCStrategy
from .scd_type_2 import SCDType2Strategy

STRATEGIES: dict[str, LoadStrategy] = {
    "APPEND_LOAD": AppendLoadStrategy(),
    "FULL_LOAD": FullLoadStrategy(),
    "INCREMENTAL_CDC": IncrementalCDCStrategy(),
    "SCD_TYPE_2": SCDType2Strategy(),
}

__all__ = ["STRATEGIES", "LoadStrategy"]
