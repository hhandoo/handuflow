from __future__ import annotations

from pathlib import Path

from handuflow.platform.storage.base import StorageProvider
from handuflow.platform.storage.path import StoragePath


def test_copy_duplicates_file(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    copy() should duplicate a file while leaving the source intact.
    """
    source_file = tmp_path / "source.txt"
    source_file.write_text("Handuflow")

    source = StoragePath(str(source_file))
    destination = StoragePath(str(tmp_path / "copy.txt"))

    storage.copy(source, destination)

    assert storage.exists(source) is True
    assert storage.exists(destination) is True
    assert Path(destination.uri).read_text() == "Handuflow"


def test_copy_duplicates_directory(
    storage: StorageProvider,
    tmp_path: Path,
) -> None:
    """
    copy() should duplicate a directory and its contents.
    """
    source_dir = tmp_path / "source_dir"
    source_dir.mkdir()
    (source_dir / "file.txt").write_text("Handuflow")

    source = StoragePath(str(source_dir))
    destination = StoragePath(str(tmp_path / "copy_dir"))

    storage.copy(source, destination)

    assert storage.exists(source) is True
    assert storage.exists(destination) is True
    assert storage.is_directory(destination) is True
    assert (Path(destination.uri) / "file.txt").read_text() == "Handuflow"
