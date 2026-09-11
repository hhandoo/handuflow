"""Load manifest definitions for HanduFLOW."""

from __future__ import annotations

from dataclasses import dataclass
from .feed_specs import FeedSpecs
from .feed_meta import FeedMeta
from .address import Address


@dataclass(slots=True)
class LoadManifest:
    """Complete manifest describing a HanduFLOW load."""

    feed_meta: FeedMeta
    source_address: Address
    target_address: Address
    load_type: str
    feed_specs: FeedSpecs
