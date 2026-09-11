"""Load strategy dispatcher."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from .dataclass.feed_load_result import FeedLoadResult
from .dataclass.load_manifest import LoadManifest
from .dataclass.load_plan import LoadPlan, LoadWave
from .dataclass.load_result import LoadResult
from .dataclass.plan_result import PlanResult
from .exceptions import LoadExecutionError
from .load_strategy import STRATEGIES
from .load_strategy.base import LoadStrategy


class LoadDispatcher:
    """Dispatches planned load waves to the matching load strategy."""

    def __init__(self, *, fail_fast: bool = True) -> None:
        """Initialize the load strategy registry."""
        self.fail_fast = fail_fast
        self._strategies: dict[str, LoadStrategy] = dict(STRATEGIES)

    def register(self, load_type: str, strategy: LoadStrategy) -> None:
        """Replace or add a strategy for a load type."""
        self._strategies[load_type] = strategy

    def dispatch_plan(self, plan: LoadPlan) -> PlanResult:
        """Dispatch a load plan to the appropriate load strategies.

        Waves run in order. A single-feed wave runs on the current thread;
        a multi-feed wave runs in parallel. With ``fail_fast`` (the default),
        a failed wave raises ``LoadExecutionError`` so later waves never start.
        """
        collected: list[FeedLoadResult] = []
        for wave in plan:
            if len(wave) <= 1:
                wave_results = (
                    [self._run_feed(wave[0], wave.index)] if wave else []
                )
            else:
                wave_results = self._run_parallel_wave(wave)

            collected.extend(wave_results)
            failed = [item for item in wave_results if not item.success]
            if failed and self.fail_fast:
                names = ", ".join(item.unique_identifier for item in failed)
                raise LoadExecutionError(
                    f"Wave {wave.index} failed ({names}); later waves were not started.",
                    failed_results=failed,
                )

        return PlanResult(
            success=all(item.success for item in collected),
            results=collected,
        )

    def _run_parallel_wave(self, wave: LoadWave) -> list[FeedLoadResult]:
        ordered: list[FeedLoadResult | None] = [None] * len(wave)
        with ThreadPoolExecutor(max_workers=len(wave)) as pool:
            futures = {
                pool.submit(self._run_feed, manifest, wave.index): index
                for index, manifest in enumerate(wave)
            }
            for future in as_completed(futures):
                ordered[futures[future]] = future.result()
        return [item for item in ordered if item is not None]

    def _run_feed(self, manifest: LoadManifest, wave_index: int) -> FeedLoadResult:
        unique_identifier = manifest.feed_meta.unique_identifier
        started_at = datetime.now()
        try:
            strategy = self._strategies.get(manifest.load_type)
            if strategy is None:
                raise KeyError(
                    f"No load strategy registered for '{manifest.load_type}'."
                )

            raw = strategy.execute(
                source=manifest.source_address,
                target=manifest.target_address,
                feed_meta=manifest.feed_meta,
                feed_specs=manifest.feed_specs,
                load_type=manifest.load_type,
            )
            completed_at = datetime.now()
            result = self._coerce_result(
                raw,
                load_type=manifest.load_type,
                started_at=started_at,
                completed_at=completed_at,
            )
        except Exception as exc:
            result = LoadResult(
                success=False,
                load_type=manifest.load_type,
                started_at=started_at,
                completed_at=datetime.now(),
                error_message=str(exc),
            )

        return FeedLoadResult(
            unique_identifier=unique_identifier,
            wave_index=wave_index,
            result=result,
        )

    @staticmethod
    def _coerce_result(
        raw: object,
        *,
        load_type: str,
        started_at: datetime,
        completed_at: datetime,
    ) -> LoadResult:
        if isinstance(raw, LoadResult):
            return raw
        return LoadResult(
            success=True,
            load_type=load_type,
            started_at=started_at,
            completed_at=completed_at,
        )
