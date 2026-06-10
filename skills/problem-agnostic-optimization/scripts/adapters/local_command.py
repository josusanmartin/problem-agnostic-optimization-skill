from __future__ import annotations

from pathlib import Path
import re
import subprocess
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
        command_template = self.config.get("command")
        if not isinstance(command_template, str) or not command_template.strip():
            return {
                "ok": False,
                "status": "blocked",
                "correct": False,
                "metric_name": self.config.get("metric_name", "score"),
                "score": None,
                "direction": self.config.get("direction", "lower"),
                "message": "local_command adapter missing command",
            }

        project_root = Path(request.get("project_root", "."))
        artifact_path = request["artifact_path"]
        values = {
            "artifact_path": artifact_path,
            "artifact_path_abs": str((project_root / artifact_path).resolve()),
            "candidate_id": request.get("candidate_id", ""),
        }
        command = command_template.format_map(values)
        timeout = self.config.get("timeout_seconds")
        try:
            completed = subprocess.run(
                command,
                shell=True,
                cwd=project_root,
                text=True,
                capture_output=True,
                timeout=float(timeout) if timeout is not None else None,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "ok": False,
                "status": "timeout",
                "correct": False,
                "metric_name": self.config.get("metric_name", "score"),
                "score": None,
                "direction": self.config.get("direction", "lower"),
                "message": f"command timed out after {timeout} seconds",
                "raw": {
                    "stdout": exc.stdout or "",
                    "stderr": exc.stderr or "",
                    "command": command,
                },
            }

        output = f"{completed.stdout}\n{completed.stderr}"
        metric_name = self.config.get("metric_name", "score")
        metric_regex = self.config.get("metric_regex")
        score = None
        if isinstance(metric_regex, str) and metric_regex:
            match = re.search(metric_regex, output, re.MULTILINE)
            if match:
                score = float(match.group(1))

        correct_regex = self.config.get("correct_regex")
        if isinstance(correct_regex, str) and correct_regex:
            correct = re.search(correct_regex, output, re.MULTILINE | re.IGNORECASE) is not None
        else:
            correct = completed.returncode == 0 and score is not None

        status = self._status(completed.returncode, correct, score, output)
        return {
            "ok": status == "measured" and correct,
            "status": status,
            "correct": correct,
            "metric_name": metric_name,
            "score": score,
            "direction": self.config.get("direction", "lower"),
            "message": self._message(status, completed.returncode, output),
            "raw": {
                "command": command,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            },
        }

    @staticmethod
    def _status(returncode: int, correct: bool, score: float | None, output: str) -> str:
        if returncode != 0:
            lowered = output.lower()
            if "compile" in lowered or "syntax" in lowered:
                return "compile_error"
            return "runtime_error"
        if score is None:
            return "submission_error"
        if not correct:
            return "wrong_answer"
        return "measured"

    @staticmethod
    def _message(status: str, returncode: int, output: str) -> str:
        for line in output.splitlines():
            text = line.strip()
            if text:
                return text[:500]
        if status == "runtime_error":
            return f"command exited with status {returncode}"
        return status
