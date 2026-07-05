from __future__ import annotations

from .base import StorageProvider
from .adapters.local import LocalStorageProvider


class StorageManager:
    """
    Manages the active storage provider.

    All storage operations within HanduFLOW are delegated to the
    currently configured provider.
    """

    def __init__(self) -> None:
        self._provider: StorageProvider = LocalStorageProvider()

    @property
    def provider(self) -> StorageProvider:
        """
        Return the active storage provider.
        """
        return self._provider

    def set_provider(
        self,
        provider: StorageProvider,
    ) -> None:
        """
        Configure the active storage provider.
        """
        self._provider = provider

    def reset(self) -> None:
        """
        Reset the storage provider to the default local implementation.
        """
        self._provider = LocalStorageProvider()

    def __getattr__(self, name: str):
        return getattr(self._provider, name)