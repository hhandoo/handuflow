"""Append load strategy."""

from __future__ import annotations

from typing import Any

from .base import LoadStrategy


class AppendLoadStrategy(LoadStrategy):
    """Strategy for appending data to the target."""

    def execute(
        self,
        source: Any,
        target: Any,
        **kwargs: Any,
    ) -> Any:
        """Append source records to the target."""
        raise NotImplementedError
