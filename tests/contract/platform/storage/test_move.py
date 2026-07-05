from __future__ import annotations

from pathlib import Path

from handuflow.platform.storage.base import StorageProvider
from handuflow.platform.storage.path import StoragePath


def test_move_relocates_file(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    move() should relocate a file to a new path.
    """
    source_file = tmp_path / "source.txt"
    source_file.write_text("Handuflow")

    source = StoragePath(str(source_file))
    destination = StoragePath(str(tmp_path / "destination.txt"))

    storage.move(source, destination)

    assert storage.exists(source) is False
    assert storage.exists(destination) is True
    assert storage.is_file(destination) is True


def test_move_renames_file_in_same_directory(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    move() should rename a file within the same directory.
    """
    original = tmp_path / "original.txt"
    original.write_text("Handuflow")

    source = StoragePath(str(original))
    destination = StoragePath(str(tmp_path / "renamed.txt"))

    storage.move(source, destination)

    assert storage.exists(source) is False
    assert storage.exists(destination) is True


def test_move_relocates_directory(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    move() should relocate a directory to a new path.
    """
    source_dir = tmp_path / "source_dir"
    source_dir.mkdir()
    (source_dir / "file.txt").write_text("Handuflow")

    source = StoragePath(str(source_dir))
    destination = StoragePath(str(tmp_path / "destination_dir"))

    storage.move(source, destination)

    assert storage.exists(source) is False
    assert storage.exists(destination) is True
    assert storage.is_directory(destination) is True
    assert storage.exists(StoragePath(str(tmp_path / "destination_dir" / "file.txt"))) is True
