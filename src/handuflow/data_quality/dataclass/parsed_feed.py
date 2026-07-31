from dataclasses import dataclass
from .check_obj import CheckObj

@dataclass(slots=True)
class ParsedFeed:
    full_file_path: str
    feed_identifier: str
    parsed_data_quality_checks: list[CheckObj]