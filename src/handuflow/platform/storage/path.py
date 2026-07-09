"""Storage path value object for HanduFLOW."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StoragePath:
    """
    Represents a storage location.

    Examples:
        file:///tmp/data.csv
        s3://bucket/data.csv
        gs://bucket/data.csv
        dbfs:/mnt/data.csv
        abfss://container@account/path/file.csv
    """

    uri: str

    def __str__(self) -> str:
        return self.uri