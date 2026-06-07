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
        "breakthroughs.md",
        "checkpoints/progress.json",
        "candidates/_template.result.json",
        "dashboard.html",
        "events.jsonl",
        "log.md",
        "plan.md",
        "promotion_ladder.md",
        "progress.svg",
        "progress.tsv",
        "review.md",
        "schemas/candidate_result.schema.json",
        "state.json",
        "verifier.md",
    ]
    for name in expected:
        assert (work / name).exists()

    state = json.loads((work / "state.json").read_text(encoding="utf-8"))
    assert state["schema_version"] == 2
    assert state["score_unit"] == "cycles"
    assert state["harness_mode"] == "standard"
    assert state["candidate_artifacts"]["required_for_promotions"] is True
    assert state["breakthrough_mining"]["path"].endswith("work/breakthroughs.md")
    assert state["breakthrough_mining"]["enabled"] is True
    assert state["escape"]["status"] == "tracking"
    assert state["escape"]["active_burst"] == []
    assert state["escape"]["basin_memory"] == []
    assert state["escape"]["diversity_map"] == []
    assert state["escape"]["operator_credit"] == {}
    assert state["escape"]["controlled_regression_allowed"] is False
    assert state["promotion_ladder"]["enabled"] is True
    assert state["promotion_ladder"]["gating_steps"] == [
        "apply_or_build",
        "correctness",
        "authoritative_metric",
        "regression_or_adversarial",
        "fresh_verifier",
        "promote",
    ]
    assert state["verifier"]["mode"] == "fresh_environment_when_possible"
    assert state["execution_boundary"]["draft_patch_only"] is False
    assert state["checkpoint"]["path"].endswith("work/checkpoints/progress.json")
    assert state["progress"]["chart_enabled"] is True
    assert state["progress"]["critical_path_required"] == [
        "correctness",
        "authoritative_metric",
        "progress_row",
        "raw_evidence_path",
        "decision",
    ]
    assert state["progress"]["sidecar"]["enabled"] is True
    assert state["progress"]["sidecar"]["policy"] == "defer_advisory_artifacts_without_blocking_candidate_iteration"
    assert "render_progress.py" in state["progress"]["sidecar"]["refresh_command"]
    assert state["progress"]["sidecar"]["must_not_mutate"] == [
        str(work / "best.md"),
        "canonical promotion state",
        "final submission state",
    ]
    assert state["progress"]["events"].endswith("work/events.jsonl")
    assert state["progress"]["usage_source"] == "explicit get_goal snapshots in work/log.md"
    assert "latest_usage_snapshot" in state["progress"]
    assert state["multi_agent"]["enabled"] is False
    assert state["multi_agent"]["mode"] == "off"
    assert (work / "progress.tsv").read_text(encoding="utf-8").startswith(
        "timestamp\tcandidate\tscore\tdecision\ttokens_total\ttokens_delta\twall_seconds\tlabel"
    )
    assert "sub 1000 cycles" in (work / "best.md").read_text(encoding="utf-8")
    assert "Multi-agent mode: off" in (work / "best.md").read_text(encoding="utf-8")
    assert "Harness mode: standard" in (work / "best.md").read_text(encoding="utf-8")
    assert "Draft patch only: no" in (work / "best.md").read_text(encoding="utf-8")
    assert "- harness mode: standard" in (work / "log.md").read_text(encoding="utf-8")
    assert "Token source:" in (work / "review.md").read_text(encoding="utf-8")
    assert "Fresh Verifier Gate" in (work / "verifier.md").read_text(encoding="utf-8")
    assert "Promotion Ladder" in (work / "promotion_ladder.md").read_text(encoding="utf-8")
    breakthroughs = (work / "breakthroughs.md").read_text(encoding="utf-8")
    assert "Breakthrough Rows" in breakthroughs
    assert "Diversity Map / Feature Cells" in breakthroughs
    assert "Escape Operator Credit" in breakthroughs
    assert "Closed Hills / New-Hill Commitments" in breakthroughs
    plan = (work / "plan.md").read_text(encoding="utf-8")
    assert "Escape Ladder" in plan
    assert "Escape operator:" in plan
    assert "Basin memory:" in plan
    assert "Critical Path" in plan
    assert "Sidecar Queue" in plan
    checkpoint = json.loads((work / "checkpoints" / "progress.json").read_text(encoding="utf-8"))
    assert checkpoint["current_phase"] == "harness_boot"
    assert checkpoint["phase_status"]["fresh_verifier"] == "pending"
    schema = json.loads((work / "schemas" / "candidate_result.schema.json").read_text(encoding="utf-8"))
    assert "mechanism_class" in schema["required"]
    template = json.loads((work / "candidates" / "_template.result.json").read_text(encoding="utf-8"))
    assert template["promotion_ladder"]["fresh_verifier"] == "pending"
    assert template["verifier"]["verdict"] is None
    assert template["screening"]["promotion_allowed"] is False
    assert template["screening"]["calibration"]["stacked_knob_cases"] == []
    assert template["validation_island"]["contract_allowed"] is False
    assert template["phase_owners"] == []
    assert template["escape"]["status"] == "tracking"
    assert template["escape"]["escape_operator"] is None
    assert template["escape"]["controlled_regression_allowed"] is False
    assert template["escape"]["operator_credit_signal"] is None
    for dirname in ("raw_logs", "results", "profiles", "PATCHES"):
        assert (work / dirname).is_dir()
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
    assert (work / "verifier.md").exists()
    assert (work / "promotion_ladder.md").exists()
    assert (work / "checkpoints" / "progress.json").exists()
    assert not (work / "progress.svg").exists()
    assert not (work / "dashboard.html").exists()
    state = json.loads((work / "state.json").read_text(encoding="utf-8"))
    assert state["progress"]["chart_enabled"] is False
    assert state["progress"]["sidecar"]["enabled"] is False


def test_init_harness_can_use_minimal_harness_mode(tmp_path: Path) -> None:
    work = tmp_path / "work"

    subprocess.run(
        [
            sys.executable,
            str(INIT_SCRIPT),
            "--work-dir",
            str(work),
            "--harness-mode",
            "minimal",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    state = json.loads((work / "state.json").read_text(encoding="utf-8"))
    assert state["harness_mode"] == "minimal"
    assert state["progress"]["critical_path_required"] == [
        "correctness",
        "authoritative_metric",
        "progress_row",
        "raw_evidence_path",
        "decision",
    ]
    assert state["progress"]["sidecar"]["enabled"] is False
    assert "Harness mode: minimal" in (work / "best.md").read_text(encoding="utf-8")


def test_init_harness_can_enable_multi_agent_mode(tmp_path: Path) -> None:
    work = tmp_path / "work"

    subprocess.run(
        [
            sys.executable,
            str(INIT_SCRIPT),
            "--work-dir",
            str(work),
            "--multi-agent-mode",
            "on",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    state = json.loads((work / "state.json").read_text(encoding="utf-8"))
    assert state["multi_agent"]["enabled"] is True
    assert state["multi_agent"]["mode"] == "on"
    assert state["multi_agent"]["promotion_policy"] == "coordinator_only_authoritative_gate"
    assert "Multi-agent mode: on" in (work / "best.md").read_text(encoding="utf-8")
    assert "- multi-agent mode: on" in (work / "log.md").read_text(encoding="utf-8")
    assert "- Multi-agent mode: on" in (work / "plan.md").read_text(encoding="utf-8")
