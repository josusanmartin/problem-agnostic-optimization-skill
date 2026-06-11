#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, HTTPServer
import importlib
import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace
from typing import Any
from urllib.parse import urlparse

from adapters.base import API_VERSION, STATUSES
import record_progress


DEFAULT_WORK_DIR = Path("work/optimization_harness")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def metric_direction(config: dict[str, Any]) -> tuple[str, str]:
    metric = config.get("metric") if isinstance(config.get("metric"), dict) else {}
    name = metric.get("name", "score")
    direction = metric.get("direction", "lower")
    if direction not in {"lower", "higher"}:
        raise SystemExit("metric.direction must be 'lower' or 'higher'")
    return str(name), str(direction)


def import_adapter(import_spec: str, adapter_config: dict[str, Any]) -> Any:
    if ":" not in import_spec:
        raise SystemExit("adapter.import must be MODULE:CLASS")
    module_name, class_name = import_spec.split(":", 1)
    module = importlib.import_module(module_name)
    adapter_class = getattr(module, class_name)
    return adapter_class(adapter_config)


def clean_candidate_id(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("candidate_id is required")
    text = value.strip()
    if any(ch in text for ch in "/\\\t\r\n"):
        raise ValueError("candidate_id cannot contain slashes, tabs, or newlines")
    return text


def decision_for_status(status: str, correct: bool, score: float | int | None, best_score: float | None, direction: str) -> str:
    if status == "measured" and correct and score is not None:
        if best_score is None:
            return "promote"
        if direction == "lower" and float(score) < best_score:
            return "promote"
        if direction == "higher" and float(score) > best_score:
            return "promote"
        if float(score) == best_score:
            return "keep"
        return "reject"
    if status == "wrong_answer":
        return "reject"
    if status in {"compile_error", "runtime_error", "timeout", "submission_error", "internal_error"}:
        return "bug"
    if status in {"rate_limited", "blocked"}:
        return "blocked"
    return "unknown"


def progress_decision(decision_hint: str) -> str:
    return {
        "promote": "promote",
        "keep": "keep",
        "reject": "reject",
        "bug": "bug",
        "blocked": "blocked",
    }.get(decision_hint, "blocked")


def normalize_status(status: Any, ok: bool, correct: bool) -> str:
    if isinstance(status, str) and status in STATUSES:
        return status
    if ok and correct:
        return "measured"
    return "internal_error"


class HarnessState:
    def __init__(self, config_path: Path):
        self.config_path = config_path.resolve()
        self.config = load_json(self.config_path)
        if self.config.get("api_version", API_VERSION) != API_VERSION:
            raise SystemExit(f"unsupported api_version: {self.config.get('api_version')!r}")

        server = self.config.get("server") if isinstance(self.config.get("server"), dict) else {}
        self.host = str(server.get("host", DEFAULT_HOST))
        self.port = int(server.get("port", DEFAULT_PORT))
        if self.host != DEFAULT_HOST:
            raise SystemExit("pao harness server binds only to 127.0.0.1")

        self.project_root = (self.config_path.parent / self.config.get("project_root", ".")).resolve()
        self.work_dir = (self.project_root / self.config.get("work_dir", str(DEFAULT_WORK_DIR))).resolve()
        self.mode = str(self.config.get("mode", "fast"))
        if self.mode not in {"fast", "standard", "audit"}:
            raise SystemExit("mode must be fast, standard, or audit")
        self.metric_name, self.direction = metric_direction(self.config)
        self.rate_limit = self.config.get("rate_limit") if isinstance(self.config.get("rate_limit"), dict) else {}
        self.sidecar = self.config.get("sidecar") if isinstance(self.config.get("sidecar"), dict) else {}
        adapter = self.config.get("adapter") if isinstance(self.config.get("adapter"), dict) else {}
        import_spec = adapter.get("import", "adapters.local_command:Adapter")
        adapter_config = adapter.get("config") if isinstance(adapter.get("config"), dict) else {}
        adapter_config.setdefault("metric_name", self.metric_name)
        adapter_config.setdefault("direction", self.direction)
        self.adapter_import = str(import_spec)
        self.adapter = import_adapter(self.adapter_import, adapter_config)
        self.best_path = self.work_dir / "best.json"
        self.progress_path = self.work_dir / "progress.tsv"
        self.state_path = self.work_dir / "state.json"
        self.raw_logs_dir = self.work_dir / "raw_logs"
        self.last_evaluation_at: float | None = None
        self.evaluation_count = 0
        self.redact_values = self._redact_values(adapter_config)
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for path in (
            self.work_dir,
            self.raw_logs_dir,
            self.work_dir / "results",
            self.work_dir / "profiles",
            self.work_dir / "candidates",
        ):
            path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _redact_values(adapter_config: dict[str, Any]) -> list[str]:
        values: list[str] = []
        token_env = adapter_config.get("token_env")
        if isinstance(token_env, str):
            import os

            token = os.environ.get(token_env)
            if token:
                values.append(token)
        for value in adapter_config.get("redact_values", []) if isinstance(adapter_config.get("redact_values"), list) else []:
            if isinstance(value, str) and value:
                values.append(value)
        return values

    def write_server_json(self) -> None:
        write_json(
            self.work_dir / "server.json",
            {
                "api_version": API_VERSION,
                "base_url": f"http://{self.host}:{self.port}",
                "adapter": self.adapter_import,
                "mode": self.mode,
                "work_dir": self._display_path(self.work_dir),
                "started_at": utc_now(),
            },
        )

    def contract(self) -> dict[str, Any]:
        adapter_contract = self.adapter.contract()
        if not isinstance(adapter_contract, dict):
            adapter_contract = {}
        return {
            "api_version": API_VERSION,
            "objective": self.config.get("objective", ""),
            "metric_name": adapter_contract.get("metric_name", self.metric_name),
            "direction": adapter_contract.get("direction", self.direction),
            "mode": self.mode,
            "artifact_type": adapter_contract.get("artifact_type", "file"),
            "supports_async": bool(adapter_contract.get("supports_async", False)),
            "rate_limit": self.rate_limit,
            "work_dir": self._display_path(self.work_dir),
        }

    def health(self) -> dict[str, Any]:
        return {
            "ok": True,
            "api_version": API_VERSION,
            "adapter": self.adapter_import,
            "mode": self.mode,
        }

    def best(self) -> dict[str, Any]:
        best = self._read_best()
        return {
            "ok": True,
            "best_candidate": best.get("best_candidate"),
            "best_score": best.get("best_score"),
            "metric_name": self.metric_name,
            "direction": self.direction,
            "artifact_path": best.get("artifact_path"),
        }

    def evaluate(self, request: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        try:
            candidate_id = clean_candidate_id(request.get("candidate_id"))
            artifact_path = self._artifact_path(request.get("artifact_path"))
        except ValueError as exc:
            return 400, self._error_response(str(exc), request.get("candidate_id"), "blocked")

        retry_after = self._rate_limit_wait()
        if retry_after is not None:
            return 429, self._error_response(
                f"rate limited; retry after {retry_after:.3f} seconds",
                candidate_id,
                "rate_limited",
            )

        adapter_request = dict(request)
        adapter_request["candidate_id"] = candidate_id
        adapter_request["artifact_path"] = self._display_path(artifact_path)
        adapter_request["artifact_path_abs"] = str(artifact_path)
        adapter_request["project_root"] = str(self.project_root)

        try:
            adapter_result = self.adapter.evaluate(adapter_request)
            if not isinstance(adapter_result, dict):
                raise TypeError("adapter.evaluate must return a JSON object")
        except Exception as exc:  # pragma: no cover - defensive boundary.
            adapter_result = {
                "ok": False,
                "status": "internal_error",
                "correct": False,
                "metric_name": self.metric_name,
                "score": None,
                "direction": self.direction,
                "message": f"adapter error: {exc}",
            }

        self.last_evaluation_at = time.monotonic()
        self.evaluation_count += 1
        raw_log_path = self._write_raw_log(candidate_id, request, adapter_result)
        best_before = self._read_best()
        status = normalize_status(
            adapter_result.get("status"),
            bool(adapter_result.get("ok")),
            bool(adapter_result.get("correct")),
        )
        correct = bool(adapter_result.get("correct", False))
        score = self._score(adapter_result.get("score"))
        if status == "measured" and score is None:
            status = "submission_error"
            correct = False
        elif status == "measured" and not correct:
            status = "wrong_answer"
        direction = str(adapter_result.get("direction") or self.direction)
        if direction not in {"lower", "higher"}:
            direction = self.direction
        metric_name = str(adapter_result.get("metric_name") or self.metric_name)
        decision_hint = decision_for_status(status, correct, score, self._score(best_before.get("best_score")), direction)
        best_after = self._update_best_if_needed(best_before, candidate_id, score, artifact_path, decision_hint, metric_name, direction)
        progress_written = self._write_progress(
            candidate_id,
            metric_name,
            adapter_result.get("score") if score is not None else None,
            progress_decision(decision_hint),
            request.get("label", status),
        )
        candidate_result_path = self._write_candidate_result_if_needed(
            candidate_id,
            request,
            adapter_result,
            decision_hint,
            raw_log_path,
        )
        self._update_state(best_after, candidate_id, status, score, decision_hint)
        refreshed = self._maybe_checkpoint_refresh()

        response = {
            "ok": status == "measured" and correct and score is not None,
            "api_version": API_VERSION,
            "candidate_id": candidate_id,
            "status": status,
            "correct": correct,
            "metric_name": metric_name,
            "score": score,
            "direction": direction,
            "decision_hint": decision_hint,
            "best_score": best_after.get("best_score"),
            "best_candidate": best_after.get("best_candidate"),
            "progress_written": progress_written,
            "raw_log_path": self._display_path(raw_log_path),
            "message": str(adapter_result.get("message", status)),
        }
        if candidate_result_path is not None:
            response["candidate_result_path"] = self._display_path(candidate_result_path)
        if refreshed:
            response["refreshed"] = [self._display_path(path) for path in refreshed]
        return 200, response

    def refresh(self, request: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        artifacts = request.get("artifacts", ["dashboard", "chart"])
        if not isinstance(artifacts, list) or not all(isinstance(item, str) for item in artifacts):
            return 400, {"ok": False, "api_version": API_VERSION, "message": "artifacts must be a list of strings"}
        refreshed = self._refresh_sidecar(set(artifacts))
        return 200, {
            "ok": True,
            "api_version": API_VERSION,
            "refreshed": [self._display_path(path) for path in refreshed],
        }

    def _artifact_path(self, value: Any) -> Path:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("artifact_path is required")
        path = Path(value)
        resolved = path.resolve() if path.is_absolute() else (self.project_root / path).resolve()
        if not is_relative_to(resolved, self.project_root):
            raise ValueError("artifact_path must stay inside project_root")
        return resolved

    def _rate_limit_wait(self) -> float | None:
        minimum = self.rate_limit.get("min_seconds_between_evaluations")
        if minimum is None or self.last_evaluation_at is None:
            return None
        remaining = float(minimum) - (time.monotonic() - self.last_evaluation_at)
        return remaining if remaining > 0 else None

    def _write_raw_log(self, candidate_id: str, request: dict[str, Any], adapter_result: dict[str, Any]) -> Path:
        path = self.raw_logs_dir / f"{candidate_id}.json"
        raw = {
            "api_version": API_VERSION,
            "candidate_id": candidate_id,
            "request": request,
            "adapter_result": adapter_result,
            "recorded_at": utc_now(),
        }
        text = json.dumps(raw, indent=2, sort_keys=True)
        for value in self.redact_values:
            text = text.replace(value, "[REDACTED]")
        path.write_text(text + "\n", encoding="utf-8")
        return path

    def _write_progress(self, candidate_id: str, metric_name: str, score: Any, decision: str, label: Any) -> bool:
        score_text = self._score_text(score)
        args = SimpleNamespace(
            timestamp=None,
            candidate=candidate_id,
            decision=decision,
            score=score_text if score_text is not None and metric_name == "score" else None,
            metric=f"{metric_name}={score_text}" if score_text is not None and metric_name != "score" else None,
            metric_name=metric_name if score is None else None,
            candidate_number=None,
            tokens_total=None,
            tokens_delta=None,
            wall_seconds=None,
            label=str(label or ""),
        )
        metric_column, metric_value = record_progress.parse_metric(args)
        header = record_progress.header_for_append(self.progress_path, metric_column, "")
        row = record_progress.progress_row(args, self.progress_path, header, metric_column, metric_value, "")
        record_progress.append_row(self.progress_path, header, row)
        return True

    def _read_best(self) -> dict[str, Any]:
        if not self.best_path.exists():
            return {}
        try:
            data = load_json(self.best_path)
        except Exception:
            return {}
        return data

    def _update_best_if_needed(
        self,
        best: dict[str, Any],
        candidate_id: str,
        score: float | None,
        artifact_path: Path,
        decision_hint: str,
        metric_name: str,
        direction: str,
    ) -> dict[str, Any]:
        if decision_hint != "promote" or score is None:
            return best
        updated = {
            "api_version": API_VERSION,
            "best_candidate": candidate_id,
            "best_score": score,
            "metric_name": metric_name,
            "direction": direction,
            "artifact_path": self._display_path(artifact_path),
            "updated_at": utc_now(),
        }
        write_json(self.best_path, updated)
        return updated

    def _write_candidate_result_if_needed(
        self,
        candidate_id: str,
        request: dict[str, Any],
        adapter_result: dict[str, Any],
        decision_hint: str,
        raw_log_path: Path,
    ) -> Path | None:
        if self.mode != "audit" and decision_hint != "promote" and not request.get("force_candidate_result"):
            return None
        path = self.work_dir / "candidates" / f"{candidate_id}.result.json"
        write_json(
            path,
            {
                "schema_version": 1,
                "candidate": candidate_id,
                "parent": request.get("parent"),
                "hypothesis": request.get("label", ""),
                "mechanism_class": request.get("mechanism", ""),
                "commands": {},
                "correctness": "pass" if adapter_result.get("correct") else "fail",
                "authoritative_metric": {
                    "score": adapter_result.get("score"),
                    "unit": adapter_result.get("metric_name", self.metric_name),
                    "direction": adapter_result.get("direction", self.direction),
                    "raw_result_path": self._display_path(raw_log_path),
                },
                "promotion_ladder": {},
                "verifier": {},
                "decision": decision_hint.upper(),
                "learning": adapter_result.get("message", ""),
                "created_at": utc_now(),
            },
        )
        return path

    def _update_state(self, best: dict[str, Any], candidate_id: str, status: str, score: float | None, decision_hint: str) -> None:
        state = {}
        if self.state_path.exists():
            try:
                state = load_json(self.state_path)
            except Exception:
                state = {}
        state["api_version"] = state.get("api_version", API_VERSION)
        state["harness_mode"] = self.mode
        state["iterations"] = int(state.get("iterations", 0) or 0) + 1
        if best:
            state["best_stable_candidate"] = best.get("best_candidate")
            state["best_stable_score"] = best.get("best_score")
        state["last_evaluation"] = {
            "candidate_id": candidate_id,
            "status": status,
            "score": score,
            "decision_hint": decision_hint,
            "recorded_at": utc_now(),
        }
        state["last_updated"] = utc_now()
        write_json(self.state_path, state)

    def _maybe_checkpoint_refresh(self) -> list[Path]:
        if self.mode == "fast":
            return []
        every_n = self.sidecar.get("every_n_candidates")
        if every_n is None:
            return []
        try:
            cadence = int(every_n)
        except (TypeError, ValueError):
            return []
        if cadence <= 0 or self.evaluation_count % cadence != 0:
            return []
        return self._refresh_sidecar({"dashboard", "chart"})

    def _refresh_sidecar(self, artifacts: set[str]) -> list[Path]:
        if not artifacts.intersection({"dashboard", "chart"}):
            return []
        render_script = Path(__file__).resolve().parent / "render_progress.py"
        chart_path = self.work_dir / "progress.svg"
        dashboard_path = self.work_dir / "dashboard.html"
        if not self.progress_path.exists():
            return []
        subprocess.run(
            [
                sys.executable,
                str(render_script),
                str(self.progress_path),
                "--chart-output",
                str(chart_path),
                "--dashboard-output",
                str(dashboard_path),
            ],
            cwd=self.project_root,
            check=True,
            text=True,
            capture_output=True,
        )
        refreshed: list[Path] = []
        if "chart" in artifacts:
            refreshed.append(chart_path)
        if "dashboard" in artifacts:
            refreshed.append(dashboard_path)
        return refreshed

    def _error_response(self, message: str, candidate_id: Any, status: str) -> dict[str, Any]:
        best = self._read_best()
        return {
            "ok": False,
            "api_version": API_VERSION,
            "candidate_id": candidate_id,
            "status": status,
            "correct": False,
            "metric_name": self.metric_name,
            "score": None,
            "direction": self.direction,
            "decision_hint": "blocked",
            "best_score": best.get("best_score"),
            "best_candidate": best.get("best_candidate"),
            "progress_written": False,
            "raw_log_path": None,
            "message": message,
        }

    def _display_path(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self.project_root))
        except ValueError:
            return str(path)

    @staticmethod
    def _score(value: Any) -> float | None:
        if value is None or value == "":
            return None
        try:
            number = Decimal(str(value))
        except Exception:
            return None
        if not number.is_finite():
            return None
        return float(number)

    @staticmethod
    def _score_text(value: Any) -> str | None:
        if value is None or value == "":
            return None
        try:
            number = Decimal(str(value))
        except Exception:
            return None
        if not number.is_finite():
            return None
        return record_progress.format_decimal(number)


class HarnessHandler(BaseHTTPRequestHandler):
    server_version = "PAOHarness/0.1"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._send(200, self.state.health())
        elif path == "/contract":
            self._send(200, self.state.contract())
        elif path == "/best":
            self._send(200, self.state.best())
        else:
            self._send(404, {"ok": False, "api_version": API_VERSION, "message": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            request = self._read_json()
        except ValueError as exc:
            self._send(400, {"ok": False, "api_version": API_VERSION, "message": str(exc)})
            return
        if path == "/evaluate":
            status, response = self.state.evaluate(request)
            self._send(status, response)
        elif path == "/refresh":
            status, response = self.state.refresh(request)
            self._send(status, response)
        else:
            self._send(404, {"ok": False, "api_version": API_VERSION, "message": "not found"})

    @property
    def state(self) -> HarnessState:
        return self.server.state  # type: ignore[attr-defined]

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise ValueError(f"invalid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("request JSON must be an object")
        return data

    def _send(self, status: int, data: dict[str, Any]) -> None:
        body = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - %s\n" % (self.log_date_time_string(), fmt % args))


class HarnessHTTPServer(HTTPServer):
    state: HarnessState


def serve(config_path: Path) -> None:
    state = HarnessState(config_path)
    server = HarnessHTTPServer((state.host, state.port), HarnessHandler)
    state.port = int(server.server_address[1])
    server.state = state
    state.write_server_json()
    print(f"pao harness listening on http://{state.host}:{state.port}", flush=True)
    server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local PAO harness API server.")
    parser.add_argument("--config", type=Path, default=Path("pao_harness.json"))
    args = parser.parse_args()
    serve(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
