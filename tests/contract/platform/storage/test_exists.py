from __future__ import annotations

from pathlib import Path

from handuflow.platform.storage.base import StorageProvider
from handuflow.platform.storage.path import StoragePath


def test_exists_returns_false_for_nonexistent_path(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    exists() should return False for a path that does not exist.
    """
    path = StoragePath(str(tmp_path / "missing.txt"))

    assert storage.exists(path) is False


def test_exists_returns_true_for_existing_file(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    exists() should return True for an existing file.
    """
    path = StoragePath(str(tmp_path / "file.txt"))

    path_obj = tmp_path / "file.txt"
    path_obj.write_text("Handuflow")

    assert storage.exists(path) is True


def test_exists_returns_true_for_existing_directory(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    exists() should return True for an existing directory.
    """
    directory = tmp_path / "data"
    directory.mkdir()

    path = StoragePath(str(directory))

    assert storage.exists(path) is True


def test_exists_returns_false_after_file_deletion(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    exists() should return False after a file has been deleted.
    """
    file = tmp_path / "sample.txt"
    file.write_text("Handuflow")

    path = StoragePath(str(file))

    assert storage.exists(path) is True

    storage.delete(path)

    assert storage.exists(path) is False