from __future__ import annotations

from typing import Any


class Adapter:
    def __init__(self, config: dict[str, Any]):
        self.config = config

    def contract(self) -> dict[str, Any]:
        return {
            "metric_name": self.config.get("metric_name", "score"),
            "direction": self.config.get("direction", "lower"),
            "artifact_type": "file",
            "supports_async": False,
        }

    def evaluate(self, request: dict[str, Any]) -> dict[str, Any]:
        artifact_path = request["artifact_path"]
        raise NotImplementedError(f"submit/poll/parse {artifact_path!r} in a concrete adapter")
