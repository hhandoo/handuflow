from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DefaultConfiguration:
    system_name: str
    environment: str