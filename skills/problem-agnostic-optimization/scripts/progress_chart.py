#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from datetime import datetime
from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
from typing import Any, Iterable


WIDTH = 1200
HEIGHT = 560
LEFT = 82
RIGHT = 110
TOP = 52
BOTTOM = 78
PLOT_W = WIDTH - LEFT - RIGHT
PLOT_H = HEIGHT - TOP - BOTTOM
BG = "#fbfbf7"
PANEL = "#ffffff"
GRID = "#e8e4da"
TEXT = "#1f2933"
MUTED = "#6b7280"
AXIS = "#2f2f2f"
DISCARDED = "#c7c7c7"
KEEP = "#18a058"
TOKEN = "#2563eb"
BAD = "#dc2626"

BEST_DECISIONS = {"baseline", "promote", "promoted", "keep", "kept"}
KEEP_DECISIONS = BEST_DECISIONS | {"keep variant", "verify"}
BAD_DECISIONS = {"bug", "crash", "blocked"}


@dataclass
class Point:
    row: int
    candidate: str
    score: float | None
    decision: str
    label: str
    tokens_total: float | None
    active_seconds: float | None
    wall_seconds: float | None


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def to_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def nested_value(row: dict[str, Any], name: str) -> Any:
    value: Any = row
    for part in name.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def first_present(row: dict[str, Any], names: Iterable[str]) -> Any:
    for name in names:
        value = nested_value(row, name)
        if value is not None:
            return value
    return None


def parse_timestamp(value: Any) -> float | None:
    text = to_text(value)
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        return datetime.fromisoformat(text).timestamp()
    except ValueError:
        return None


def make_point(row_index: int, row: dict[str, Any], token_total: float) -> tuple[Point, float]:
    score = to_float(first_present(row, ["score", "authoritative_score", "metric", "benchmark.score", "ranked.score"]))
    total = to_float(first_present(row, ["tokens_total", "total_tokens", "cumulative_tokens", "goal_tokens_used", "run_tokens_used"]))
    delta = to_float(first_present(row, ["tokens_delta", "token_delta", "run_tokens_delta"]))
    if total is None and delta is not None:
        token_total += delta
        total = token_total
    elif total is not None:
        token_total = total

    active_seconds = to_float(
        first_present(
            row,
            [
                "active_seconds",
                "active_time_seconds",
                "run_active_seconds",
                "run_tracked_elapsed_seconds",
                "goal_time_used_seconds",
            ],
        )
    )
    wall_seconds = to_float(first_present(row, ["wall_seconds", "wall_elapsed_seconds", "elapsed_seconds"]))
    candidate = to_text(first_present(row, ["candidate", "id"])) or f"cand_{row_index:04d}"
    decision = (to_text(first_present(row, ["decision", "status", "event"])) or "").lower()
    label = to_text(first_present(row, ["label", "description", "hypothesis"])) or ""
    point = Point(row_index, candidate, score, decision, label, total, active_seconds, wall_seconds)
    return point, token_total


def read_tsv_points(path: Path) -> list[Point]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if reader.fieldnames is None:
            raise SystemExit(f"{path} is missing a TSV header")

        points: list[Point] = []
        token_total = 0.0
        for i, row in enumerate(reader):
            point, token_total = make_point(i, row, token_total)
            points.append(point)

    if not points:
        raise SystemExit(f"{path} has no data rows")
    return points


def read_jsonl_points(path: Path) -> list[Point]:
    points: list[Point] = []
    token_total = 0.0
    first_timestamp: float | None = None

    with path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                row = json.loads(text)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number} is invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise SystemExit(f"{path}:{line_number} must be a JSON object")

            point, token_total = make_point(len(points), row, token_total)
            timestamp = parse_timestamp(first_present(row, ["checkpoint_timestamp", "timestamp", "created_at"]))
            if point.wall_seconds is None and timestamp is not None:
                if first_timestamp is None:
                    first_timestamp = timestamp
                point.wall_seconds = max(0.0, timestamp - first_timestamp)
            points.append(point)

    if not points:
        raise SystemExit(f"{path} has no data rows")
    return points


def read_points(path: Path) -> list[Point]:
    if path.suffix == ".jsonl":
        return read_jsonl_points(path)
    return read_tsv_points(path)


def nice_range(values: list[float]) -> tuple[float, float]:
    lo = min(values)
    hi = max(values)
    if lo == hi:
        pad = abs(lo) * 0.05 or 1.0
        return lo - pad, hi + pad
    pad = (hi - lo) * 0.08
    return lo - pad, hi + pad


def ticks(lo: float, hi: float, count: int = 6) -> list[float]:
    if count <= 1:
        return [lo]
    step = (hi - lo) / (count - 1)
    return [lo + i * step for i in range(count)]


def score_color(decision: str) -> str:
    if decision in BEST_DECISIONS:
        return KEEP
    if decision in KEEP_DECISIONS:
        return "#0ea5e9"
    if decision in BAD_DECISIONS:
        return BAD
    return DISCARDED


def improves(score: float, best: float, direction: str) -> bool:
    return score < best if direction == "lower" else score > best


def polyline(points: list[tuple[float, float]], color: str, width: int = 2) -> str:
    if len(points) < 2:
        return ""
    coords = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>'


def token_range(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 1.0
    hi = max(values)
    if hi <= 0:
        return 0.0, 1.0
    return 0.0, hi * 1.08


def x_axis_value(point: Point, x_axis: str) -> float | None:
    if x_axis == "candidate":
        return float(point.row)
    if x_axis == "tokens":
        return point.tokens_total
    if x_axis == "active":
        return point.active_seconds
    if x_axis == "wall":
        return point.wall_seconds
    raise ValueError(f"unknown x-axis: {x_axis}")


def x_axis_label(x_axis: str) -> str:
    return {
        "candidate": "Candidate #",
        "tokens": "Cumulative tokens",
        "active": "Tracked active time",
        "wall": "Wall elapsed time",
    }[x_axis]


def format_x_tick(value: float, x_axis: str) -> str:
    if x_axis == "candidate":
        return f"{value:.0f}"
    if x_axis == "tokens":
        return f"{value / 1000:.3g}k"
    if x_axis in {"active", "wall"}:
        if value >= 3600:
            return f"{value / 3600:.3g}h"
        if value >= 60:
            return f"{value / 60:.3g}m"
        return f"{value:.3g}s"
    return f"{value:.3g}"


def x_range(values: list[float]) -> tuple[float, float]:
    hi = max(values)
    if hi <= 0:
        return 0.0, 1.0
    return 0.0, hi * 1.03


def x_ticks(values: list[float], x_axis: str) -> list[float]:
    if x_axis == "candidate":
        hi = int(max(values))
        step = max(1, hi // 10 or 1)
        tick_values = list(range(0, hi + 1, step))
        if tick_values[-1] != hi:
            tick_values.append(hi)
        return [float(value) for value in tick_values]
    return ticks(0.0, max(values) * 1.03 if max(values) > 0 else 1.0)


def running_best(points: list[Point], direction: str, x_axis: str) -> list[tuple[float, float]]:
    best: float | None = None
    series: list[tuple[float, float]] = []
    for p in points:
        x_value = x_axis_value(p, x_axis)
        if p.score is None or x_value is None:
            continue
        eligible = p.decision in BEST_DECISIONS or (p.row == 0 and not p.decision)
        if eligible and (best is None or improves(p.score, best, direction)):
            best = p.score
        if best is not None:
            series.append((x_value, best))
    return series


def render_svg(points: list[Point], output: Path, title: str, ylabel: str, direction: str, x_axis: str) -> None:
    score_values = [p.score for p in points if p.score is not None]
    if not score_values:
        raise SystemExit("progress data has no numeric score values")

    token_values = [p.tokens_total for p in points if p.tokens_total is not None]
    x_values = [value for p in points if (value := x_axis_value(p, x_axis)) is not None]
    if not x_values:
        raise SystemExit(f"progress data has no values for x-axis {x_axis!r}")
    x_min, x_max = x_range(x_values)
    score_min, score_max = nice_range(score_values)
    token_min, token_max = token_range(token_values)

    def x(value: float) -> float:
        return LEFT + (value - x_min) / (x_max - x_min) * PLOT_W

    def y_score(score: float) -> float:
        return TOP + (score_max - score) / (score_max - score_min) * PLOT_H

    def y_token(tokens: float) -> float:
        return TOP + (token_max - tokens) / (token_max - token_min) * PLOT_H

    best = running_best(points, direction, x_axis)
    best_svg = polyline([(x(value), y_score(score)) for value, score in best], "#169c55", 2)
    token_svg = polyline(
        [
            (x(x_value), y_token(p.tokens_total))
            for p in points
            if p.tokens_total is not None and (x_value := x_axis_value(p, x_axis)) is not None
        ],
        "#2563eb",
        2,
    )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        "<style>text{font-family:Inter,Arial,Helvetica,sans-serif;font-size:13px;fill:#1f2933}.small{font-size:11px;fill:#6b7280}.title{font-size:20px;font-weight:700}.axis{font-weight:600}.legend{font-size:12px}</style>",
        f'<rect width="100%" height="100%" fill="{BG}"/>',
        f'<rect x="{LEFT}" y="{TOP}" width="{PLOT_W}" height="{PLOT_H}" rx="6" fill="{PANEL}" stroke="#ddd8cd"/>',
        f'<text x="{WIDTH / 2:.1f}" y="30" text-anchor="middle" class="title">{escape(title)}</text>',
    ]

    for value in ticks(score_min, score_max):
        yy = y_score(value)
        parts.append(f'<line x1="{LEFT}" y1="{yy:.2f}" x2="{WIDTH - RIGHT}" y2="{yy:.2f}" stroke="{GRID}"/>')
        parts.append(f'<text x="{LEFT - 10}" y="{yy + 4:.2f}" text-anchor="end" class="small">{value:.4g}</text>')

    for value in x_ticks(x_values, x_axis):
        xx = x(value)
        parts.append(f'<line x1="{xx:.2f}" y1="{TOP}" x2="{xx:.2f}" y2="{HEIGHT - BOTTOM}" stroke="#f1eee7"/>')
        parts.append(f'<text x="{xx:.2f}" y="{HEIGHT - BOTTOM + 24}" text-anchor="middle" class="small">{format_x_tick(value, x_axis)}</text>')

    for value in ticks(token_min, token_max):
        yy = y_token(value)
        parts.append(f'<text x="{WIDTH - RIGHT + 10}" y="{yy + 4:.2f}" fill="{TOKEN}" class="small">{value / 1000:.3g}k</text>')

    parts.extend(
        [
            f'<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{HEIGHT - BOTTOM}" stroke="{AXIS}"/>',
            f'<line x1="{WIDTH - RIGHT}" y1="{TOP}" x2="{WIDTH - RIGHT}" y2="{HEIGHT - BOTTOM}" stroke="{TOKEN}"/>',
            f'<line x1="{LEFT}" y1="{HEIGHT - BOTTOM}" x2="{WIDTH - RIGHT}" y2="{HEIGHT - BOTTOM}" stroke="{AXIS}"/>',
            f'<text x="{WIDTH / 2:.1f}" y="{HEIGHT - 22}" text-anchor="middle" class="axis">{x_axis_label(x_axis)}</text>',
            f'<text x="22" y="{HEIGHT / 2:.1f}" transform="rotate(-90 22 {HEIGHT / 2:.1f})" text-anchor="middle" class="axis">{escape(ylabel)}</text>',
            f'<text x="{WIDTH - 24}" y="{HEIGHT / 2:.1f}" transform="rotate(90 {WIDTH - 24} {HEIGHT / 2:.1f})" text-anchor="middle" fill="{TOKEN}" class="axis">Cumulative tokens</text>',
            best_svg,
            token_svg,
        ]
    )

    for p in points:
        x_value = x_axis_value(p, x_axis)
        if p.score is None or x_value is None:
            continue
        xx = x(x_value)
        yy = y_score(p.score)
        color = score_color(p.decision)
        opacity = "0.96" if color != DISCARDED else "0.56"
        radius = "4.8" if p.decision in BEST_DECISIONS else "3.6"
        stroke = PANEL if p.decision in BEST_DECISIONS else "none"
        parts.append(f'<circle cx="{xx:.2f}" cy="{yy:.2f}" r="{radius}" fill="{color}" opacity="{opacity}" stroke="{stroke}" stroke-width="1.5"/>')
        if p.decision in BEST_DECISIONS and p.label:
            label = escape(p.label[:54])
            parts.append(f'<text x="{xx + 8:.2f}" y="{yy - 7:.2f}" fill="{KEEP}" class="small" transform="rotate(-25 {xx + 8:.2f} {yy - 7:.2f})">{label}</text>')

    legend_x = WIDTH - RIGHT - 160
    legend_y = TOP + 8
    parts.extend(
        [
            f'<rect x="{legend_x}" y="{legend_y - 16}" width="150" height="72" rx="6" fill="white" stroke="#ddd8cd"/>',
            f'<circle cx="{legend_x + 14}" cy="{legend_y}" r="4" fill="{DISCARDED}" opacity="0.56"/><text x="{legend_x + 26}" y="{legend_y + 4}" class="legend">Discarded</text>',
            f'<circle cx="{legend_x + 14}" cy="{legend_y + 20}" r="4.8" fill="{KEEP}"/><text x="{legend_x + 26}" y="{legend_y + 24}" class="legend">Promoted/kept</text>',
            f'<line x1="{legend_x + 7}" y1="{legend_y + 40}" x2="{legend_x + 21}" y2="{legend_y + 40}" stroke="{KEEP}" stroke-width="2.5" stroke-linecap="round"/><text x="{legend_x + 26}" y="{legend_y + 44}" class="legend">Running best</text>',
            f'<line x1="{legend_x + 7}" y1="{legend_y + 60}" x2="{legend_x + 21}" y2="{legend_y + 60}" stroke="{TOKEN}" stroke-width="2.5" stroke-linecap="round"/><text x="{legend_x + 26}" y="{legend_y + 64}" class="legend">Tokens</text>',
        ]
    )

    parts.append("</svg>")
    output.write_text("\n".join(part for part in parts if part), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render optimization progress from work/progress.tsv or work/events.jsonl.")
    parser.add_argument("input", type=Path, help="TSV or JSONL with candidate, score, decision, and token columns")
    parser.add_argument("-o", "--output", type=Path, default=Path("work/progress.svg"))
    parser.add_argument("--title", default="Optimization Progress")
    parser.add_argument("--ylabel", default="Authoritative metric")
    parser.add_argument("--direction", choices=("lower", "higher"), default="lower")
    parser.add_argument("--x-axis", choices=("candidate", "tokens", "active", "wall"), default="candidate")
    args = parser.parse_args()

    points = read_points(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    render_svg(points, args.output, args.title, args.ylabel, args.direction, args.x_axis)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
