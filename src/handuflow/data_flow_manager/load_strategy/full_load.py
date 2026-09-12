"""Full load strategy."""

from __future__ import annotations

from typing import Any

from .base import LoadStrategy
from ..dataclass.load_manifest import LoadManifest
from ...platform.configurator import ConfigurationContext


class FullLoadStrategy(LoadStrategy):
    """Strategy for performing a full load."""

    def __init__(
        self, load_manifest: LoadManifest, configuration_context: ConfigurationContext
    ) -> None:
        super().__init__(
            load_manifest=load_manifest, configuration_context=configuration_context
        )
        self.load_manifest = load_manifest
        self.transfer_config = self._generate_transfer_config(
            self.load_manifest.source_address, self.load_manifest.target_address
        )

    def __build_staging_layer(self):
        pass

    def execute(self) -> Any:
        """Replace the target with the source dataset."""
        self.__build_staging_layer()
