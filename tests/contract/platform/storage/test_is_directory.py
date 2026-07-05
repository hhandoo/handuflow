from __future__ import annotations

from pathlib import Path

from handuflow.platform.storage.base import StorageProvider
from handuflow.platform.storage.path import StoragePath


def test_is_directory_returns_false_for_nonexistent_path(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    is_directory() should return False for a path that does not exist.
    """
    path = StoragePath(str(tmp_path / "missing"))

    assert storage.is_directory(path) is False


def test_is_directory_returns_true_for_existing_directory(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    is_directory() should return True for an existing directory.
    """
    directory = tmp_path / "data"
    directory.mkdir()

    path = StoragePath(str(directory))

    assert storage.is_directory(path) is True


def test_is_directory_returns_false_for_existing_file(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    is_directory() should return False for an existing file.
    """
    file = tmp_path / "file.txt"
    file.write_text("Handuflow")

    path = StoragePath(str(file))

    assert storage.is_directory(path) is False
