"""Full load strategy."""

from __future__ import annotations

from typing import Any

from .base import LoadStrategy


class FullLoadStrategy(LoadStrategy):
    """Strategy for performing a full load."""

    def execute(
        self,
        source: Any,
        target: Any,
        **kwargs: Any,
    ) -> Any:
        """Replace the target with the source dataset."""
        raise NotImplementedError
