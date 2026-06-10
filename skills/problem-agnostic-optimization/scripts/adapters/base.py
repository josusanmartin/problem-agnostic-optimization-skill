from __future__ import annotations

from typing import Any, Protocol


API_VERSION = "pao-harness.v1"

STATUSES = {
    "measured",
    "wrong_answer",
    "compile_error",
    "runtime_error",
    "timeout",
    "rate_limited",
    "submission_error",
    "blocked",
    "internal_error",
}

DECISION_HINTS = {
    "promote",
    "keep",
    "reject",
    "bug",
    "blocked",
    "unknown",
}


class ChallengeAdapter(Protocol):
    def contract(self) -> dict[str, Any]:
        """Return metric, direction, artifact expectations, and limits."""
        ...

    def evaluate(self, request: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a candidate and return a normalized result without progress writing."""
        ...
