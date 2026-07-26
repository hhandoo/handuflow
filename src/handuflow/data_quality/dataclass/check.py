from dataclasses import dataclass


@dataclass
class CheckDC:
    name: str
    check_range: range | None = None

    def __str__(self) -> str:
        if self.check_range is None:
            range_str = "None"
        else:
            range_str = (
                f"range(start={self.check_range.start}, "
                f"stop={self.check_range.stop}, "
                f"step={self.check_range.step})"
            )

        return (
            f"CheckDC("
            f"name='{self.name}', "
            f"check_range={range_str}"
            f")"
        )