#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from progress_chart import generated_at_value, infer_log_path, infer_state_path, read_points, render_svg
from progress_dashboard import render_dashboard


def main() -> int:
    parser = argparse.ArgumentParser(description="Render progress.svg and dashboard.html from one progress ledger.")
    parser.add_argument("input", type=Path, nargs="?", default=Path("work/progress.tsv"))
    parser.add_argument("--chart-output", type=Path, default=Path("work/progress.svg"))
    parser.add_argument("--dashboard-output", type=Path, default=Path("work/dashboard.html"))
    parser.add_argument("--log", type=Path, help="Log file containing explicit get_goal token snapshots; defaults to input sibling log.md")
    parser.add_argument("--state", type=Path, help="State file with current best/latest usage snapshot; defaults to input sibling state.json")
    parser.add_argument("--title", default="Optimization Progress")
    parser.add_argument("--ylabel", default="Authoritative metric")
    parser.add_argument("--direction", choices=("lower", "higher"), default="lower")
    parser.add_argument("--x-axis", choices=("candidate", "tokens", "active", "wall"), default="candidate")
    parser.add_argument("--target", type=float, help="Target score line for the SVG and embedded dashboard chart")
    parser.add_argument("--hide-before-candidate", type=int, default=3, help="Hide early candidate numbers below this value when possible")
    parser.add_argument("--score-scale", choices=("auto", "log", "linear"), default="auto", help="Score y-axis scale for the SVG")
    parser.add_argument("--generated-at", help="Fixed generation timestamp for deterministic output; ISO-8601, normalized to UTC Z")
    parser.add_argument("--no-generated-at", action="store_true", help="Omit the SVG generated timestamp footer")
    parser.add_argument("--rows", type=int, default=30, help="Recent rows to include in the dashboard table")
    args = parser.parse_args()

    generated_at = generated_at_value(args.generated_at, args.no_generated_at)
    points = read_points(args.input)
    args.chart_output.parent.mkdir(parents=True, exist_ok=True)
    render_svg(
        points,
        args.chart_output,
        args.title,
        args.ylabel,
        args.direction,
        args.x_axis,
        infer_log_path(args.input, args.log),
        infer_state_path(args.input, args.state),
        args.target,
        args.hide_before_candidate,
        args.score_scale,
        generated_at,
    )

    html = render_dashboard(
        args.input,
        args.title,
        args.ylabel,
        args.direction,
        args.x_axis,
        args.rows,
        None,
        args.target,
        args.hide_before_candidate,
        args.score_scale,
        generated_at,
        args.log,
        args.state,
    )
    args.dashboard_output.parent.mkdir(parents=True, exist_ok=True)
    args.dashboard_output.write_text(html, encoding="utf-8")
    print(args.chart_output)
    print(args.dashboard_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
