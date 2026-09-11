from .load_result import LoadResult

from dataclasses import dataclass


@dataclass(slots=True)
class FeedLoadResult:
    unique_identifier: str
    wave_index: int
    result: LoadResult

    @property
    def success(self) -> bool:
        return self.result.success
