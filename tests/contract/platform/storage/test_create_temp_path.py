from __future__ import annotations

from pathlib import Path

from handuflow.platform.storage.base import StorageProvider
from handuflow.platform.storage.path import StoragePath


def test_create_temp_path_returns_storage_path(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    create_temp_path() should return a StoragePath instance.
    """
    path = StoragePath(str(tmp_path / "target.txt"))

    temp_path = storage.create_temp_path(path)

    assert isinstance(temp_path, StoragePath)


def test_create_temp_path_returns_unique_path(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    create_temp_path() should return a path distinct from the target path.
    """
    path = StoragePath(str(tmp_path / "target.txt"))

    temp_path = storage.create_temp_path(path)

    assert temp_path.uri != path.uri


def test_create_temp_path_returns_nonexistent_path(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    create_temp_path() should return a path that does not yet exist.
    """
    path = StoragePath(str(tmp_path / "target.txt"))

    temp_path = storage.create_temp_path(path)

    assert storage.exists(temp_path) is False
