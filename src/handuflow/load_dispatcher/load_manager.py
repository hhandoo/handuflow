"""Centralized load manager."""

from __future__ import annotations

from .load_dispatcher import LoadDispatcher


class LoadManager:
    """Central entry point for load execution."""

    def __init__(
        self,
        dispatcher: LoadDispatcher | None = None,
    ) -> None:
        """Initialize the load manager."""
        self._dispatcher = dispatcher or LoadDispatcher()
