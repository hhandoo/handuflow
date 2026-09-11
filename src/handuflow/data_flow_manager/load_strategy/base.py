"""Base class for HanduFLOW load strategies."""

from __future__ import annotations

from typing import Any
from abc import ABC, abstractmethod
from ..dataclass.load_manifest import LoadManifest


class LoadStrategy(ABC):
    """Abstract base class for all load strategies."""

    def __detect_source_target_change(self, load_manifest: LoadManifest) -> bool:
        """Detect if the source data has changed since the last load."""
        # Placeholder for actual change detection logic
        return True

    @abstractmethod
    def execute(self, load_manifest: LoadManifest) -> Any:

        raise NotImplementedError
