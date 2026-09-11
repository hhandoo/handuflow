"""Tests for dependency-aware load planning."""

from __future__ import annotations

from handuflow.data_flow_manager.dataclass.address import Address
from handuflow.data_flow_manager.dataclass.feed_meta import FeedMeta
from handuflow.data_flow_manager.dataclass.feed_specs import FeedSpecs
from handuflow.data_flow_manager.dataclass.load_manifest import LoadManifest
from handuflow.data_flow_manager.load_planner import LoadPlanner


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


def test_parallel_feeds_share_a_batch() -> None:
    """Feeds with the same dependency should run in parallel after it completes."""
    manifests = [
        _manifest("C"),
        _manifest("A", depends_on=["C"]),
        _manifest("B", depends_on=["C"]),
    ]

    plan = LoadPlanner().build_plan(manifests)

    assert len(plan) == 2
    assert {manifest.feed_meta.unique_identifier for manifest in plan[0]} == {"C"}
    assert {manifest.feed_meta.unique_identifier for manifest in plan[1]} == {
        "A",
        "B",
    }
    assert plan[1].is_parallel


def test_series_feeds_run_in_separate_batches() -> None:
    """A chain of dependencies should produce one feed per batch."""
    manifests = [
        _manifest("raw"),
        _manifest("staging", depends_on=["raw"]),
        _manifest("mart", depends_on=["staging"]),
    ]

    plan = LoadPlanner().build_plan(manifests)

    assert len(plan) == 3
    assert [manifest.feed_meta.unique_identifier for manifest in plan[0]] == ["raw"]
    assert [manifest.feed_meta.unique_identifier for manifest in plan[1]] == [
        "staging"
    ]
    assert [manifest.feed_meta.unique_identifier for manifest in plan[2]] == ["mart"]


def test_mixed_graph_produces_expected_batches() -> None:
    """C -> (A, B in parallel) -> D."""
    manifests = [
        _manifest("C"),
        _manifest("A", depends_on=["C"]),
        _manifest("B", depends_on=["C"]),
        _manifest("D", depends_on=["A", "B"]),
    ]

    plan = LoadPlanner().build_plan(manifests)

    assert len(plan) == 3
    assert {manifest.feed_meta.unique_identifier for manifest in plan[0]} == {"C"}
    assert {manifest.feed_meta.unique_identifier for manifest in plan[1]} == {
        "A",
        "B",
    }
    assert {manifest.feed_meta.unique_identifier for manifest in plan[2]} == {"D"}


def test_unknown_dependency_raises() -> None:
    manifests = [_manifest("A", depends_on=["missing"])]

    try:
        LoadPlanner().build_plan(manifests)
    except ValueError as exc:
        assert "unknown dependency" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for unknown dependency")


def test_circular_dependency_raises() -> None:
    manifests = [
        _manifest("A", depends_on=["B"]),
        _manifest("B", depends_on=["A"]),
    ]

    try:
        LoadPlanner().build_plan(manifests)
    except ValueError as exc:
        assert "circular dependency" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for circular dependency")
