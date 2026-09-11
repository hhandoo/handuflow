from __future__ import annotations

from collections import defaultdict, deque

from .dataclass.load_manifest import LoadManifest
from .dataclass.load_plan import LoadPlan, LoadWave


class LoadPlanner:
    """Turn LoadManifests into dependency-aware execution waves.

    A feed is ready when every id in feed_meta.depends_on has already
    been placed in an earlier wave. Feeds that become ready together
    share a wave and may run in parallel.
    """

    def build_plan(self, manifests: list[LoadManifest]) -> LoadPlan:
        by_id = self._index(manifests)
        dependents, indegree = self._graph(by_id)

        ready = deque(feed_id for feed_id, degree in indegree.items() if degree == 0)
        waves: list[LoadWave] = []
        placed = 0

        while ready:
            wave_ids = sorted(ready)
            ready.clear()
            waves.append(
                LoadWave(
                    index=len(waves),
                    manifests=[by_id[feed_id] for feed_id in wave_ids],
                )
            )
            placed += len(wave_ids)

            for feed_id in wave_ids:
                for child in dependents[feed_id]:
                    indegree[child] -= 1
                    if indegree[child] == 0:
                        ready.append(child)

        if placed != len(by_id):
            cyclic = sorted(
                feed_id for feed_id, degree in indegree.items() if degree > 0
            )
            raise ValueError(
                "Circular dependency detected in feed configuration: "
                + ", ".join(cyclic)
            )

        return LoadPlan(waves=waves)

    def format_execution_tree(self, plan: LoadPlan) -> str:
        """Console-ready execution tree of unique identifiers."""
        return plan.format_execution_tree()

    def print_execution_tree(self, plan: LoadPlan) -> None:
        plan.print_execution_tree()

    @staticmethod
    def _index(manifests: list[LoadManifest]) -> dict[str, LoadManifest]:
        by_id: dict[str, LoadManifest] = {}
        for manifest in manifests:
            feed_id = manifest.feed_meta.unique_identifier
            if feed_id in by_id:
                raise ValueError(f"Duplicate unique_identifier: '{feed_id}'")
            by_id[feed_id] = manifest
        return by_id

    @staticmethod
    def _deps(manifest: LoadManifest) -> list[str]:
        raw = getattr(manifest.feed_meta, "depends_on", None)
        if not raw:
            return []
        if isinstance(raw, str):
            return [raw]
        return [dep for dep in raw if dep]

    def _graph(
        self,
        by_id: dict[str, LoadManifest],
    ) -> tuple[dict[str, list[str]], dict[str, int]]:
        dependents: dict[str, list[str]] = defaultdict(list)
        indegree: dict[str, int] = {feed_id: 0 for feed_id in by_id}

        for feed_id, manifest in by_id.items():
            seen: set[str] = set()
            for dep in self._deps(manifest):
                if dep not in by_id:
                    raise ValueError(
                        f"Feed '{feed_id}' depends_on unknown dependency '{dep}'."
                    )
                if dep == feed_id:
                    raise ValueError(f"Feed '{feed_id}' cannot depend on itself.")
                if dep in seen:
                    continue
                seen.add(dep)
                dependents[dep].append(feed_id)
                indegree[feed_id] += 1

        return dependents, indegree
