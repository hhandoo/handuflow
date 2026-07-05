from __future__ import annotations

from pathlib import Path

from handuflow.platform.storage.base import StorageProvider
from handuflow.platform.storage.path import StoragePath


def test_list_returns_directory_contents(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    list() should return all immediate children of a directory.
    """
    directory = tmp_path / "data"
    directory.mkdir()
    (directory / "file.txt").write_text("Handuflow")
    (directory / "subdir").mkdir()

    path = StoragePath(str(directory))
    children = list(storage.list(path))

    assert len(children) == 2
    assert all(isinstance(child, StoragePath) for child in children)
    child_names = {Path(child.uri).name for child in children}
    assert child_names == {"file.txt", "subdir"}


def test_list_returns_empty_for_empty_directory(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    list() should return an empty iterable for an empty directory.
    """
    directory = tmp_path / "empty"
    directory.mkdir()

    path = StoragePath(str(directory))

    assert list(storage.list(path)) == []
