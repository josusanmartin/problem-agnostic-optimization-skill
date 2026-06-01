from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = REPO_ROOT / "skills" / "problem-agnostic-optimization" / "scripts" / "init_harness.py"


def test_init_harness_creates_progress_artifacts(tmp_path: Path) -> None:
    work = tmp_path / "work"

    subprocess.run(
        [
            sys.executable,
            str(INIT_SCRIPT),
            "--work-dir",
            str(work),
            "--objective",
            "sub 1000 cycles",
            "--metric",
            "cycles",
            "--budget",
            "no budget limit",
            "--validation",
            "official checker",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    expected = [
        "audit.md",
        "best.md",
        "dashboard.html",
        "events.jsonl",
        "log.md",
        "plan.md",
        "progress.svg",
        "progress.tsv",
        "review.md",
        "state.json",
    ]
    for name in expected:
        assert (work / name).exists()

    state = json.loads((work / "state.json").read_text(encoding="utf-8"))
    assert state["score_unit"] == "cycles"
    assert state["progress"]["chart_enabled"] is True
    assert state["progress"]["events"].endswith("work/events.jsonl")
    assert state["progress"]["usage_source"] == "runtime goal usage if available"
    assert (work / "progress.tsv").read_text(encoding="utf-8").startswith("timestamp\tcandidate\tscore\tdecision\ttokens_total")
    assert "sub 1000 cycles" in (work / "best.md").read_text(encoding="utf-8")
    assert "Token source:" in (work / "review.md").read_text(encoding="utf-8")
    dashboard = (work / "dashboard.html").read_text(encoding="utf-8").lower()
    assert "waiting for the first measurement" in dashboard


def test_init_harness_can_disable_chart_placeholders(tmp_path: Path) -> None:
    work = tmp_path / "work"

    subprocess.run(
        [
            sys.executable,
            str(INIT_SCRIPT),
            "--work-dir",
            str(work),
            "--progress-chart",
            "off",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert (work / "events.jsonl").exists()
    assert not (work / "progress.svg").exists()
    assert not (work / "dashboard.html").exists()
    state = json.loads((work / "state.json").read_text(encoding="utf-8"))
    assert state["progress"]["chart_enabled"] is False
