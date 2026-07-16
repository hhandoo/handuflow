from abc import ABC, abstractmethod

from .dataclass.result import CheckResult


class BaseDataQualityCheck(ABC):

    name = "Base Check"

    @abstractmethod
    def validate(self, context) -> CheckResult:
        pass