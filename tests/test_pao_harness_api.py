from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "problem-agnostic-optimization"
SERVER_SCRIPT = SKILL_DIR / "scripts" / "pao_harness_server.py"
CLIENT_SCRIPT = SKILL_DIR / "scripts" / "pao_harness_client.py"


def write_project(tmp_path: Path, *, mode: str = "fast", every_n: int | None = None) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    (project / "submissions").mkdir()
    (project / "benchmark.py").write_text(
        "\n".join(
            [
                "from pathlib import Path",
                "import re",
                "import sys",
                "artifact = Path(sys.argv[1])",
                "text = artifact.read_text(encoding='utf-8')",
                "if 'compile_error' in text:",
                "    print('compiler error: undefined symbol foo')",
                "    raise SystemExit(1)",
                "if 'runtime_error' in text:",
                "    print('runtime explosion')",
                "    raise SystemExit(2)",
                "match = re.search(r'score\\s*=\\s*([0-9.]+)', text)",
                "score = float(match.group(1)) if match else 999.0",
                "correct = 'wrong_answer' not in text",
                "print(f'score: {score:g}')",
                "print(f'correct: {str(correct).lower()}')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    sidecar: dict[str, Any] = {"refresh_policy": "checkpoint_only"}
    if every_n is not None:
        sidecar["every_n_candidates"] = every_n
    config = {
        "api_version": "pao-harness.v1",
        "server": {"host": "127.0.0.1", "port": 0},
        "project_root": ".",
        "work_dir": "work/optimization_harness",
        "mode": mode,
        "metric": {"name": "score", "direction": "lower"},
        "adapter": {
            "import": "adapters.local_command:Adapter",
            "config": {
                "command": f"{sys.executable} benchmark.py {{artifact_path}}",
                "metric_regex": r"score:\s*([0-9.]+)",
                "correct_regex": r"correct:\s*true",
            },
        },
        "sidecar": sidecar,
    }
    (project / "pao_harness.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return project


def start_server(project: Path) -> tuple[subprocess.Popen[str], str]:
    proc = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT), "--config", "pao_harness.json"],
        cwd=project,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    server_json = project / "work" / "optimization_harness" / "server.json"
    deadline = time.time() + 10
    while time.time() < deadline:
        if server_json.exists():
            data = json.loads(server_json.read_text(encoding="utf-8"))
            return proc, data["base_url"]
        if proc.poll() is not None:
            stdout, stderr = proc.communicate()
            raise AssertionError(f"server exited early\nstdout={stdout}\nstderr={stderr}")
        time.sleep(0.05)
    stop_server(proc)
    raise AssertionError("server did not write server.json")


def stop_server(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate(timeout=5)


def api_request(base_url: str, method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(f"{base_url}{path}", data=body, method=method, headers=headers)
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def evaluate(base_url: str, candidate: str, artifact: str, label: str = "") -> tuple[int, dict[str, Any]]:
    return api_request(
        base_url,
        "POST",
        "/evaluate",
        {
            "candidate_id": candidate,
            "artifact_path": artifact,
            "parent": "baseline",
            "label": label,
            "mechanism": "test mechanism",
        },
    )


def progress_rows(project: Path) -> list[dict[str, str]]:
    progress = project / "work" / "optimization_harness" / "progress.tsv"
    with progress.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def test_health_and_contract(tmp_path: Path) -> None:
    project = write_project(tmp_path)
    proc, base_url = start_server(project)
    try:
        status, health = api_request(base_url, "GET", "/health")
        assert status == 200
        assert health["ok"] is True
        assert health["api_version"] == "pao-harness.v1"
        assert health["mode"] == "fast"

        status, contract = api_request(base_url, "GET", "/contract")
        assert status == 200
        assert contract["metric_name"] == "score"
        assert contract["direction"] == "lower"
        assert contract["artifact_type"] == "file"
        assert contract["supports_async"] is False
        assert contract["work_dir"] == "work/optimization_harness"
    finally:
        stop_server(proc)


def test_evaluate_success_writes_progress_raw_log_and_best(tmp_path: Path) -> None:
    project = write_project(tmp_path)
    (project / "submissions" / "cand_0001.py").write_text("score = 10\n", encoding="utf-8")
    proc, base_url = start_server(project)
    try:
        status, result = evaluate(base_url, "cand_0001", "submissions/cand_0001.py", "baseline candidate")
        assert status == 200
        assert result["ok"] is True
        assert result["status"] == "measured"
        assert result["correct"] is True
        assert result["score"] == 10.0
        assert result["decision_hint"] == "promote"
        assert result["best_candidate"] == "cand_0001"
        assert result["progress_written"] is True
        assert result["raw_log_path"] == "work/optimization_harness/raw_logs/cand_0001.json"

        rows = progress_rows(project)
        assert rows[-1]["candidate"] == "cand_0001"
        assert rows[-1]["score"] == "10.0"
        assert rows[-1]["decision"] == "promote"
        assert rows[-1]["label"] == "baseline candidate"

        raw = json.loads((project / result["raw_log_path"]).read_text(encoding="utf-8"))
        assert raw["adapter_result"]["status"] == "measured"

        best = json.loads((project / "work" / "optimization_harness" / "best.json").read_text(encoding="utf-8"))
        assert best["best_candidate"] == "cand_0001"
        assert best["best_score"] == 10.0
        assert best["artifact_path"] == "submissions/cand_0001.py"

        candidate_result = project / "work" / "optimization_harness" / "candidates" / "cand_0001.result.json"
        assert candidate_result.exists()
    finally:
        stop_server(proc)


def test_best_does_not_update_on_regression(tmp_path: Path) -> None:
    project = write_project(tmp_path)
    (project / "submissions" / "cand_0001.py").write_text("score = 10\n", encoding="utf-8")
    (project / "submissions" / "cand_0002.py").write_text("score = 12\n", encoding="utf-8")
    proc, base_url = start_server(project)
    try:
        assert evaluate(base_url, "cand_0001", "submissions/cand_0001.py")[1]["decision_hint"] == "promote"
        status, result = evaluate(base_url, "cand_0002", "submissions/cand_0002.py", "regressed")
        assert status == 200
        assert result["decision_hint"] == "reject"
        assert result["best_candidate"] == "cand_0001"
        assert result["best_score"] == 10.0
        assert not (project / "work" / "optimization_harness" / "candidates" / "cand_0002.result.json").exists()

        status, best = api_request(base_url, "GET", "/best")
        assert status == 200
        assert best["best_candidate"] == "cand_0001"
        assert best["best_score"] == 10.0
    finally:
        stop_server(proc)


def test_compile_error_writes_bug_progress_and_raw_log(tmp_path: Path) -> None:
    project = write_project(tmp_path)
    (project / "submissions" / "cand_bad.py").write_text("compile_error\n", encoding="utf-8")
    proc, base_url = start_server(project)
    try:
        status, result = evaluate(base_url, "cand_bad", "submissions/cand_bad.py", "bad compile")
        assert status == 200
        assert result["ok"] is False
        assert result["status"] == "compile_error"
        assert result["decision_hint"] == "bug"
        assert result["progress_written"] is True
        rows = progress_rows(project)
        assert rows[-1]["candidate"] == "cand_bad"
        assert rows[-1]["score"] == ""
        assert rows[-1]["decision"] == "bug"
        raw = json.loads((project / result["raw_log_path"]).read_text(encoding="utf-8"))
        assert raw["adapter_result"]["raw"]["returncode"] == 1
    finally:
        stop_server(proc)


def test_rejects_artifact_outside_project_root(tmp_path: Path) -> None:
    project = write_project(tmp_path)
    (tmp_path / "outside.py").write_text("score = 1\n", encoding="utf-8")
    proc, base_url = start_server(project)
    try:
        status, result = evaluate(base_url, "cand_escape", "../outside.py")
        assert status == 400
        assert result["status"] == "blocked"
        assert result["progress_written"] is False
        assert result["raw_log_path"] is None
        assert "inside project_root" in result["message"]
        assert not (project / "work" / "optimization_harness" / "progress.tsv").exists()
    finally:
        stop_server(proc)


def test_fast_mode_does_not_refresh_dashboard_per_candidate(tmp_path: Path) -> None:
    project = write_project(tmp_path, mode="fast", every_n=1)
    (project / "submissions" / "cand_0001.py").write_text("score = 10\n", encoding="utf-8")
    proc, base_url = start_server(project)
    try:
        status, result = evaluate(base_url, "cand_0001", "submissions/cand_0001.py")
        assert status == 200
        assert "refreshed" not in result
        harness = project / "work" / "optimization_harness"
        assert not (harness / "progress.svg").exists()
        assert not (harness / "dashboard.html").exists()
    finally:
        stop_server(proc)


def test_standard_mode_refreshes_at_checkpoint(tmp_path: Path) -> None:
    project = write_project(tmp_path, mode="standard", every_n=1)
    (project / "submissions" / "cand_0001.py").write_text("score = 10\n", encoding="utf-8")
    proc, base_url = start_server(project)
    try:
        status, result = evaluate(base_url, "cand_0001", "submissions/cand_0001.py")
        assert status == 200
        assert result["refreshed"] == [
            "work/optimization_harness/progress.svg",
            "work/optimization_harness/dashboard.html",
        ]
        assert (project / "work" / "optimization_harness" / "progress.svg").exists()
        assert (project / "work" / "optimization_harness" / "dashboard.html").exists()
    finally:
        stop_server(proc)


def test_refresh_endpoint(tmp_path: Path) -> None:
    project = write_project(tmp_path)
    (project / "submissions" / "cand_0001.py").write_text("score = 10\n", encoding="utf-8")
    proc, base_url = start_server(project)
    try:
        assert evaluate(base_url, "cand_0001", "submissions/cand_0001.py")[0] == 200
        status, result = api_request(base_url, "POST", "/refresh", {"artifacts": ["chart", "dashboard"]})
        assert status == 200
        assert result["ok"] is True
        assert result["refreshed"] == [
            "work/optimization_harness/progress.svg",
            "work/optimization_harness/dashboard.html",
        ]
    finally:
        stop_server(proc)


def test_raw_logs_redact_configured_secret_values(tmp_path: Path) -> None:
    project = write_project(tmp_path)
    config_path = project / "pao_harness.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["adapter"]["config"]["command"] = f"{sys.executable} benchmark.py {{artifact_path}} && printf SECRET_VALUE"
    config["adapter"]["config"]["redact_values"] = ["SECRET_VALUE"]
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    (project / "submissions" / "cand_0001.py").write_text("score = 10\n", encoding="utf-8")
    proc, base_url = start_server(project)
    try:
        status, result = evaluate(base_url, "cand_0001", "submissions/cand_0001.py")
        assert status == 200
        raw_text = (project / result["raw_log_path"]).read_text(encoding="utf-8")
        assert "SECRET_VALUE" not in raw_text
        assert "[REDACTED]" in raw_text
    finally:
        stop_server(proc)


def test_client_reads_server_json_and_evaluate_prints_json(tmp_path: Path) -> None:
    project = write_project(tmp_path)
    (project / "submissions" / "cand_0001.py").write_text("score = 10\n", encoding="utf-8")
    proc, _base_url = start_server(project)
    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(CLIENT_SCRIPT),
                "evaluate",
                "--candidate",
                "cand_0001",
                "--artifact",
                "submissions/cand_0001.py",
                "--label",
                "client path",
            ],
            cwd=project,
            check=True,
            text=True,
            capture_output=True,
        )
        result = json.loads(completed.stdout)
        assert result["candidate_id"] == "cand_0001"
        assert result["decision_hint"] == "promote"
        assert result["progress_written"] is True
    finally:
        stop_server(proc)
