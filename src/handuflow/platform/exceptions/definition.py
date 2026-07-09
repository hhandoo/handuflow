"""Immutable error definition model for HanduFLOW exceptions."""

from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ErrorDefinition:
    """
    Immutable definition of an application error.

    Every error in HanduFLOW should be represented by one
    ErrorDefinition instance.
    """

    code: str
    message: str
    recoverable: bool = False