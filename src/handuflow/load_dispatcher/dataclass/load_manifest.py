"""Load manifest definitions for HanduFLOW."""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass
from .feed_specs import FeedSpecs


@dataclass(slots=True)
class LoadManifest:
    """Complete manifest describing a HanduFLOW load."""

    run_id: str
    feed_name: str
    load_type: str
    feed_specs: FeedSpecs
    source: Any = None
    target: Any = None
