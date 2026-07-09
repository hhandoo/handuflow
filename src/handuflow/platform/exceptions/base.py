"""Base exception types for HanduFLOW."""

from __future__ import annotations

from typing import Any

from .definition import ErrorDefinition


class HanduflowError(Exception):
    """
    Base exception for all HanduFLOW exceptions.

    Every framework exception should inherit from this class.

    The exception contains:
        • Error definition
        • Runtime context
        • Original cause
    """

    def __init__(
        self,
        error: ErrorDefinition,
        *,
        cause: Exception | None = None,
        **context: Any,
    ) -> None:
        super().__init__(error.message)

        self.error = error
        self.cause = cause
        self.context = context

    @property
    def code(self) -> str:
        return self.error.code

    @property
    def message(self) -> str:
        return self.error.message

    @property
    def severity(self):
        return self.error.severity

    @property
    def recoverable(self):
        return self.error.recoverable

    def to_dict(self) -> dict[str, Any]:
        """
        Return a structured representation suitable
        for logging or serialization.
        """
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "recoverable": self.recoverable,
            "context": self.context,
            "cause": repr(self.cause) if self.cause else None,
        }

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"