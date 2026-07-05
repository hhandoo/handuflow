from __future__ import annotations

from pathlib import Path

from handuflow.platform.storage.base import StorageProvider
from handuflow.platform.storage.path import StoragePath


def test_delete_removes_existing_file(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    delete() should remove an existing file.
    """
    file = tmp_path / "sample.txt"
    file.write_text("Handuflow")

    path = StoragePath(str(file))

    storage.delete(path)

    assert storage.exists(path) is False


def test_delete_removes_existing_directory(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    delete() should remove an existing directory and its contents.
    """
    directory = tmp_path / "data"
    directory.mkdir()
    (directory / "nested.txt").write_text("Handuflow")

    path = StoragePath(str(directory))

    storage.delete(path)

    assert storage.exists(path) is False
