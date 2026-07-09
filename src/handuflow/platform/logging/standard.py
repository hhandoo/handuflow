"""Standard date-partitioned file logging handler backed by storage.

Log files are written to ``{log_directory}/{YYYY}/{MM}/{DD}/`` and expired
day directories can be removed automatically via ``log_retention_days``.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path

from handuflow.platform.exceptions.domains.configuration import ConfigurationError
from handuflow.platform.exceptions.domains.storage import StorageError
from handuflow.platform.storage.base import StorageProvider
from handuflow.platform.storage.path import StoragePath

DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

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
    StorageError,
)


def _build_standard_log_path(
    log_directory: StoragePath,
    log_file_name: str,
    run_id: str,
    *,
    run_date: datetime | None = None,
) -> StoragePath:
    when = run_date or datetime.now()
    date_path = when.strftime("%Y/%m/%d")
    filename = f"{log_file_name}_{run_id}.log"
    return StoragePath(f"{log_directory.uri}/{date_path}/{filename}")


def _purge_expired_standard_logs(
    log_directory: StoragePath,
    storage: StorageProvider,
    log_retention_days: int,
    *,
    now: datetime | None = None,
) -> None:
    if log_retention_days <= 0:
        return

    if not storage.exists(log_directory):
        return

    cutoff_date = (now or datetime.now()).date() - timedelta(days=log_retention_days)

    for year_path in _list_directories(storage, log_directory):
        year_name = Path(year_path.uri).name
        if len(year_name) != 4 or not year_name.isdigit():
            continue

        for month_path in _list_directories(storage, year_path):
            month_name = Path(month_path.uri).name
            if len(month_name) != 2 or not month_name.isdigit():
                continue

            for day_path in _list_directories(storage, month_path):
                day_name = Path(day_path.uri).name
                if len(day_name) != 2 or not day_name.isdigit():
                    continue

                try:
                    log_date = datetime(
                        int(year_name),
                        int(month_name),
                        int(day_name),
                    ).date()
                except ValueError:
                    continue

                if log_date < cutoff_date:
                    storage.delete(day_path)


def _list_directories(
    storage: StorageProvider,
    path: StoragePath,
) -> list[StoragePath]:
    return [
        child
        for child in storage.list(path)
        if storage.is_directory(child)
    ]


class StorageFileHandler(logging.Handler):
    """
    Write log records to a single storage-backed file without rotation.

    Typically configured externally, for example by ``SystemConfigurator``.
    """

    def __init__(
        self,
        log_directory: StoragePath,
        log_file_name: str,
        run_id: str,
        storage: StorageProvider,
        *,
        log_retention_days: int = 0,
        run_date: datetime | None = None,
        encoding: str = "utf-8",
    ) -> None:
        super().__init__()
        self.log_directory = log_directory
        self._storage = storage
        self.encoding = encoding
        self._lock = threading.Lock()

        _purge_expired_standard_logs(
            log_directory,
            storage,
            log_retention_days,
            now=run_date,
        )

        self.path = _build_standard_log_path(
            log_directory,
            log_file_name,
            run_id,
            run_date=run_date,
        )

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
        self._storage.write_safe(self.path, current + data)

    def _read_current(self) -> bytes:
        if self._storage.exists(self.path) and self._storage.is_file(self.path):
            return self._storage.read(self.path)
        return b""

    def _ensure_parent_exists(self) -> None:
        parent = StoragePath(str(Path(self.path.uri).parent))
        if not self._storage.exists(parent):
            self._storage.create_directory(parent, parents=True)
