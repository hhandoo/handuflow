"""Load execution exceptions."""

from __future__ import annotations

from .dataclass.feed_load_result import FeedLoadResult


class LoadExecutionError(Exception):
    """Raised when a load wave fails and later waves must not start."""

    def __init__(
        self,
        message: str,
        *,
        failed_results: list[FeedLoadResult],
    ) -> None:
        super().__init__(message)
        self.failed_results = failed_results
