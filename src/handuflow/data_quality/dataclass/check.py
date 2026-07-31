from dataclasses import dataclass

@dataclass
class CheckDC:
    name: str
    check_range: list[dict[str, int]] | None = None

    def __str__(self) -> str:
        return (
            f"\n"
            f"name      = {self.name}\n"
            f"check_range     = {self.check_range}\n"
        )
