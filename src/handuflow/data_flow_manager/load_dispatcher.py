"""Load strategy dispatcher."""

from __future__ import annotations


from .load_strategy.base import LoadStrategy
from .load_strategy import STRATEGIES
from .dataclass.load_plan import LoadPlan, LoadWave
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from .dataclass.load_manifest import LoadManifest

# from .dataclass.plan_result import PlanResult
# from .dataclass.feed_load_result import FeedLoadResult


class LoadDispatcher:
    """Dispatches loads to the appropriate load strategy."""

    def __init__(self) -> None:
        """Initialize the load strategy registry."""
        self._strategies: dict[str, LoadStrategy] = dict(STRATEGIES)

    def dispatch_plan(self, plan: LoadPlan) -> None:
        """Dispatch a load plan wave by wave."""

        for wave in plan:
            print(f"Dispatching wave {wave.index} " f"with {len(wave)} feed(s)...")

            if wave.is_parallel:
                self._run_parallel_wave(wave)
            else:
                self._run_sequential_wave(wave)

    def _run_sequential_wave(self, wave: LoadWave) -> None:
        """Execute all manifests in a wave sequentially."""

        for manifest in wave:
            self._run_feed(
                manifest=manifest,
                wave_index=wave.index,
            )

    def _run_parallel_wave(self, wave: LoadWave) -> None:
        """Execute all manifests in a wave concurrently."""

        futures: dict[Future[None], LoadManifest] = {}

        with ThreadPoolExecutor(
            max_workers=len(wave),
            thread_name_prefix=f"handuflow-wave-{wave.index}",
        ) as executor:
            for manifest in wave:
                future: Future[None] = executor.submit(
                    self._run_feed,
                    manifest,
                    wave.index,
                )
                futures[future] = manifest

            for future in as_completed(futures):
                manifest: LoadManifest = futures[future]

                try:
                    future.result()
                except Exception:
                    feed_id: str = manifest.feed_meta.unique_identifier

                    print(f"[Wave {wave.index}] " f"Feed failed: {feed_id}")

                    raise

    def _run_feed(
        self,
        manifest: LoadManifest,
        wave_index: int,
    ) -> None:
        """Execute a single feed manifest."""

        feed_id: str = manifest.feed_meta.unique_identifier

        print(f"[Wave {wave_index}] " f"Starting feed: {feed_id}")

        # Strategy execution will be added here.
        pass
