#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Iterable


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


def to_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def first_present(row: dict[str, str], names: Iterable[str]) -> str | None:
    for name in names:
        if name in row:
            return row[name]
    return None


def read_points(path: Path) -> list[Point]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if reader.fieldnames is None:
            raise SystemExit(f"{path} is missing a TSV header")

        points: list[Point] = []
        token_total = 0.0
        for i, row in enumerate(reader):
            score = to_float(first_present(row, ["score", "authoritative_score", "metric"]))
            total = to_float(first_present(row, ["tokens_total", "total_tokens", "cumulative_tokens"]))
            delta = to_float(first_present(row, ["tokens_delta", "token_delta"]))
            if total is None and delta is not None:
                token_total += delta
                total = token_total
            elif total is not None:
                token_total = total

            candidate = (first_present(row, ["candidate", "id"]) or f"cand_{i:04d}").strip()
            decision = (first_present(row, ["decision", "status"]) or "").strip().lower()
            label = (first_present(row, ["label", "description", "hypothesis"]) or "").strip()
            points.append(Point(i, candidate, score, decision, label, total))

    if not points:
        raise SystemExit(f"{path} has no data rows")
    return points


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


def running_best(points: list[Point], direction: str) -> list[tuple[int, float]]:
    best: float | None = None
    series: list[tuple[int, float]] = []
    for p in points:
        if p.score is None:
            continue
        eligible = p.decision in BEST_DECISIONS or (p.row == 0 and not p.decision)
        if eligible and (best is None or improves(p.score, best, direction)):
            best = p.score
        if best is not None:
            series.append((p.row, best))
    return series


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


def render_svg(points: list[Point], output: Path, title: str, ylabel: str, direction: str) -> None:
    score_values = [p.score for p in points if p.score is not None]
    if not score_values:
        raise SystemExit("progress data has no numeric score values")

    token_values = [p.tokens_total for p in points if p.tokens_total is not None]
    x_min, x_max = 0, max(1, len(points) - 1)
    score_min, score_max = nice_range(score_values)
    token_min, token_max = token_range(token_values)

    def x(row: int) -> float:
        return LEFT + (row - x_min) / (x_max - x_min) * PLOT_W

    def y_score(score: float) -> float:
        return TOP + (score_max - score) / (score_max - score_min) * PLOT_H

    def y_token(tokens: float) -> float:
        return TOP + (token_max - tokens) / (token_max - token_min) * PLOT_H

    best = running_best(points, direction)
    best_svg = polyline([(x(row), y_score(score)) for row, score in best], "#169c55", 2)
    token_svg = polyline(
        [(x(p.row), y_token(p.tokens_total)) for p in points if p.tokens_total is not None],
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

    for i in range(0, len(points), max(1, len(points) // 10)):
        xx = x(i)
        parts.append(f'<line x1="{xx:.2f}" y1="{TOP}" x2="{xx:.2f}" y2="{HEIGHT - BOTTOM}" stroke="#f1eee7"/>')
        parts.append(f'<text x="{xx:.2f}" y="{HEIGHT - BOTTOM + 24}" text-anchor="middle" class="small">{i}</text>')

    for value in ticks(token_min, token_max):
        yy = y_token(value)
        parts.append(f'<text x="{WIDTH - RIGHT + 10}" y="{yy + 4:.2f}" fill="{TOKEN}" class="small">{value / 1000:.3g}k</text>')

    parts.extend(
        [
            f'<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{HEIGHT - BOTTOM}" stroke="{AXIS}"/>',
            f'<line x1="{WIDTH - RIGHT}" y1="{TOP}" x2="{WIDTH - RIGHT}" y2="{HEIGHT - BOTTOM}" stroke="{TOKEN}"/>',
            f'<line x1="{LEFT}" y1="{HEIGHT - BOTTOM}" x2="{WIDTH - RIGHT}" y2="{HEIGHT - BOTTOM}" stroke="{AXIS}"/>',
            f'<text x="{WIDTH / 2:.1f}" y="{HEIGHT - 22}" text-anchor="middle" class="axis">Candidate #</text>',
            f'<text x="22" y="{HEIGHT / 2:.1f}" transform="rotate(-90 22 {HEIGHT / 2:.1f})" text-anchor="middle" class="axis">{escape(ylabel)}</text>',
            f'<text x="{WIDTH - 24}" y="{HEIGHT / 2:.1f}" transform="rotate(90 {WIDTH - 24} {HEIGHT / 2:.1f})" text-anchor="middle" fill="{TOKEN}" class="axis">Cumulative tokens</text>',
            best_svg,
            token_svg,
        ]
    )

    for p in points:
        if p.score is None:
            continue
        xx = x(p.row)
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
    parser = argparse.ArgumentParser(description="Render optimization progress from work/progress.tsv.")
    parser.add_argument("input", type=Path, help="TSV with candidate, score, decision, and token columns")
    parser.add_argument("-o", "--output", type=Path, default=Path("work/progress.svg"))
    parser.add_argument("--title", default="Optimization Progress")
    parser.add_argument("--ylabel", default="Authoritative metric")
    parser.add_argument("--direction", choices=("lower", "higher"), default="lower")
    args = parser.parse_args()

    points = read_points(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    render_svg(points, args.output, args.title, args.ylabel, args.direction)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
