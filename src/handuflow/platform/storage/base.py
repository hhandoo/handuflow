"""Abstract storage contract for HanduFLOW providers.

Defines ``StorageProvider``, the interface implemented by every storage
backend such as local filesystem, object stores, and lakehouse paths.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, IO

from .path import StoragePath


class StorageProvider(ABC):
    """
    Abstract base class for all storage providers.

    Every storage backend (Local, S3, ADLS, GCS, DBFS, etc.) must
    implement this interface. The rest of HanduFLOW interacts only
    with this contract and never with a concrete implementation.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the human-readable name of the storage provider."""

    @abstractmethod
    def exists(
        self,
        path: StoragePath,
        **kwargs: Any,
    ) -> bool:
        """Return ``True`` if the path exists."""

    @abstractmethod
    def is_file(
        self,
        path: StoragePath,
        **kwargs: Any,
    ) -> bool:
        """Return ``True`` if the path represents a file."""

    @abstractmethod
    def is_directory(
        self,
        path: StoragePath,
        **kwargs: Any,
    ) -> bool:
        """Return ``True`` if the path represents a directory."""

    @abstractmethod
    def create_directory(
        self,
        path: StoragePath,
        **kwargs: Any
    ) -> None:
        """Create a directory."""

    @abstractmethod
    def delete(
        self,
        path: StoragePath,
        **kwargs: Any
    ) -> None:
        """Delete a file or directory."""

    @abstractmethod
    def move(
        self,
        source: StoragePath,
        destination: StoragePath,
        **kwargs: Any,
    ) -> None:
        """Move or rename a file or directory."""

    @abstractmethod
    def copy(
        self,
        source: StoragePath,
        destination: StoragePath,
        **kwargs: Any,
    ) -> None:
        """Copy a file or directory."""

    @abstractmethod
    def list(
        self,
        path: StoragePath,
        **kwargs: Any,
    ) -> Iterable[StoragePath]:
        """Return the contents of a directory."""

    @abstractmethod
    def read(
        self,
        path: StoragePath,
        **kwargs: Any,
    ) -> bytes:
        """Read and return the contents of a file."""

    @abstractmethod
    def create_temp_path(
            self,
            path: StoragePath,
    ) -> StoragePath:
        """Return a temporary path for writing."""

    def write_safe(
        self,
        path: StoragePath,
        data: bytes,
        **kwargs: Any,
    ) -> None:
        temp_path = self.create_temp_path(path)

        try:
            self._write(temp_path, data, **kwargs)
            self.move(temp_path, path)
        except Exception:
            self.delete(temp_path)
            raise

    @abstractmethod
    def _write(
        self,
        path: StoragePath,
        data: bytes,
        **kwargs: Any,
    ) -> None:
        """Write directly to the given path."""
