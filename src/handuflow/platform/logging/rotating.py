"""Rotating file logging handler backed by the HanduFLOW storage layer."""

from __future__ import annotations

import logging
import threading
from pathlib import Path

from handuflow.platform.storage.base import StorageProvider
from handuflow.platform.storage.path import StoragePath
from handuflow.platform.exceptions.domains.configuration import ConfigurationError
from handuflow.platform.exceptions.domains.storage import StorageError


_EMIT_ERRORS = (
    AttributeError,
    KeyError,
    OSError,
    RecursionError,
    RuntimeError,
    TypeError,
    UnicodeError,
    ValueError,
    ConfigurationError,
    StorageError
)


class StorageRotatingFileHandler(logging.Handler):
    """
    Write log records to storage and rotate when the file exceeds ``max_bytes``.

    Rotation follows the standard pattern:
    ``app.log`` -> ``app.log.1`` -> ``app.log.2``, and so on.

    A lock is used because loggers may be called from multiple threads and
    each emit performs a read-modify-write cycle on the same file.
    """

    def __init__(
        self,
        path: StoragePath,
        storage: StorageProvider,
        max_bytes: int,
        backup_count: int,
        encoding: str = "utf-8",
    ) -> None:
        super().__init__()
        self.path = path
        self._storage = storage
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.encoding = encoding
        self._lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record) + "\n"
            with self._lock:
                self._append(message.encode(self.encoding))
        except _EMIT_ERRORS:
            self.handleError(record)

    def _append(self, data: bytes) -> None:
        self._ensure_parent_exists()

        current = self._read_current()
        if current and 0 < self.max_bytes < len(current) + len(data):
            self._rotate()
            current = b""

        self._storage.write_safe(self.path, current + data)

    def _read_current(self) -> bytes:
        if self._storage.exists(self.path) and self._storage.is_file(self.path):
            return self._storage.read(self.path)
        return b""

    def _ensure_parent_exists(self) -> None:
        parent = StoragePath(str(Path(self.path.uri).parent))
        if not self._storage.exists(parent):
            self._storage.create_directory(parent, parents=True)

    def _backup_path(self, index: int) -> StoragePath:
        return StoragePath(f"{self.path.uri}.{index}")

    def _rotate(self) -> None:
        if self.backup_count <= 0:
            if self._storage.exists(self.path):
                self._storage.delete(self.path)
            return

        oldest = self._backup_path(self.backup_count)
        if self._storage.exists(oldest):
            self._storage.delete(oldest)

        for index in range(self.backup_count - 1, 0, -1):
            source = self._backup_path(index)
            destination = self._backup_path(index + 1)
            if self._storage.exists(source):
                self._storage.move(source, destination)

        if self._storage.exists(self.path):
            self._storage.move(self.path, self._backup_path(1))
