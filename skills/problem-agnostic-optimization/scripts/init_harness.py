#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def placeholder_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="720" viewBox="0 0 1120 720">
<rect width="100%" height="100%" fill="#fbfbf7"/>
<rect x="92" y="72" width="943" height="318" fill="#f9fafb" stroke="#e5e7eb"/>
<rect x="92" y="475" width="943" height="165" fill="#fffbeb" stroke="#fde68a"/>
<text x="560" y="170" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="22" font-weight="700" fill="#17202a">Progress chart waiting for first measurement</text>
<text x="560" y="205" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#697386">Append measured candidate rows to work/progress.tsv.</text>
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
<p>Append one measured candidate row to <code>work/progress.tsv</code>, record any explicit <code>get_goal</code> snapshot in <code>work/log.md</code>, then regenerate this dashboard.</p>
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
        work / "log.md": log_md(args),
        work / "plan.md": plan_md(args),
        work / "review.md": review_md(args),
        work / "audit.md": audit_md(),
        work / "progress.tsv": "timestamp\tcandidate\tscore\tstatus\tdescription\n",
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

    for path in created:
        print(f"created {path}")
    for path in skipped:
        print(f"kept {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
