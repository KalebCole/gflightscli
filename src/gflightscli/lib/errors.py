"""Structured error types with JSON envelopes and exit codes."""

from __future__ import annotations

import json
import sys


class GFlightsError(Exception):
    """Base error with structured JSON output."""

    code: int = 5
    error_type: str = "internal_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            "status": "error",
            "error": {
                "code": self.code,
                "type": self.error_type,
                "message": self.message,
            },
        }


class APIError(GFlightsError):
    code = 1
    error_type = "api_error"


class ValidationError(GFlightsError):
    code = 3
    error_type = "validation_error"


class NotFoundError(GFlightsError):
    code = 4
    error_type = "not_found"


class InternalError(GFlightsError):
    code = 5
    error_type = "internal_error"


def handle_error(err: GFlightsError) -> None:
    """Print JSON error envelope to stdout and exit with the error code."""
    print(json.dumps(err.to_dict(), indent=2))
    sys.exit(err.code)
