"""Built-in HanduFLOW validation rules."""

from __future__ import annotations

from ..base import Validation
from .print_validation import PrintValidation

VALIDATIONS: list[Validation] = [
    PrintValidation(),
]

__all__ = [
    "PrintValidation",
    "VALIDATIONS",
]
