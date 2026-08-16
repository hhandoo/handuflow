"""Base class for HanduFLOW load strategies."""

from __future__ import annotations

from typing import Any
from abc import ABC, abstractmethod


class LoadStrategy(ABC):
    """Abstract base class for all load strategies."""

    @abstractmethod
    def execute(
        self,
        source: Any,
        target: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute the load strategy.

        Args:
            source: Source dataset.
            target: Target dataset.
            **kwargs: Strategy-specific configuration.

        Returns:
            Result of the load operation.
        """
        raise NotImplementedError
