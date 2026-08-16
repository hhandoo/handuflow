"""Incremental CDC load strategy."""

from __future__ import annotations

from typing import Any

from .base import LoadStrategy


class IncrementalCDCStrategy(LoadStrategy):
    """Strategy for processing incremental CDC data."""

    def execute(
        self,
        source: Any,
        target: Any,
        **kwargs: Any,
    ) -> Any:
        """Apply incremental CDC changes to the target."""
        raise NotImplementedError
