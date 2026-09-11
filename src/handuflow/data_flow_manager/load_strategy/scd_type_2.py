"""SCD Type 2 load strategy."""

from __future__ import annotations

from typing import Any

from .base import LoadStrategy


class SCDType2Strategy(LoadStrategy):
    """Strategy for implementing SCD Type 2."""

    def execute(
        self,
        source: Any,
        target: Any,
        **kwargs: Any,
    ) -> Any:
        """Apply SCD Type 2 changes to the target."""
        raise NotImplementedError
