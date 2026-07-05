from __future__ import annotations

import shutil
import tempfile
import uuid
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from ..base import StorageProvider
from ..path import StoragePath


class LocalStorageProvider(StorageProvider):
    @property
    def name(self) -> str:
        return "local"

    def exists(
        self,
        spath: StoragePath,
        **kwargs: Any,
    ) -> bool:
        return Path(spath.uri).exists()

    def is_file(
        self,
        spath: StoragePath,
        **kwargs: Any,
    ) -> bool:
        return Path(spath.uri).is_file()

    def is_directory(
        self,
        spath: StoragePath,
        **kwargs: Any,
    ) -> bool:
        return Path(spath.uri).is_dir()

    def create_directory(
        self,
        spath: StoragePath,
        **kwargs: Any,
    ) -> None:
        Path(spath.uri).mkdir(**kwargs)

    def delete(
        self,
        spath: StoragePath,
        **kwargs: Any,
    ) -> None:
        p = Path(spath.uri)

        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()

    def move(
        self,
        source: StoragePath,
        destination: StoragePath,
        **kwargs: Any,
    ) -> None:
        shutil.move(source.uri, destination.uri)

    def copy(
        self,
        source: StoragePath,
        destination: StoragePath,
        **kwargs: Any,
    ) -> None:
        src = Path(source.uri)
        dst = Path(destination.uri)

        if src.is_dir():
            shutil.copytree(src, dst, **kwargs)
        else:
            shutil.copy2(src, dst)

    def list(
        self,
        spath: StoragePath,
        **kwargs: Any,
    ) -> Iterable[StoragePath]:
        for child in Path(spath.uri).iterdir():
            yield StoragePath(str(child))

    def create_temp_path(
        self,
        spath: StoragePath,
    ) -> StoragePath:
        temp_dir = Path(tempfile.gettempdir()) / "handuflow"
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_file = temp_dir / uuid.uuid4().hex

        return StoragePath(str(temp_file))

    def _write(
        self,
        spath: StoragePath,
        data: bytes,
        **kwargs: Any,
    ) -> None:
        p = Path(spath.uri)

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)