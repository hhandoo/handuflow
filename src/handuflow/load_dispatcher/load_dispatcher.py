"""Load strategy dispatcher."""

from __future__ import annotations

from datetime import datetime

from .load_strategy.base import LoadStrategy
from .load_strategy import STRATEGIES
from .dataclass.load_manifest import LoadManifest
from .dataclass.load_result import LoadResult


class LoadDispatcher:
    """Dispatches loads to the appropriate load strategy."""

    def __init__(self) -> None:
        """Initialize the load strategy registry."""
        self._strategies: dict[str, LoadStrategy] = STRATEGIES

    def register(
        self,
        load_type: str,
        strategy: LoadStrategy,
    ) -> None:
        """Register a load strategy if it is not already registered."""
        self._strategies.setdefault(load_type, strategy)

    def dispatch(self, load_manifest: LoadManifest) -> LoadResult:

        return LoadResult(
            True, "asd", datetime.now(), datetime.now(), 1, 1, 1, 1, 0, error_message=""
        )
