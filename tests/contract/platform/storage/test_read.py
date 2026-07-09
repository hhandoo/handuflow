from __future__ import annotations

from pathlib import Path

from handuflow.platform.storage.base import StorageProvider
from handuflow.platform.storage.path import StoragePath


def test_read_returns_file_contents(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    read() should return the contents of an existing file.
    """
    file = tmp_path / "sample.txt"
    file.write_bytes(b"Handuflow")

    path = StoragePath(str(file))

    assert storage.read(path) == b"Handuflow"


def test_read_returns_empty_bytes_for_empty_file(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    read() should return empty bytes for an empty file.
    """
    file = tmp_path / "empty.bin"
    file.write_bytes(b"")

    path = StoragePath(str(file))

    assert storage.read(path) == b""


def test_read_returns_updated_contents_after_write(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    read() should return (reflect) the latest contents after a file is overwritten.
    """
    path = StoragePath(str(tmp_path / "output.bin"))

    storage.write_safe(path, b"original")
    assert storage.read(path) == b"original"

    storage.write_safe(path, b"updated")

    assert storage.read(path) == b"updated"
