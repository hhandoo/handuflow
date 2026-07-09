from __future__ import annotations

from pathlib import Path

from handuflow.platform.storage.base import StorageProvider
from handuflow.platform.storage.path import StoragePath


def test_create_directory_creates_new_directory(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    create_directory() should create a directory that does not yet exist.
    """
    path = StoragePath(str(tmp_path / "new_dir"))

    storage.create_directory(path)


    assert storage.exists(path) is True
    assert storage.is_directory(path) is True


def test_create_directory_creates_nested_directories(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    create_directory() should create nested directories when parents=True.
    """
    path = StoragePath(str(tmp_path / "a" / "b" / "c"))

    storage.create_directory(path, parents=True)

    assert storage.exists(path) is True
    assert storage.is_directory(path) is True
