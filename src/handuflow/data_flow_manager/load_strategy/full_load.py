"""Full load strategy."""

from __future__ import annotations

from typing import Any

from .base import LoadStrategy
from ..dataclass.load_manifest import LoadManifest


class FullLoadStrategy(LoadStrategy):
    """Strategy for performing a full load."""

    def __init__(self, load_manifest: LoadManifest) -> None:
        super().__init__(load_manifest)
        self.load_manifest = load_manifest

    def __build_staging_layer(self):
        pass

    def execute(self) -> Any:
        """Replace the target with the source dataset."""
        pass
