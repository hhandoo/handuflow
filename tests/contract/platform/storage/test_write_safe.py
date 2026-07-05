from __future__ import annotations

from pathlib import Path

from handuflow.platform.storage.base import StorageProvider
from handuflow.platform.storage.path import StoragePath


def test_write_safe_writes_data_to_path(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    write_safe() should write bytes to the target path.
    """
    path = StoragePath(str(tmp_path / "output.bin"))
    data = b"Handuflow"

    storage.write_safe(path, data)

    assert storage.exists(path) is True
    assert storage.is_file(path) is True
    assert Path(path.uri).read_bytes() == data


def test_write_safe_writes_to_nested_path(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    write_safe() should write bytes to a file in an existing nested directory.
    """
    directory = StoragePath(str(tmp_path / "nested" / "dir"))
    storage.create_directory(directory, parents=True)

    path = StoragePath(str(tmp_path / "nested" / "dir" / "output.bin"))
    data = b"Handuflow"

    storage.write_safe(path, data)

    assert storage.exists(path) is True
    assert Path(path.uri).read_bytes() == data


def test_write_safe_overwrites_existing_file(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    write_safe() should replace the contents of an existing file.
    """
    file = tmp_path / "output.bin"
    file.write_bytes(b"old content")

    path = StoragePath(str(file))
    data = b"new content"

    storage.write_safe(path, data)

    assert Path(path.uri).read_bytes() == data
