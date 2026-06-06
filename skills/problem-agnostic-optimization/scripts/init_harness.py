#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_text(path: Path, text: str, force: bool) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def touch(path: Path) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    path.touch(exist_ok=True)
    return not existed


def state(args: argparse.Namespace) -> dict[str, object]:
    chart_enabled = args.progress_chart == "on"
    multi_agent_enabled = args.multi_agent_mode == "on"
    return {
        "schema_version": 2,
        "target_score": None,
        "score_unit": args.metric,
        "mode": args.mode,
        "objective_source": None,
        "theoretical_floor": None,
        "best_stable_candidate": None,
        "best_stable_score": None,
        "best_benchmark_candidate": None,
        "best_benchmark_score": None,
        "fixed_budget": args.budget,
        "seed_protocol": {},
        "scenario_sets": {},
        "statistical_gate": None,
        "profiling": {
            "strength": None,
            "available_surfaces": [],
            "unavailable_surfaces": [],
            "commands": {},
            "artifact_paths": [],
            "confidence": None,
            "fallback_evidence": [],
        },
        "editable_files": [],
        "immutable_files": [],
        "candidate_artifacts": {
            "directory": str(args.work_dir / "candidates"),
            "schema": str(args.work_dir / "schemas" / "candidate_result.schema.json"),
            "required_for_promotions": True,
        },
        "breakthrough_mining": {
            "enabled": True,
            "path": str(args.work_dir / "breakthroughs.md"),
            "frontier_sources": [],
            "last_mined_at": None,
            "current_active_floor": None,
            "calibrated_screens": [],
        },
        "promotion_ladder": {
            "enabled": True,
            "gating_steps": [
                "apply_or_build",
                "correctness",
                "authoritative_metric",
                "regression_or_adversarial",
                "fresh_verifier",
                "promote",
            ],
            "advisory_steps": ["profile", "style", "local_screening"],
            "definition": str(args.work_dir / "promotion_ladder.md"),
        },
        "verifier": {
            "enabled": True,
            "mode": "fresh_environment_when_possible",
            "definition": str(args.work_dir / "verifier.md"),
            "last_verdict": None,
            "last_verified_candidate": None,
        },
        "execution_boundary": {
            "untrusted_code_sandbox": "clean_env_no_credentials_restricted_egress_when_possible",
            "draft_patch_only": False,
            "notes": [],
        },
        "isolation": {
            "fresh_run": args.fresh_run_isolation == "on",
            "allowed_prior_sources": [],
        },
        "multi_agent": {
            "enabled": multi_agent_enabled,
            "mode": args.multi_agent_mode,
            "coordinator_workspace": "canonical",
            "worker_isolation": "worktree_or_copied_sandbox",
            "active_workers": [],
            "completed_workers": [],
            "promotion_policy": "coordinator_only_authoritative_gate",
        },
        "round": 0,
        "iterations": 0,
        "stagnation_count": 0,
        "next_candidate_id": 1,
        "active_branches": [],
        "exhausted_branches": [],
        "rate_limits": {},
        "pending_jobs": [],
        "checkpoint": {
            "path": str(args.work_dir / "checkpoints" / "progress.json"),
            "current_phase": "harness_boot",
            "completed_phases": [],
            "completed_shards": [],
            "resume_policy": "skip_completed_terminal_phases_only",
        },
        "progress": {
            "logging_enabled": True,
            "chart_enabled": chart_enabled,
            "events": str(args.work_dir / "events.jsonl"),
            "dashboard": str(args.work_dir / "dashboard.html"),
            "table": str(args.work_dir / "progress.tsv"),
            "chart": str(args.work_dir / "progress.svg"),
            "review": str(args.work_dir / "review.md"),
            "x_axis": "candidate",
            "tokens_total": 0,
            "tokens_since_promotion": 0,
            "token_budget": None,
            "usage_source": "explicit get_goal snapshots in work/log.md",
            "usage_gap": None,
            "latest_usage_snapshot": {
                "source": "get_goal",
                "recorded_at": None,
                "wall_seconds": None,
                "total_tokens": None,
                "input_tokens": None,
                "cached_input_tokens": None,
                "output_tokens": None,
                "reasoning_output_tokens": None,
                "cache_creation_input_tokens": None,
                "cache_read_input_tokens": None,
            },
        },
        "audit": {
            "enabled": True,
            "report": str(args.work_dir / "audit.md"),
            "write_surface": [str(args.work_dir / "audit.md")],
            "last_audited_at": None,
            "last_verdict": None,
        },
        "last_updated": now(),
    }


def checkpoint_json(args: argparse.Namespace) -> str:
    checkpoint = {
        "schema_version": 1,
        "objective": args.objective,
        "current_phase": "harness_boot",
        "completed_phases": [],
        "phase_status": {
            "contract": "pending",
            "baseline": "pending",
            "candidate": "pending",
            "validation": "pending",
            "measurement": "pending",
            "fresh_verifier": "pending",
            "promotion": "pending",
            "handoff": "pending",
        },
        "completed_shards": [],
        "terminal_results": [],
        "resume_policy": "skip completed terminal phases; retry failed, blocked, or partial phases",
        "updated_at": now(),
    }
    return json.dumps(checkpoint, indent=2, sort_keys=True) + "\n"


def candidate_result_schema() -> str:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Problem-Agnostic Optimization Candidate Result",
        "type": "object",
        "required": [
            "schema_version",
            "candidate",
            "parent",
            "hypothesis",
            "mechanism_class",
            "commands",
            "promotion_ladder",
            "verifier",
            "decision",
        ],
        "properties": {
            "schema_version": {"type": "integer"},
            "candidate": {"type": "string"},
            "parent": {"type": ["string", "null"]},
            "parent_hash": {"type": ["string", "null"]},
            "mode": {"type": ["string", "null"]},
            "mechanism_class": {"type": "string"},
            "duplicate_check": {"type": ["string", "null"]},
            "hypothesis": {"type": "string"},
            "artifact_paths": {"type": "array", "items": {"type": "string"}},
            "raw_log_paths": {"type": "array", "items": {"type": "string"}},
            "commands": {"type": "object"},
            "correctness": {"type": ["string", "null"]},
            "authoritative_metric": {"type": "object"},
            "breakthrough": {"type": "object"},
            "screening": {"type": "object"},
            "validation_island": {"type": "object"},
            "phase_owners": {"type": "array", "items": {"type": "object"}},
            "promotion_ladder": {"type": "object"},
            "verifier": {"type": "object"},
            "decision": {"type": "string"},
            "learning": {"type": "string"},
            "created_at": {"type": ["string", "null"]},
            "updated_at": {"type": ["string", "null"]},
        },
        "additionalProperties": True,
    }
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


def candidate_result_template() -> str:
    template = {
        "schema_version": 1,
        "candidate": "cand_0001",
        "parent": None,
        "parent_hash": None,
        "mode": None,
        "mechanism_class": "",
        "duplicate_check": None,
        "hypothesis": "",
        "artifact_paths": [],
        "raw_log_paths": [],
        "commands": {
            "apply_or_build": None,
            "correctness": None,
            "authoritative_metric": None,
            "regression_or_adversarial": None,
            "fresh_verifier": None,
        },
        "correctness": None,
        "authoritative_metric": {
            "score": None,
            "unit": None,
            "direction": None,
            "raw_result_path": None,
        },
        "breakthrough": {
            "frontier_row": None,
            "active_floor": None,
            "mechanism": "",
            "resource_trade": "",
            "dependency": "",
            "slack_left_behind": [],
            "negative_result": False,
        },
        "screening": {
            "screen_metric": None,
            "calibration": {
                "known_clean_cases": [],
                "known_dirty_cases": [],
                "stacked_knob_cases": [],
                "false_clean_risk": None,
                "false_dirty_risk": None,
                "verdict": None,
            },
            "promotion_allowed": False,
        },
        "validation_island": {
            "contract_allowed": False,
            "selector": None,
            "old_island_invalidated_by": None,
            "search_space": None,
            "full_validation": None,
        },
        "phase_owners": [],
        "promotion_ladder": {
            "apply_or_build": "pending",
            "correctness": "pending",
            "authoritative_metric": "pending",
            "regression_or_adversarial": "pending",
            "fresh_verifier": "pending",
            "promote": "pending",
            "advisory": {
                "profile": "not_run",
                "style": "not_run",
                "local_screening": "not_run",
            },
        },
        "verifier": {
            "mode": "fresh_environment_when_possible",
            "verdict": None,
            "evidence": "",
            "limitations": [],
        },
        "decision": "PENDING",
        "learning": "",
        "created_at": None,
        "updated_at": None,
    }
    return json.dumps(template, indent=2, sort_keys=True) + "\n"


def verifier_md() -> str:
    return """# Fresh Verifier Gate

Use this gate before updating `work/best.md` for any meaningful promotion.

- Recreate or reset the environment when practical.
- Carry only the candidate artifact or diff, the validation command, and the recorded contract across the boundary.
- Rerun correctness before the authoritative metric.
- Treat local screening, profile deltas, and candidate rationale as advisory.
- If a fresh environment is unavailable, record the limitation in the candidate result and run the cleanest independent retest available.
- Do not expose credentials or unrelated host files to untrusted/generated target code.

Verdict values: `PASS`, `FAIL`, `INCONCLUSIVE`, or `SKIPPED_WITH_LIMITATION`.
"""


def promotion_ladder_md() -> str:
    return """# Promotion Ladder

Every promoted candidate should pass the gating steps in order:

1. `apply_or_build`: patch applies, code builds, or the candidate artifact can be loaded.
2. `correctness`: required correctness/reference/shape/seed checks pass.
3. `authoritative_metric`: the official metric improves outside the recorded noise or gate.
4. `regression_or_adversarial`: targeted regressions, hidden-risk cases, or no-exploit checks pass when applicable.
5. `fresh_verifier`: an independent/fresh retest sees only the artifact, contract, and commands.
6. `promote`: update `work/best.md`, `work/state.json`, ledgers, and dashboard.

Advisory steps such as profiles, local screening, style, and implementation neatness can explain a candidate but cannot promote it.
"""


def best_md(args: argparse.Namespace) -> str:
    return f"""# Best Known State

## Objective
Mode: {args.mode}
Target: {args.objective}
Objective source:
Authoritative metric: {args.metric}
Baseline: {args.baseline}
Budget / stopping rule: {args.budget}
Validation: {args.validation}
Progress chart: {args.progress_chart}
Fresh-run isolation: {args.fresh_run_isolation}
Multi-agent mode: {args.multi_agent_mode}

## Current Best
Current best stable:
Current best benchmark-only:
Why it wins:

## Boundaries
Editable files:
Immutable files:
Draft patch only: no
Untrusted code execution boundary: clean env, no credentials, restricted egress when possible

## Bottleneck
Confirmed bottlenecks:
Exhausted branches:
Open directions:
"""


def log_md(args: argparse.Namespace) -> str:
    return f"""# Optimization Log

## {now()} :: harness_boot

- objective: {args.objective}
- authoritative metric: {args.metric}
- baseline: {args.baseline}
- validation: {args.validation}
- progress chart: {args.progress_chart}
- multi-agent mode: {args.multi_agent_mode}
- decision: BOOTSTRAP
- learning: harness initialized before candidate work
"""


def plan_md(args: argparse.Namespace) -> str:
    return f"""# Optimization Plan

- Target: {args.objective}
- Current best: {args.baseline}
- Stagnation count: 0
- Multi-agent mode: {args.multi_agent_mode}
- Next candidate: reproduce or establish baseline before optimization

## Active Branches

## Worker Queue

Each worker packet must include parent hash, mechanism class, target lane, duplicate check, expected signal, and immutable files.

## Closed Branches
"""


def review_md(args: argparse.Namespace) -> str:
    return f"""# Progress Review

- Current best: {args.baseline}
- Best score:
- Last promotion:
- Candidates since promotion: 0
- Tokens since promotion: 0
- Token source: explicit get_goal snapshots in work/log.md
- Token gap:
- Active time:
- Wall elapsed:
- Stagnation count: 0
- Bug/crash/blocked rate: 0
- Open blockers: waiting for first measured candidate
- Reassessment trigger:
- Next candidate: reproduce or establish baseline
"""


def audit_md() -> str:
    return """# Optimization Audit

- Verdict: unknown
- Audited at:
- Scope:
- Current best:
- Latest event:
- Progress since last audit:
- Token/time burn:
- Contract issues:
- Promotion/integrity issues:
- Search-health issues:
- Blockers:
- Recommended next action:
"""


def breakthroughs_md() -> str:
    return """# Breakthrough Mining

Use this file for plateaued, high-stakes, public-leaderboard, or multi-agent runs.
Keep it compact and durable; detailed raw logs belong under `work/raw_logs/`.

## Frontier Sources

| source | snapshot/time | contract match | notes |
|---|---|---|---|

## Breakthrough Rows

| row | parent -> candidate | score/resources | active floor | delta | mechanism | proof/invariant | search tool | validation | slack/dependency |
|---:|---|---:|---|---:|---|---|---|---|---|

## Phase Owners / Co-Binders

| phase/resource owner | height/cost | next floor | evidence | proposed stack |
|---|---:|---:|---|---|

## Screen Calibration

| screen | predicts | known-clean reproduced | known-dirty rejected | stacked-knob calibration | false-clean risk | false-dirty risk | promotion use |
|---|---|---|---|---|---|---|---|

## Validation Islands / Selectors

| candidate | selector/seed/route | contract-allowed reason | invalidated prior island | full validation |
|---|---|---|---|---|

## Negative Breakthroughs

| idea | why tempting | measured blocker | resource trade | reopen condition |
|---|---|---|---|---|
"""


def placeholder_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="720" viewBox="0 0 1120 720">
<rect width="100%" height="100%" fill="#fbfbf7"/>
<rect x="92" y="72" width="943" height="318" fill="#f9fafb" stroke="#e5e7eb"/>
<rect x="92" y="475" width="943" height="165" fill="#fffbeb" stroke="#fde68a"/>
<text x="560" y="170" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="22" font-weight="700" fill="#17202a">Progress chart waiting for first measurement</text>
<text x="560" y="205" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#697386">Append measured rows with scripts/record_progress.py when available.</text>
<text x="560" y="555" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#92400e">Record explicit get_goal snapshots in work/log.md for token history.</text>
</svg>
"""


def placeholder_dashboard() -> str:
    return """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Optimization Dashboard</title></head>
<body style="font-family:Arial,Helvetica,sans-serif;background:#f7f7f2;color:#17202a;margin:40px">
<main style="max-width:860px;margin:auto;background:#fff;border:1px solid #ded8cc;border-radius:8px;padding:28px">
<h1>Optimization Dashboard</h1>
<p>Waiting for the first measurement.</p>
<p>Append one measured candidate row with <code>scripts/record_progress.py</code>, try to record a <code>get_goal</code> snapshot in <code>work/log.md</code>, then regenerate this dashboard.</p>
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize the optimization harness quickly.")
    parser.add_argument("--work-dir", type=Path, default=Path("work"))
    parser.add_argument("--objective", default="unknown")
    parser.add_argument("--metric", default="authoritative metric")
    parser.add_argument("--baseline", default="unknown, reproduce first")
    parser.add_argument("--budget", default="not recorded")
    parser.add_argument("--validation", default="not recorded")
    parser.add_argument("--mode", default="clean leaderboard")
    parser.add_argument("--progress-chart", choices=("on", "off"), default="on")
    parser.add_argument("--fresh-run-isolation", choices=("on", "off"), default="on")
    parser.add_argument("--multi-agent-mode", choices=("on", "off"), default="off")
    parser.add_argument("--force", action="store_true", help="Overwrite existing harness files")
    args = parser.parse_args()

    work = args.work_dir
    created: list[str] = []
    skipped: list[str] = []

    files = {
        work / "best.md": best_md(args),
        work / "breakthroughs.md": breakthroughs_md(),
        work / "log.md": log_md(args),
        work / "plan.md": plan_md(args),
        work / "review.md": review_md(args),
        work / "audit.md": audit_md(),
        work / "verifier.md": verifier_md(),
        work / "promotion_ladder.md": promotion_ladder_md(),
        work / "checkpoints" / "progress.json": checkpoint_json(args),
        work / "schemas" / "candidate_result.schema.json": candidate_result_schema(),
        work / "candidates" / "_template.result.json": candidate_result_template(),
        work / "progress.tsv": "timestamp\tcandidate\tscore\tdecision\ttokens_total\ttokens_delta\twall_seconds\tlabel\n",
        work / "state.json": json.dumps(state(args), indent=2, sort_keys=True) + "\n",
    }
    if args.progress_chart == "on":
        files[work / "progress.svg"] = placeholder_svg()
        files[work / "dashboard.html"] = placeholder_dashboard()

    for path, text in files.items():
        if write_text(path, text, args.force):
            created.append(str(path))
        else:
            skipped.append(str(path))

    events_path = work / "events.jsonl"
    if args.force:
        events_path.write_text("", encoding="utf-8")
        created.append(str(events_path))
    elif touch(events_path):
        created.append(str(events_path))
    else:
        skipped.append(str(events_path))

    for dirname in ("raw_logs", "results", "profiles", "PATCHES"):
        path = work / dirname
        path.mkdir(parents=True, exist_ok=True)

    for path in created:
        print(f"created {path}")
    for path in skipped:
        print(f"kept {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
