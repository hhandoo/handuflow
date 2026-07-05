from __future__ import annotations

import pytest

from handuflow.platform.storage.adapters.local import LocalStorageProvider
from handuflow.platform.storage.base import StorageProvider


@pytest.fixture
def storage() -> StorageProvider:
    """
    Return the storage provider under test.

    Contract tests should depend only on the StorageProvider
    interface, never on a concrete implementation.
    """
    return LocalStorageProvider()