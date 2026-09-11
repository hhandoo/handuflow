"""Tests for parallel load execution."""

from __future__ import annotations

import threading
import time
from typing import Any

from handuflow.data_flow_manager.dataclass.address import Address
from handuflow.data_flow_manager.dataclass.feed_meta import FeedMeta
from handuflow.data_flow_manager.dataclass.feed_specs import FeedSpecs
from handuflow.data_flow_manager.dataclass.load_manifest import LoadManifest
from handuflow.data_flow_manager.exceptions import LoadExecutionError
from handuflow.data_flow_manager.load_dispatcher import LoadDispatcher
from handuflow.data_flow_manager.load_planner import LoadPlanner
from handuflow.data_flow_manager.load_strategy.base import LoadStrategy


class RecordingStrategy(LoadStrategy):
    """Strategy that records execution order and thread ids."""

    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []
        self._lock = threading.Lock()

    def execute(self, source: Any, target: Any, **kwargs: Any) -> Any:
        feed_meta = kwargs["feed_meta"]
        with self._lock:
            self.events.append(
                (feed_meta.unique_identifier, threading.current_thread().name)
            )
        time.sleep(0.05)
        return None


def _manifest(feed_id: str, depends_on: list[str] | None = None) -> LoadManifest:
    return LoadManifest(
        feed_meta=FeedMeta(
            unique_identifier=feed_id,
            depends_on=depends_on or [],
        ),
        source_address=Address(
            type="hive_metastore",
            format="delta",
            schema="demo",
            table=feed_id,
        ),
        target_address=Address(
            type="hive_metastore",
            format="delta",
            schema="test",
            table=feed_id,
        ),
        load_type="FULL_LOAD",
        feed_specs=FeedSpecs(),
    )


def test_executor_runs_parallel_batch_on_different_threads() -> None:
    strategy = RecordingStrategy()
    dispatcher = LoadDispatcher()
    dispatcher.register("FULL_LOAD", strategy)

    manifests = [
        _manifest("C"),
        _manifest("A", depends_on=["C"]),
        _manifest("B", depends_on=["C"]),
    ]
    plan = LoadPlanner().build_plan(manifests)

    result = dispatcher.dispatch_plan(plan)

    assert result.success
    assert strategy.events[0][0] == "C"
    assert {feed_id for feed_id, _ in strategy.events[1:]} == {"A", "B"}

    parallel_threads = {thread for feed_id, thread in strategy.events if feed_id in {"A", "B"}}
    assert len(parallel_threads) == 2


def test_executor_stops_after_failed_batch() -> None:
    class FailingStrategy(LoadStrategy):
        def execute(self, source: Any, target: Any, **kwargs: Any) -> Any:
            feed_meta = kwargs["feed_meta"]
            if feed_meta.unique_identifier == "A":
                raise RuntimeError("boom")
            return None

    dispatcher = LoadDispatcher()
    dispatcher.register("FULL_LOAD", FailingStrategy())

    manifests = [
        _manifest("C"),
        _manifest("A", depends_on=["C"]),
        _manifest("B", depends_on=["C"]),
        _manifest("D", depends_on=["A", "B"]),
    ]
    plan = LoadPlanner().build_plan(manifests)

    try:
        dispatcher.dispatch_plan(plan)
    except LoadExecutionError as exc:
        assert len(exc.failed_results) == 1
        assert exc.failed_results[0].unique_identifier == "A"
    else:
        raise AssertionError("Expected LoadExecutionError when a feed fails")
