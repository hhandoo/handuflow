from dataclasses import dataclass, field
from .feed_load_result import FeedLoadResult


@dataclass(slots=True)
class PlanResult:
    success: bool
    results: list[FeedLoadResult] = field(
        default_factory=lambda: list[FeedLoadResult]()
    )
