from __future__ import annotations

import json
from pathlib import Path
import shlex
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = REPO_ROOT / "skills" / "problem-agnostic-optimization" / "scripts" / "init_harness.py"
RENDER_SCRIPT = INIT_SCRIPT.parent / "render_progress.py"


def test_init_harness_creates_progress_artifacts(tmp_path: Path) -> None:
    work = tmp_path / "work" / "optimization_harness"

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
            "--progress-chart",
            "on",
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
    assert state["harness_mode"] == "fast"
    assert state["requested_harness_mode"] == "fast"
    assert state["candidate_artifacts"]["directory"] == str(work / "candidates")
    assert state["candidate_artifacts"]["schema"] == str(work / "schemas" / "candidate_result.schema.json")
    assert state["candidate_artifacts"]["required_for_promotions"] is True
    assert state["candidate_artifacts"]["required_for_rejects"] is False
    assert state["candidate_artifacts"]["fast_mode_reject_policy"] == "progress_row_plus_one_line_learning_is_enough"
    assert state["breakthrough_mining"]["path"] == str(work / "breakthroughs.md")
    assert state["breakthrough_mining"]["enabled"] is True
    assert state["escape"]["status"] == "tracking"
    assert state["escape"]["active_burst"] == []
    assert state["escape"]["basin_memory"] == []
    assert state["escape"]["diversity_map"] == []
    assert state["escape"]["operator_credit"] == {}
    assert state["escape"]["controlled_regression_allowed"] is False
    assert state["search_health"]["accounting_unit"] == "measured_attempt"
    assert state["search_health"]["attempts_since_promotion"] == 0
    assert state["search_health"]["same_family_miss_limit"] == 3
    assert state["search_health"]["promotion_drought_budget_fraction"] == 0.10
    assert state["search_health"]["force_off_hill_next"] is False
    assert state["search_health"]["compound_structural_candidates_allowed"] is True
    assert state["search_health"]["checkpoints_count_as_candidates"] is False
    assert state["search_health"]["floor_requires_lower_bound"] is True
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
    assert state["checkpoint"]["path"] == str(work / "checkpoints" / "progress.json")
    assert state["progress"]["chart_enabled"] is True
    assert state["progress"]["critical_path_required"] == [
        "result_or_blocker",
        "decision",
        "next_direction",
    ]
    assert state["progress"]["critical_path_best_effort"] == [
        "progress_row",
        "usage_snapshot",
        "raw_evidence_path",
        "compact_log_note",
    ]
    assert "candidate_json_for_rejected_candidates" in state["progress"]["checkpoint_or_audit_only"]
    assert state["progress"]["throughput_guard"]["enabled"] is True
    assert state["progress"]["throughput_guard"]["degrade_to"] == "fast"
    assert "next_candidate_known_and_logging_is_only_remaining_work" in state["progress"]["throughput_guard"]["switch_when"]
    assert "checkpoint_or_token_work_can_be_owned_by_a_coordinator" in state["progress"]["throughput_guard"]["switch_when"]
    assert state["progress"]["sidecar"]["enabled"] is False
    assert state["progress"]["sidecar"]["policy"] == "checkpoint_only"
    assert state["progress"]["sidecar"]["refresh_triggers"]["every_n_candidates"] == 10
    assert state["progress"]["sidecar"]["refresh_triggers"]["idle_only"] is True
    assert "token_accounting_wait" in state["progress"]["sidecar"]["forbidden_on_fast_path"]
    assert "same_artifact_checkpoint_administration_when_delegable" in state["progress"]["sidecar"]["forbidden_on_fast_path"]
    assert state["progress"]["sidecar"]["semantics"].startswith("deferred_in_single_agent_runs")
    refresh_command = state["progress"]["sidecar"]["refresh_command"]
    assert refresh_command.startswith(f"python {shlex.quote(str(RENDER_SCRIPT))} ")
    assert "python skills/problem-agnostic-optimization/scripts/render_progress.py" not in refresh_command
    assert str(work / "progress.tsv") in refresh_command
    assert state["progress"]["sidecar"]["safe_sidecar_outputs"] == [
        str(work / "progress.svg"),
        str(work / "dashboard.html"),
        str(work / "review.md"),
    ]
    assert state["progress"]["sidecar"]["must_not_mutate"] == [
        str(work / "best.md"),
        "canonical promotion state",
        "final submission state",
    ]
    assert state["progress"]["events"] == str(work / "events.jsonl")
    assert state["progress"]["dashboard"] == str(work / "dashboard.html")
    assert state["progress"]["table"] == str(work / "progress.tsv")
    assert state["progress"]["chart"] == str(work / "progress.svg")
    assert state["progress"]["review"] == str(work / "review.md")
    assert state["progress"]["usage_source"] == f"best-effort explicit get_goal snapshots in {work / 'log.md'}"
    assert "latest_usage_snapshot" in state["progress"]
    assert state["multi_agent"]["enabled"] is False
    assert state["multi_agent"]["mode"] == "off"
    assert (work / "progress.tsv").read_text(encoding="utf-8").startswith(
        "timestamp\tcandidate\tscore\tdecision\ttokens_total\ttokens_delta\twall_seconds\tlabel"
    )
    assert "sub 1000 cycles" in (work / "best.md").read_text(encoding="utf-8")
    assert "Multi-agent mode: off" in (work / "best.md").read_text(encoding="utf-8")
    assert "Harness mode: fast" in (work / "best.md").read_text(encoding="utf-8")
    assert "Draft patch only: no" in (work / "best.md").read_text(encoding="utf-8")
    assert "- harness mode: fast" in (work / "log.md").read_text(encoding="utf-8")
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
    assert "Best Effort" in plan
    assert "Checkpoint Sidecar Queue" in plan
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
    assert template["search_accounting"]["attempts_consumed"] == 0
    assert template["search_accounting"]["coordinated_edits_required"] is False
    assert template["search_accounting"]["same_artifact_checkpoint"] is False
    assert template["search_accounting"]["force_off_hill_next"] is False
    assert template["escape"]["status"] == "tracking"
    assert template["escape"]["escape_operator"] is None
    assert template["escape"]["controlled_regression_allowed"] is False
    assert template["escape"]["operator_credit_signal"] is None
    for dirname in ("raw_logs", "results", "profiles", "PATCHES"):
        assert (work / dirname).is_dir()
    dashboard = (work / "dashboard.html").read_text(encoding="utf-8").lower()
    assert "waiting for the first measurement" in dashboard


def test_init_harness_default_uses_isolated_harness_dir(tmp_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(INIT_SCRIPT),
            "--objective",
            "default path check",
        ],
        cwd=tmp_path,
        check=True,
        text=True,
        capture_output=True,
    )

    harness = tmp_path / "work" / "optimization_harness"
    assert (harness / "state.json").exists()
    assert (harness / "progress.tsv").exists()
    assert (harness / "checkpoints" / "progress.json").exists()
    assert not (tmp_path / "work" / "state.json").exists()
    assert not (tmp_path / "work" / "progress.tsv").exists()
    state = json.loads((harness / "state.json").read_text(encoding="utf-8"))
    assert state["progress"]["table"] == "work/optimization_harness/progress.tsv"
    assert state["progress"]["chart_enabled"] is False
    assert not (harness / "progress.svg").exists()
    assert not (harness / "dashboard.html").exists()
    assert state["progress"]["sidecar"]["must_not_mutate"][0] == "work/optimization_harness/best.md"
    assert state["progress"]["sidecar"]["safe_sidecar_outputs"][0] == "work/optimization_harness/progress.svg"


def test_init_harness_can_disable_chart_placeholders(tmp_path: Path) -> None:
    work = tmp_path / "work" / "optimization_harness"

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


def test_init_harness_accepts_minimal_alias_for_fast_mode(tmp_path: Path) -> None:
    work = tmp_path / "work" / "optimization_harness"

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
    assert state["harness_mode"] == "fast"
    assert state["requested_harness_mode"] == "minimal"
    assert state["progress"]["critical_path_required"] == [
        "result_or_blocker",
        "decision",
        "next_direction",
    ]
    assert "progress_row" in state["progress"]["critical_path_best_effort"]
    assert state["progress"]["sidecar"]["enabled"] is False
    assert "Harness mode: fast (requested alias: minimal)" in (work / "best.md").read_text(encoding="utf-8")


def test_init_harness_standard_mode_has_checkpoint_sidecar_triggers(tmp_path: Path) -> None:
    work = tmp_path / "work" / "optimization_harness"

    subprocess.run(
        [
            sys.executable,
            str(INIT_SCRIPT),
            "--work-dir",
            str(work),
            "--harness-mode",
            "standard",
            "--progress-chart",
            "on",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    state = json.loads((work / "state.json").read_text(encoding="utf-8"))
    assert state["harness_mode"] == "standard"
    assert state["progress"]["sidecar"]["enabled"] is True
    assert state["progress"]["sidecar"]["policy"] == "checkpoint_only"
    assert state["progress"]["sidecar"]["refresh_triggers"] == {
        "promotion": True,
        "reassessment": True,
        "handoff": True,
        "user_request": True,
        "every_n_candidates": 10,
        "idle_only": True,
    }
    assert "dashboard_refresh" in state["progress"]["sidecar"]["forbidden_on_fast_path"]
    assert "usage_snapshot" in state["progress"]["critical_path_best_effort"]
    assert "raw_evidence_path" not in state["progress"]["critical_path_required"]


def test_init_harness_audit_mode_requires_full_reject_artifacts(tmp_path: Path) -> None:
    work = tmp_path / "work" / "optimization_harness"

    subprocess.run(
        [
            sys.executable,
            str(INIT_SCRIPT),
            "--work-dir",
            str(work),
            "--harness-mode",
            "audit",
            "--progress-chart",
            "on",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    state = json.loads((work / "state.json").read_text(encoding="utf-8"))
    assert state["harness_mode"] == "audit"
    assert state["candidate_artifacts"]["required_for_rejects"] is True
    assert state["progress"]["sidecar"]["enabled"] is True
    assert "verifier_details" in state["progress"]["checkpoint_or_audit_only"]


def test_init_harness_can_enable_multi_agent_mode(tmp_path: Path) -> None:
    work = tmp_path / "work" / "optimization_harness"

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
