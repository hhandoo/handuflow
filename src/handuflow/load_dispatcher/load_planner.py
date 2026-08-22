from __future__ import annotations

from collections import defaultdict
from typing import TypeAlias

from .dataclass.load_manifest import LoadManifest

LoadBatch: TypeAlias = list[LoadManifest]
LoadPlan: TypeAlias = list[LoadBatch]


class LoadPlanner:
    """Builds dependency-aware execution plans for feeds."""

    def build_plan(
        self,
        manifests: list[LoadManifest],
    ) -> LoadPlan:
        """Build parallel execution batches from feed manifests.

        Feeds with no unresolved dependencies are placed in the
        same batch and can therefore execute in parallel.
        """

        manifest_map = self._build_manifest_map(manifests)

        dependencies = self._build_dependency_map(
            manifests,
            manifest_map,
        )

        remaining = set(manifest_map)

        plan: LoadPlan = []

        while remaining:
            batch = [
                manifest_map[feed_id]
                for feed_id in remaining
                if not dependencies[feed_id] & remaining
            ]

            if not batch:
                raise ValueError("Circular dependency detected in feed configuration.")

            plan.append(batch)

            completed = {manifest.feed_meta.unique_identifier for manifest in batch}

            remaining -= completed

        return plan

    @staticmethod
    def _build_manifest_map(
        manifests: list[LoadManifest],
    ) -> dict[str, LoadManifest]:
        """Index manifests by unique identifier."""
        manifest_map: dict[str, LoadManifest] = {}
        for manifest in manifests:
            feed_id = manifest.feed_meta.unique_identifier
            manifest_map[feed_id] = manifest
        return manifest_map

    @staticmethod
    def _build_dependency_map(
        manifests: list[LoadManifest],
        manifest_map: dict[str, LoadManifest],
    ) -> dict[str, set[str]]:
        """Build feed dependency relationships."""

        dependencies: dict[str, set[str]] = defaultdict(set)

        for manifest in manifests:
            feed_id = manifest.feed_meta.unique_identifier
            upstream = manifest.feed_meta.upstream_identifier

            if upstream:
                if upstream not in manifest_map:
                    raise ValueError(
                        f"Feed '{feed_id}' references unknown "
                        f"upstream feed '{upstream}'."
                    )

                dependencies[feed_id].add(upstream)

        for feed_id in manifest_map:
            dependencies.setdefault(feed_id, set())

        return dict(dependencies)
