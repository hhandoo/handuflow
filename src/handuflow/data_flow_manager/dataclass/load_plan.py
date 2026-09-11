from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from .load_manifest import LoadManifest


@dataclass(slots=True)
class LoadWave:
    """One execution wave. Multiple manifests run in parallel."""

    index: int
    manifests: list[LoadManifest] = field(
        default_factory=lambda: list[LoadManifest]()
    )

    @property
    def is_parallel(self) -> bool:
        return len(self.manifests) > 1

    @property
    def unique_identifiers(self) -> list[str]:
        return [manifest.feed_meta.unique_identifier for manifest in self.manifests]

    def __iter__(self) -> Iterator[LoadManifest]:
        return iter(self.manifests)

    def __len__(self) -> int:
        return len(self.manifests)

    def __getitem__(self, index: int) -> LoadManifest:
        return self.manifests[index]


@dataclass(slots=True)
class LoadPlan:
    """Ordered waves: each wave waits for the previous wave to finish."""

    waves: list[LoadWave] = field(default_factory=list[LoadWave])

    @property
    def feed_count(self) -> int:
        return sum(len(wave) for wave in self.waves)

    @property
    def wave_count(self) -> int:
        return len(self.waves)

    def __iter__(self) -> Iterator[LoadWave]:
        return iter(self.waves)

    def __len__(self) -> int:
        return len(self.waves)

    def __getitem__(self, index: int) -> LoadWave:
        return self.waves[index]

    def format_execution_tree(self) -> str:
        if not self.waves:
            return "HanduFLOW load plan\n(no feeds)"

        lines: list[str] = [
            "HanduFLOW load plan",
            f"{self.feed_count} feed{'s' if self.feed_count != 1 else ''} "
            f"→ {self.wave_count} wave{'s' if self.wave_count != 1 else ''}",
            "",
        ]

        for wave in self.waves:
            mode = "parallel" if wave.is_parallel else "sequential"
            parents = _wave_parents(wave)
            after = f"  after: {', '.join(parents)}" if parents else "  roots"
            lines.append(
                f"[wave {wave.index}]  ({len(wave)} feed"
                f"{'s' if len(wave) != 1 else ''}, {mode}){after}"
            )
            lines.extend(_tree_lines(wave))
            if wave.index < self.wave_count - 1:
                lines.append("    │")
                lines.append("    ▼")

        return "\n".join(lines)

    def print_execution_tree(self) -> None:
        print(self.format_execution_tree())


def _deps(manifest: LoadManifest) -> list[str]:
    raw = getattr(manifest.feed_meta, "depends_on", None)
    if not raw:
        return []
    if isinstance(raw, str):
        return [raw]
    return [dep for dep in raw if dep]


def _wave_parents(wave: LoadWave) -> list[str]:
    parents: set[str] = set()
    for manifest in wave:
        parents.update(_deps(manifest))
    return sorted(parents)


def _tree_lines(wave: LoadWave) -> list[str]:
    lines: list[str] = []
    last = len(wave) - 1
    for i, manifest in enumerate(wave):
        feed_id = manifest.feed_meta.unique_identifier
        deps = _deps(manifest)
        suffix = f"  ← {', '.join(deps)}" if deps else ""
        branch = "└── " if i == last else "├── "
        lines.append(f"    {branch}{feed_id}{suffix}")
    return lines
