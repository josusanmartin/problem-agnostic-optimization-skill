#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
import json
import math
import os
from pathlib import Path
import re
from typing import Any, Iterable


WIDTH = 1120
HEIGHT = 720
LEFT = 92
RIGHT = 85
PLOT_RIGHT = WIDTH - RIGHT
PLOT_W = PLOT_RIGHT - LEFT
SCORE_Y = 72
SCORE_H = 318
TOKEN_Y = 475
TOKEN_H = 165
BG = "#ffffff"
SCORE_PANEL = "#f9fafb"
TOKEN_PANEL = "#fffbeb"
UNKNOWN = "#f3f4f6"
GRID = "#e5e7eb"
TOKEN_GRID = "#fde68a"
TEXT = "#111827"
MUTED = "#4b5563"
SUBTLE = "#6b7280"
GREEN = "#059669"
BLUE = "#2563eb"
ORANGE = "#f59e0b"
ORANGE_DARK = "#d97706"
AMBER_TEXT = "#92400e"
RED = "#dc2626"
RED_TEXT = "#b91c1c"
MEASURED = "#9ca3af"

BEST_DECISIONS = {"baseline", "promote", "promoted"}
KEEP_DECISIONS = {"keep", "kept", "keep variant", "verify", "tie", "tied"}
BAD_DECISIONS = {"bug", "crash", "blocked", "fail", "failed", "wrong", "incorrect"}
REJECT_DECISIONS = {"reject", "rejected", "discard", "discarded"}
SKILL_URL = "https://github.com/josusanmartin/problem-agnostic-optimization-skill"
SKILL_LINK_TEXT = SKILL_URL


@dataclass
class Point:
    row: int
    candidate: str
    candidate_number: float
    score: float | None
    decision: str
    label: str
    tokens_total: float | None
    active_seconds: float | None
    wall_seconds: float | None


@dataclass
class TokenSnapshot:
    label: str
    wall_seconds: float | None
    total_tokens: float | None
    input_tokens: float | None = None
    cached_input_tokens: float | None = None
    output_tokens: float | None = None
    reasoning_output_tokens: float | None = None
    cache_creation_input_tokens: float | None = None
    cache_read_input_tokens: float | None = None
    best_score: float | None = None
    timestamp: float | None = None
    source: str = "get_goal"


def to_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    multiplier = 1.0
    if text[-1:].lower() == "k":
        multiplier = 1_000.0
        text = text[:-1]
    elif text[-1:].lower() == "m":
        multiplier = 1_000_000.0
        text = text[:-1]
    try:
        number = float(text) * multiplier
    except ValueError:
        return None
    return number if math.isfinite(number) else None


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


def utc_timestamp(value: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError("timestamp cannot be empty")
    candidate = f"{text[:-1]}+00:00" if text.endswith("Z") else text
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def timestamp_from_epoch(value: str) -> str:
    seconds = int(value.strip())
    return datetime.fromtimestamp(seconds, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generated_at_value(explicit: str | None = None, omit: bool = False) -> str | None:
    if omit:
        return None
    if explicit is not None:
        try:
            return utc_timestamp(explicit)
        except ValueError as exc:
            raise SystemExit("--generated-at must be an ISO-8601 timestamp") from exc
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        try:
            return timestamp_from_epoch(epoch)
        except ValueError as exc:
            raise SystemExit("SOURCE_DATE_EPOCH must be an integer Unix timestamp") from exc
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def candidate_number(text: str, row_index: int, explicit: Any = None) -> float:
    parsed = to_float(explicit)
    if parsed is not None:
        return parsed

    stripped = text.strip()
    if re.fullmatch(r"\d+", stripped):
        return float(int(stripped))

    match = re.fullmatch(r"(?:cand|candidate|c)[_\-\s]?0*(\d+)", stripped, re.IGNORECASE)
    if match:
        return float(int(match.group(1)))

    return float(row_index)


def make_point(row_index: int, row: dict[str, Any], token_total: float) -> tuple[Point, float]:
    candidate = to_text(first_present(row, ["candidate", "id"])) or f"cand_{row_index:04d}"
    score = to_float(
        first_present(
            row,
            [
                "score",
                "authoritative_score",
                "metric",
                "cycles",
                "runtime",
                "latency",
                "benchmark.score",
                "ranked.score",
            ],
        )
    )
    total = to_float(
        first_present(
            row,
            [
                "tokens_total",
                "total_tokens",
                "cumulative_tokens",
                "token_consumption_cumulative",
                "cumulative_token_consumption",
                "goal_tokens_used",
                "run_tokens_used",
            ],
        )
    )
    delta = to_float(first_present(row, ["tokens_delta", "token_delta", "token_consumption_delta", "run_tokens_delta"]))
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
    decision = (to_text(first_present(row, ["decision", "status", "event"])) or "").lower()
    label = to_text(first_present(row, ["label", "description", "hypothesis"])) or ""
    point = Point(
        row_index,
        candidate,
        candidate_number(candidate, row_index, first_present(row, ["candidate_number", "candidate_index", "candidate_idx"])),
        score,
        decision,
        label,
        total,
        active_seconds,
        wall_seconds,
    )
    return point, token_total


def read_tsv_points(path: Path) -> list[Point]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if reader.fieldnames is None:
            raise SystemExit(f"{path} is missing a TSV header")

        points: list[Point] = []
        token_total = 0.0
        first_timestamp: float | None = None
        for i, row in enumerate(reader):
            point, token_total = make_point(i, row, token_total)
            timestamp = parse_timestamp(first_present(row, ["checkpoint_timestamp", "timestamp", "created_at"]))
            if point.wall_seconds is None and timestamp is not None:
                if first_timestamp is None:
                    first_timestamp = timestamp
                point.wall_seconds = max(0.0, timestamp - first_timestamp)
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


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    out: dict[str, Any] = {}
    for key, item in value.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        out[name] = item
        if isinstance(item, dict):
            out.update(flatten(item, name))
    return out


def norm_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


def find_value(flat: dict[str, Any], names: Iterable[str]) -> Any:
    normalized = {norm_key(name) for name in names}
    for key, value in flat.items():
        key_norm = norm_key(key)
        last_norm = norm_key(key.split(".")[-1])
        if key_norm in normalized or last_norm in normalized:
            return value
        for name in normalized:
            if key_norm.endswith(name):
                return value
    return None


def find_number(flat: dict[str, Any], names: Iterable[str]) -> float | None:
    return to_float(find_value(flat, names))


def find_text(flat: dict[str, Any], names: Iterable[str]) -> str | None:
    return to_text(find_value(flat, names))


def context_label(context: str) -> str | None:
    for pattern in (r"\bC\s*[-_ ]?(\d+)\b", r"\bcand(?:idate)?[_ -]?(\d+)\b", r"\bplateau audit\b"):
        match = re.search(pattern, context, re.IGNORECASE)
        if not match:
            continue
        if "plateau" in match.group(0).lower():
            return "plateau audit"
        return f"C{int(match.group(1))}"
    return None


def snapshot_from_mapping(obj: dict[str, Any], context: str = "") -> TokenSnapshot | None:
    flat = flatten(obj)
    context_lower = context.lower()
    explicit = (
        "get_goal" in context_lower
        or "goal" in context_lower
        or find_value(flat, ["tokensUsed", "timeUsedSeconds"]) is not None
        or any("total_token_usage" in key or "token_usage" in key for key in flat)
    )
    if not explicit:
        return None

    total = find_number(flat, ["tokensUsed", "tokens_total", "total_tokens", "totalTokens"])
    input_tokens = find_number(flat, ["input_tokens", "inputTokens"])
    cached_input_tokens = find_number(
        flat,
        ["cached_input_tokens", "cachedTokens", "cached_tokens", "input_tokens_details.cached_tokens"],
    )
    output_tokens = find_number(flat, ["output_tokens", "outputTokens"])
    reasoning_output_tokens = find_number(flat, ["reasoning_output_tokens", "reasoningTokens", "reasoning_tokens"])
    cache_creation_input_tokens = find_number(flat, ["cache_creation_input_tokens", "cacheCreationInputTokens"])
    cache_read_input_tokens = find_number(flat, ["cache_read_input_tokens", "cacheReadInputTokens"])
    if total is None:
        anthropic_total = sum(
            value or 0.0
            for value in [input_tokens, cache_creation_input_tokens, cache_read_input_tokens, output_tokens]
        )
        openai_total = sum(value or 0.0 for value in [input_tokens, output_tokens])
        total = anthropic_total if (cache_creation_input_tokens or cache_read_input_tokens) else openai_total or None

    wall = find_number(
        flat,
        [
            "timeUsedSeconds",
            "elapsedSeconds",
            "elapsed_time_seconds",
            "elapsed_wall_seconds",
            "wall_seconds",
            "wall_elapsed_seconds",
            "active_seconds",
            "time_used_seconds",
        ],
    )
    timestamp = parse_timestamp(find_value(flat, ["timestamp", "recorded_at", "created_at", "updated_at"]))
    if total is None and wall is None:
        return None

    label = (
        find_text(flat, ["candidate", "current_candidate", "latest_candidate", "label", "snapshot_label", "event"])
        or context_label(context)
        or "snapshot"
    )
    best = find_number(
        flat,
        ["best_stable_score", "best_score", "current_best", "protected_best", "progress.best_stable_score"],
    )
    return TokenSnapshot(
        label=label,
        wall_seconds=wall,
        total_tokens=total,
        input_tokens=input_tokens,
        cached_input_tokens=cached_input_tokens,
        output_tokens=output_tokens,
        reasoning_output_tokens=reasoning_output_tokens,
        cache_creation_input_tokens=cache_creation_input_tokens,
        cache_read_input_tokens=cache_read_input_tokens,
        best_score=best,
        timestamp=timestamp,
    )


def json_objects(text: str) -> Iterable[tuple[dict[str, Any], int, int]]:
    decoder = json.JSONDecoder()
    index = 0
    while True:
        start = text.find("{", index)
        if start < 0:
            return
        try:
            obj, end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            index = start + 1
            continue
        index = start + max(end, 1)
        if isinstance(obj, dict):
            yield obj, start, index


def nearby_text(text: str, start: int, end: int) -> str:
    line_start = text.rfind("\n", 0, start)
    for _ in range(2):
        previous = text.rfind("\n", 0, line_start)
        if previous < 0:
            break
        line_start = previous
    line_end = text.find("\n", end)
    for _ in range(2):
        if line_end < 0:
            line_end = len(text)
            break
        next_end = text.find("\n", line_end + 1)
        if next_end < 0:
            line_end = len(text)
            break
        line_end = next_end
    return text[max(0, line_start) : line_end]


def parse_duration(value: str, unit: str) -> float:
    number = float(value.replace(",", ""))
    unit = unit.lower()
    if unit.startswith("h"):
        return number * 3600.0
    if unit.startswith("m"):
        return number * 60.0
    return number


def parse_snapshot_line(line: str) -> TokenSnapshot | None:
    lower = line.lower()
    if "tokens" not in lower or not any(marker in lower for marker in ["get_goal", "snapshot", "usage", "token usage"]):
        return None
    token_match = re.search(r"([0-9][0-9,]*(?:\.[0-9]+)?\s*[kKmM]?)\s*(?:total\s*)?tokens\b", line)
    if token_match is None:
        token_match = re.search(r"\btokensUsed\s*=\s*([0-9][0-9,]*(?:\.[0-9]+)?\s*[kKmM]?)\b", line)
    time_match = re.search(r"(?:at|elapsed|wall|time)\s*[:=]?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(h|hr|hrs|hour|hours|m|min|mins|minute|minutes|s|sec|secs|second|seconds)\b", line, re.IGNORECASE)
    time_seconds_match = None
    if time_match is None:
        time_seconds_match = re.search(r"\btimeUsedSeconds\s*=\s*([0-9][0-9,]*(?:\.[0-9]+)?)\b", line)
    if not token_match or not time_match:
        if not token_match or not time_seconds_match:
            return None
    best_match = re.search(r"\bbest\s*[:=]?\s*([0-9][0-9,]*(?:\.[0-9]+)?)", line, re.IGNORECASE)
    wall_seconds = (
        parse_duration(time_match.group(1), time_match.group(2))
        if time_match is not None
        else to_float(time_seconds_match.group(1))
    )
    return TokenSnapshot(
        label=context_label(line) or "snapshot",
        wall_seconds=wall_seconds,
        total_tokens=to_float(token_match.group(1)),
        best_score=to_float(best_match.group(1)) if best_match else None,
    )


def dedupe_snapshots(snapshots: list[TokenSnapshot]) -> list[TokenSnapshot]:
    seen: set[tuple[float | None, float | None, str]] = set()
    deduped: list[TokenSnapshot] = []
    for snapshot in snapshots:
        key = (snapshot.wall_seconds, snapshot.total_tokens, snapshot.label)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(snapshot)
    return sorted(
        deduped,
        key=lambda item: (
            float("inf") if item.wall_seconds is None else item.wall_seconds,
            float("inf") if item.timestamp is None else item.timestamp,
        ),
    )


def read_token_snapshots(path: Path | None) -> list[TokenSnapshot]:
    if path is None or not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    snapshots: list[TokenSnapshot] = []
    for obj, start, end in json_objects(text):
        snapshot = snapshot_from_mapping(obj, nearby_text(text, start, end))
        if snapshot is not None:
            snapshots.append(snapshot)
    for line in text.splitlines():
        snapshot = parse_snapshot_line(line)
        if snapshot is not None:
            snapshots.append(snapshot)
    return dedupe_snapshots(snapshots)


def legacy_token_snapshots(points: list[Point]) -> list[TokenSnapshot]:
    snapshots: list[TokenSnapshot] = []
    for point in points:
        if point.tokens_total is None or point.wall_seconds is None:
            continue
        snapshots.append(
            TokenSnapshot(
                label=point.candidate,
                wall_seconds=point.wall_seconds,
                total_tokens=point.tokens_total,
                source="legacy token columns",
            )
        )
    return dedupe_snapshots(snapshots)


def state_snapshot(path: Path | None) -> tuple[TokenSnapshot | None, float | None, float | None]:
    if path is None or not path.exists():
        return None, None, None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return None, None, None
    flat = flatten(data)
    target = find_number(flat, ["target_score", "target", "objective_target"])
    best = find_number(flat, ["best_stable_score", "best_score", "protected_best", "progress.best_stable_score"])
    snapshot_obj = (
        nested_value(data, "progress.latest_usage_snapshot")
        or nested_value(data, "latest_usage_snapshot")
        or nested_value(data, "usage_snapshot")
    )
    snapshot = snapshot_from_mapping(snapshot_obj, "get_goal current usage snapshot") if isinstance(snapshot_obj, dict) else None
    if snapshot is None:
        total = find_number(flat, ["progress.tokens_total", "tokens_total", "tokensUsed", "total_tokens"])
        wall = find_number(flat, ["progress.wall_seconds", "wall_seconds", "timeUsedSeconds", "elapsedSeconds"])
        if total is not None or wall is not None:
            snapshot = TokenSnapshot(
                label="current",
                wall_seconds=wall,
                total_tokens=total,
                best_score=best,
                source="state.json",
            )
    if snapshot is not None and snapshot.best_score is None:
        snapshot.best_score = best
    return snapshot, target, best


def improves(score: float, best: float, direction: str) -> bool:
    return score < best if direction == "lower" else score > best


def visible_points(points: list[Point], hide_before_candidate: int) -> tuple[list[Point], float, float, bool]:
    numeric = [p.candidate_number for p in points]
    if not numeric:
        return points, 0.0, max(1.0, float(len(points) - 1)), False
    data_min = min(numeric)
    data_max = max(numeric)
    hide = data_max >= hide_before_candidate and any(p.candidate_number >= hide_before_candidate for p in points)
    visible = [p for p in points if not hide or p.candidate_number >= hide_before_candidate]
    if not visible:
        visible = points
        hide = False
    xmin = min(p.candidate_number for p in visible)
    xmax = max(p.candidate_number for p in visible)
    if xmin == xmax:
        xmax = xmin + 1.0
    return visible, xmin, xmax, hide


def status_kind(decision: str) -> str:
    decision = decision.lower()
    if decision in BEST_DECISIONS:
        return "promote"
    if decision in KEEP_DECISIONS:
        return "keep"
    if decision in BAD_DECISIONS or any(word in decision for word in ["fail", "wrong", "incorrect"]):
        return "failure"
    if decision in REJECT_DECISIONS:
        return "reject"
    return "measured"


def format_number(value: float | None, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M{suffix}"
    if abs(value) >= 1000:
        return f"{value:,.0f}{suffix}"
    return f"{value:.4g}{suffix}"


def format_tokens(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1000:
        return f"{value / 1000:.0f}k"
    return f"{value:.0f}"


def format_target(value: float) -> str:
    if value.is_integer() and abs(value) < 10000:
        return f"{value:.0f}"
    return format_number(value)


def format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "n/a"
    if seconds >= 3600:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h{minutes:02d}m" if minutes else f"{hours}h"
    if seconds >= 60:
        minutes = int(seconds // 60)
        rem = int(seconds % 60)
        return f"{minutes}m{rem:02d}s" if rem else f"{minutes}m"
    return f"{seconds:.0f}s"


def token_detail(snapshot: TokenSnapshot | None) -> str:
    if snapshot is None:
        return "current usage snapshot: n/a"
    parts = [f"{format_tokens(snapshot.total_tokens)} tokens"]
    granular = [
        ("input", snapshot.input_tokens),
        ("cached", snapshot.cached_input_tokens),
        ("cache create", snapshot.cache_creation_input_tokens),
        ("cache read", snapshot.cache_read_input_tokens),
        ("output", snapshot.output_tokens),
        ("reasoning", snapshot.reasoning_output_tokens),
    ]
    parts.extend(f"{label} {format_tokens(value)}" for label, value in granular if value is not None)
    if snapshot.wall_seconds is not None:
        parts.append(f"at {format_duration(snapshot.wall_seconds)}")
    return "current usage snapshot: " + " | ".join(parts)


def polyline(points: list[tuple[float, float]], color: str, width: float = 2.0, extra: str = "") -> str:
    if len(points) < 2:
        return ""
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width:g}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def log_ticks(lo: float, hi: float) -> list[float]:
    if lo <= 0 or hi <= 0:
        return []
    mantissas = [1, 1.1, 1.2, 1.3, 1.5, 2, 2.5, 3, 4, 5, 7.5]
    start_exp = math.floor(math.log10(lo)) - 1
    end_exp = math.ceil(math.log10(hi)) + 1
    values: list[float] = []
    for exp in range(start_exp, end_exp + 1):
        base = 10**exp
        for mantissa in mantissas:
            value = mantissa * base
            if lo <= value <= hi:
                values.append(value)
    if len(values) > 8:
        stride = math.ceil(len(values) / 7)
        values = values[::stride]
    return values


def linear_ticks(lo: float, hi: float, count: int = 6) -> list[float]:
    if count <= 1:
        return [lo]
    step = (hi - lo) / (count - 1)
    return [lo + i * step for i in range(count)]


def candidate_ticks(xmin: float, xmax: float) -> list[float]:
    span = max(1.0, xmax - xmin)
    step = max(1, int(math.ceil(span / 9)))
    start = int(math.ceil(xmin / step) * step)
    values = [float(int(xmin))]
    values.extend(float(value) for value in range(start, int(xmax) + 1, step))
    if values[-1] != float(int(xmax)):
        values.append(float(int(xmax)))
    out: list[float] = []
    for value in values:
        if xmin <= value <= xmax and value not in out:
            out.append(value)
    return out


def time_ticks(xmax: float) -> list[float]:
    if xmax <= 0:
        return [0.0, 1.0]
    if xmax <= 7200:
        step = 900.0
    elif xmax <= 21600:
        step = 3600.0
    else:
        step = 7200.0
    values = [0.0]
    value = step
    while value < xmax:
        values.append(value)
        value += step
    values.append(xmax)
    return values


def best_series(points: list[Point], direction: str, xmin: float) -> tuple[list[tuple[float, float]], Point | None]:
    best_score: float | None = None
    best_point: Point | None = None
    series: list[tuple[float, float]] = []
    for point in sorted(points, key=lambda item: item.candidate_number):
        eligible = point.decision in BEST_DECISIONS or (point.row == 0 and not point.decision)
        if point.score is not None and eligible:
            if best_score is None or improves(point.score, best_score, direction):
                best_score = point.score
                best_point = point
        if best_score is not None and point.candidate_number >= xmin:
            series.append((point.candidate_number, best_score))
    return series, best_point


def score_title(point: Point, ylabel: str) -> str:
    bits = [f"{point.candidate}: {point.decision or 'measured'}"]
    if point.score is not None:
        bits.append(f"{format_number(point.score)} {ylabel}")
    if point.label:
        bits.append(point.label)
    return " - ".join(bits)


def category_series(snapshots: list[TokenSnapshot]) -> list[tuple[str, str, list[tuple[float, float]]]]:
    fields = [
        ("input", "#2563eb", "input_tokens"),
        ("cached input", "#7c3aed", "cached_input_tokens"),
        ("cache creation", "#0ea5e9", "cache_creation_input_tokens"),
        ("cache read", "#14b8a6", "cache_read_input_tokens"),
        ("output", "#16a34a", "output_tokens"),
        ("reasoning", "#dc2626", "reasoning_output_tokens"),
    ]
    out: list[tuple[str, str, list[tuple[float, float]]]] = []
    for label, color, attr in fields:
        values = [(s.wall_seconds, getattr(s, attr)) for s in snapshots if s.wall_seconds is not None and getattr(s, attr) is not None]
        if len(values) >= 2:
            out.append((label, color, [(float(x), float(y)) for x, y in values]))
    return out


def snapshot_title(snapshot: TokenSnapshot, ylabel: str) -> str:
    parts = [f"{snapshot.label}: {format_tokens(snapshot.total_tokens)} tokens at {format_duration(snapshot.wall_seconds)}"]
    if snapshot.source != "get_goal":
        parts.append(snapshot.source)
    for label, value in [
        ("input", snapshot.input_tokens),
        ("cached input", snapshot.cached_input_tokens),
        ("cache creation", snapshot.cache_creation_input_tokens),
        ("cache read", snapshot.cache_read_input_tokens),
        ("output", snapshot.output_tokens),
        ("reasoning", snapshot.reasoning_output_tokens),
    ]:
        if value is not None:
            parts.append(f"{label} {format_tokens(value)}")
    if snapshot.best_score is not None:
        parts.append(f"best {format_number(snapshot.best_score)} {ylabel}")
    return ", ".join(parts)


def render_svg(
    points: list[Point],
    output: Path,
    title: str,
    ylabel: str,
    direction: str,
    x_axis: str = "candidate",
    log_path: Path | None = None,
    state_path: Path | None = None,
    target: float | None = None,
    hide_before_candidate: int = 3,
    score_scale: str = "auto",
    generated_at: str | None = None,
) -> None:
    del x_axis
    if not points:
        raise SystemExit("progress data has no candidate rows")

    snapshots = read_token_snapshots(log_path)
    token_source = "explicit get_goal snapshots"
    if not snapshots:
        snapshots = legacy_token_snapshots(points)
        if snapshots:
            token_source = "legacy token columns"
    current_snapshot, state_target, state_best = state_snapshot(state_path)
    if target is None:
        target = state_target
    if current_snapshot is None and snapshots:
        current_snapshot = snapshots[-1]

    visible, xmin, xmax, hid_early = visible_points(points, hide_before_candidate)
    series, protected_best = best_series(points, direction, xmin)
    scored_visible = [p for p in visible if p.score is not None]
    score_values = [p.score for p in scored_visible if p.score is not None]
    if not score_values:
        score_values = [p.score for p in points if p.score is not None]
    if not score_values:
        raise SystemExit("progress data has no numeric score values")
    score_values.extend(score for _, score in series)
    if target is not None:
        score_values.append(target)
    if state_best is not None:
        score_values.append(state_best)

    if score_scale == "auto":
        scale = "log" if all(value > 0 for value in score_values) else "linear"
    else:
        scale = score_scale
    if scale == "log" and any(value <= 0 for value in score_values):
        raise SystemExit("log score scale requires all plotted score and target values to be positive; use --score-scale linear")

    raw_min = min(score_values)
    raw_max = max(score_values)
    if scale == "log":
        score_min = raw_min * 0.965
        score_max = raw_max * 1.045
        scale_min = math.log(score_min)
        scale_max = math.log(score_max)
    else:
        span = raw_max - raw_min
        pad = max(abs(raw_min), abs(raw_max), 1.0) * 0.045 if span == 0 else span * 0.08
        score_min = raw_min - pad
        score_max = raw_max + pad
        scale_min = score_min
        scale_max = score_max

    def x_candidate(value: float) -> float:
        return LEFT + (value - xmin) / (xmax - xmin) * PLOT_W

    def y_score(score: float) -> float:
        scaled = math.log(score) if scale == "log" else score
        return SCORE_Y + (scale_max - scaled) / (scale_max - scale_min) * SCORE_H

    if state_best is not None and (protected_best is None or protected_best.score != state_best):
        protected_best_value = state_best
    else:
        protected_best_value = protected_best.score if protected_best is not None else None
    measured_line = polyline(
        [(x_candidate(p.candidate_number), y_score(p.score)) for p in scored_visible if p.score is not None and (scale != "log" or p.score > 0)],
        MEASURED,
        1.2,
        'stroke-opacity="0.65" stroke-dasharray="3 4"',
    )
    best_line = polyline([(x_candidate(candidate), y_score(score)) for candidate, score in series if scale != "log" or score > 0], BLUE, 2.8)

    token_chart_snapshots = [s for s in snapshots if s.wall_seconds is not None and s.total_tokens is not None]
    max_wall = max([s.wall_seconds or 0.0 for s in token_chart_snapshots] + [current_snapshot.wall_seconds or 0.0 if current_snapshot else 0.0, 1.0])
    token_values = [s.total_tokens for s in token_chart_snapshots if s.total_tokens is not None]
    for _, _, category in category_series(token_chart_snapshots):
        token_values.extend(value for _, value in category)
    if current_snapshot and current_snapshot.total_tokens is not None:
        token_values.append(current_snapshot.total_tokens)
    token_max = max(token_values or [1.0]) * 1.12

    def x_time(seconds: float) -> float:
        return LEFT + seconds / max_wall * PLOT_W

    def y_token(tokens: float) -> float:
        return TOKEN_Y + (token_max - tokens) / token_max * TOKEN_H

    desc = (
        f"Optimization timeline displayed from Candidate {xmin:.0f} through Candidate {xmax:.0f}. "
        f"Protected best is {format_number(protected_best_value)} {ylabel}. "
        f"Token usage source: {token_source}."
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)} With Token Usage</title>',
        f'<desc id="desc">{escape(desc)}</desc>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>',
        f'<text x="{LEFT:.1f}" y="30" font-family="Arial, sans-serif" font-size="20" fill="{TEXT}" text-anchor="start" font-weight="700">{escape(title)} With Tokens</text>',
        f'<text x="{PLOT_RIGHT:.1f}" y="30" font-family="Arial, sans-serif" font-size="12" fill="{MUTED}" text-anchor="end">displayed candidates {xmin:.0f}-{xmax:.0f}</text>',
        f'<text x="{PLOT_RIGHT:.1f}" y="48" font-family="Arial, sans-serif" font-size="12" fill="{AMBER_TEXT}" text-anchor="end" font-weight="700">{escape(token_detail(current_snapshot))}</text>',
        f'<rect x="{LEFT:.1f}" y="{SCORE_Y:.1f}" width="{PLOT_W:.1f}" height="{SCORE_H:.1f}" fill="{SCORE_PANEL}" stroke="{GRID}"/>',
    ]

    tick_values = log_ticks(score_min, score_max) if scale == "log" else linear_ticks(score_min, score_max)
    for value in tick_values:
        yy = y_score(value)
        parts.append(f'<line x1="{LEFT:.1f}" y1="{yy:.1f}" x2="{PLOT_RIGHT:.1f}" y2="{yy:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{LEFT - 10:.1f}" y="{yy + 4:.1f}" font-family="Arial, sans-serif" font-size="11" fill="{SUBTLE}" text-anchor="end">{format_number(value)}</text>')

    if target is not None and score_min <= target <= score_max:
        yy = y_score(target)
        comparator = "&lt;" if direction == "lower" else "&gt;"
        parts.append(f'<line x1="{LEFT:.1f}" y1="{yy:.1f}" x2="{PLOT_RIGHT:.1f}" y2="{yy:.1f}" stroke="{RED}" stroke-width="1.3" stroke-dasharray="5 5"/>')
        parts.append(f'<text x="{LEFT - 10:.1f}" y="{yy + 4:.1f}" font-family="Arial, sans-serif" font-size="11" fill="{RED_TEXT}" text-anchor="end">target {comparator}{format_target(target)}</text>')

    axis_y = SCORE_Y + SCORE_H
    for value in candidate_ticks(xmin, xmax):
        xx = x_candidate(value)
        parts.append(f'<line x1="{xx:.1f}" y1="{axis_y:.1f}" x2="{xx:.1f}" y2="{axis_y + 6:.1f}" stroke="{MEASURED}" stroke-width="1"/>')
        parts.append(f'<text x="{xx:.1f}" y="{axis_y + 22:.1f}" font-family="Arial, sans-serif" font-size="11" fill="{SUBTLE}" text-anchor="middle">{value:.0f}</text>')
    hidden_note = f" ({hide_before_candidate} early candidates hidden)" if hid_early else ""
    parts.append(f'<text x="{(LEFT + PLOT_RIGHT) / 2:.1f}" y="{axis_y + 42:.1f}" font-family="Arial, sans-serif" font-size="12" fill="{MUTED}" text-anchor="middle">Candidate number{escape(hidden_note)}</text>')
    parts.append(f'<text x="22" y="{SCORE_Y + SCORE_H / 2:.1f}" font-family="Arial, sans-serif" font-size="12" fill="{MUTED}" text-anchor="middle" transform="rotate(-90 22 {SCORE_Y + SCORE_H / 2:.1f})">{escape(ylabel)}, {scale} scale</text>')
    parts.append(measured_line)
    parts.append(best_line)

    failure_y = axis_y + 20
    for point in visible:
        xx = x_candidate(point.candidate_number)
        kind = status_kind(point.decision)
        title_text = escape(score_title(point, ylabel))
        if point.score is None or (scale == "log" and point.score <= 0):
            if kind == "failure":
                parts.append(f'<path d="M {xx - 4:.1f} {failure_y - 4:.1f} L {xx + 4:.1f} {failure_y + 4:.1f} M {xx + 4:.1f} {failure_y - 4:.1f} L {xx - 4:.1f} {failure_y + 4:.1f}" stroke="{RED}" stroke-width="1.7"><title>{title_text}</title></path>')
            continue
        yy = y_score(point.score)
        if kind == "promote":
            parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="3.2" fill="{GREEN}"><title>{title_text}</title></circle>')
        elif kind == "keep":
            parts.append(f'<polygon points="{xx:.1f},{yy - 4:.1f} {xx + 4:.1f},{yy:.1f} {xx:.1f},{yy + 4:.1f} {xx - 4:.1f},{yy:.1f}" fill="{ORANGE}"><title>{title_text}</title></polygon>')
        elif kind == "failure":
            parts.append(f'<path d="M {xx - 4:.1f} {yy - 4:.1f} L {xx + 4:.1f} {yy + 4:.1f} M {xx + 4:.1f} {yy - 4:.1f} L {xx - 4:.1f} {yy + 4:.1f}" stroke="{RED}" stroke-width="1.7"><title>{title_text}</title></path>')
        elif kind == "reject":
            parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="3.3" fill="#ffffff" stroke="{RED}" stroke-width="1.5"><title>{title_text}</title></circle>')
        else:
            parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="2.8" fill="{MEASURED}"><title>{title_text}</title></circle>')

    if protected_best_value is not None and (scale != "log" or protected_best_value > 0):
        yy = y_score(protected_best_value)
        parts.append(f'<text x="{PLOT_RIGHT - 4:.1f}" y="{yy - 10:.1f}" font-family="Arial, sans-serif" font-size="12" fill="#065f46" text-anchor="end" font-weight="700">protected best: {format_number(protected_best_value)} {escape(ylabel)}</text>')
    if hid_early:
        parts.append(f'<text x="{LEFT + 8:.1f}" y="{SCORE_Y + 18:.1f}" font-family="Arial, sans-serif" font-size="11" fill="{SUBTLE}" text-anchor="start">Candidates 0-{hide_before_candidate - 1} hidden for scale</text>')

    parts.extend(
        [
            f'<text x="{LEFT:.1f}" y="447" font-family="Arial, sans-serif" font-size="16" fill="{TEXT}" text-anchor="start" font-weight="700">Recorded Token Usage</text>',
            f'<text x="{PLOT_RIGHT:.1f}" y="447" font-family="Arial, sans-serif" font-size="12" fill="{MUTED}" text-anchor="end">x-axis is elapsed wall time from {escape(token_source)}</text>',
            f'<rect x="{LEFT:.1f}" y="{TOKEN_Y:.1f}" width="{PLOT_W:.1f}" height="{TOKEN_H:.1f}" fill="{TOKEN_PANEL}" stroke="{TOKEN_GRID}"/>',
        ]
    )
    if token_chart_snapshots:
        first_wall = min(s.wall_seconds or 0.0 for s in token_chart_snapshots)
        if first_wall > 0:
            parts.append(f'<rect x="{LEFT:.1f}" y="{TOKEN_Y:.1f}" width="{x_time(first_wall) - LEFT:.1f}" height="{TOKEN_H:.1f}" fill="{UNKNOWN}" opacity="0.65"/>')
            parts.append(f'<text x="{LEFT + 12:.1f}" y="{TOKEN_Y + 20:.1f}" font-family="Arial, sans-serif" font-size="11" fill="{SUBTLE}" text-anchor="start">token/time not recorded before first snapshot</text>')
    else:
        parts.append(f'<rect x="{LEFT:.1f}" y="{TOKEN_Y:.1f}" width="{PLOT_W:.1f}" height="{TOKEN_H:.1f}" fill="{UNKNOWN}" opacity="0.65"/>')
        parts.append(f'<text x="{(LEFT + PLOT_RIGHT) / 2:.1f}" y="{TOKEN_Y + TOKEN_H / 2:.1f}" font-family="Arial, sans-serif" font-size="13" fill="{SUBTLE}" text-anchor="middle">no explicit get_goal snapshots or legacy token columns</text>')

    for value in linear_ticks(0.0, token_max):
        yy = y_token(value)
        parts.append(f'<line x1="{LEFT:.1f}" y1="{yy:.1f}" x2="{PLOT_RIGHT:.1f}" y2="{yy:.1f}" stroke="{TOKEN_GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{LEFT - 10:.1f}" y="{yy + 4:.1f}" font-family="Arial, sans-serif" font-size="11" fill="{AMBER_TEXT}" text-anchor="end">{format_tokens(value)}</text>')
    for value in time_ticks(max_wall):
        xx = x_time(value)
        parts.append(f'<line x1="{xx:.1f}" y1="{TOKEN_Y + TOKEN_H:.1f}" x2="{xx:.1f}" y2="{TOKEN_Y + TOKEN_H + 6:.1f}" stroke="{ORANGE_DARK}" stroke-width="1"/>')
        parts.append(f'<text x="{xx:.1f}" y="{TOKEN_Y + TOKEN_H + 22:.1f}" font-family="Arial, sans-serif" font-size="11" fill="{AMBER_TEXT}" text-anchor="middle">{format_duration(value)}</text>')
    parts.append(f'<text x="{(LEFT + PLOT_RIGHT) / 2:.1f}" y="{TOKEN_Y + TOKEN_H + 44:.1f}" font-family="Arial, sans-serif" font-size="12" fill="{MUTED}" text-anchor="middle">Elapsed wall time from recorded run snapshots</text>')
    parts.append(f'<text x="22" y="{TOKEN_Y + TOKEN_H / 2:.1f}" font-family="Arial, sans-serif" font-size="12" fill="{AMBER_TEXT}" text-anchor="middle" transform="rotate(-90 22 {TOKEN_Y + TOKEN_H / 2:.1f})">Cumulative tokens</text>')

    for label, color, series_values in category_series(token_chart_snapshots):
        points_xy = [(x_time(seconds), y_token(tokens)) for seconds, tokens in series_values]
        parts.append(polyline(points_xy, color, 1.3, 'stroke-opacity="0.62" stroke-dasharray="2 4"'))
    token_line = polyline(
        [(x_time(float(s.wall_seconds)), y_token(float(s.total_tokens))) for s in token_chart_snapshots if s.wall_seconds is not None and s.total_tokens is not None],
        ORANGE,
        3,
    )
    parts.append(token_line)
    label_every = max(1, len(token_chart_snapshots) // 7)
    for index, snapshot in enumerate(token_chart_snapshots):
        xx = x_time(float(snapshot.wall_seconds))
        yy = y_token(float(snapshot.total_tokens))
        parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="4" fill="{ORANGE_DARK}"><title>{escape(snapshot_title(snapshot, ylabel))}</title></circle>')
        if index == 0 or index == len(token_chart_snapshots) - 1 or index % label_every == 0:
            parts.append(f'<text x="{xx:.1f}" y="{yy - 8:.1f}" font-family="Arial, sans-serif" font-size="10" fill="{AMBER_TEXT}" text-anchor="middle">{escape(snapshot.label[:16])}</text>')
    if current_snapshot and current_snapshot.total_tokens is not None:
        yy = y_token(current_snapshot.total_tokens)
        parts.append(f'<text x="{PLOT_RIGHT - 4:.1f}" y="{yy - 10:.1f}" font-family="Arial, sans-serif" font-size="12" fill="{AMBER_TEXT}" text-anchor="end" font-weight="700">{format_tokens(current_snapshot.total_tokens)} tokens</text>')

    legend_y = 692
    legend = [
        (BLUE, "best score"),
        (MEASURED, "measured score"),
        (GREEN, "promoted"),
        (ORANGE, "kept/tokens"),
        (RED, "reject/fail"),
    ]
    x0 = LEFT
    for color, label in legend:
        parts.append(f'<line x1="{x0:.1f}" y1="{legend_y:.1f}" x2="{x0 + 18:.1f}" y2="{legend_y:.1f}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{x0 + 24:.1f}" y="{legend_y + 4:.1f}" font-family="Arial, sans-serif" font-size="11" fill="#374151" text-anchor="start">{escape(label)}</text>')
        x0 += 145
    if category_series(token_chart_snapshots):
        parts.append(f'<text x="{x0:.1f}" y="{legend_y + 4:.1f}" font-family="Arial, sans-serif" font-size="11" fill="{SUBTLE}" text-anchor="start">dashed token category lines when recorded</text>')
    if generated_at is not None:
        parts.append(f'<text x="{PLOT_RIGHT:.1f}" y="{legend_y + 4:.1f}" font-family="Arial, sans-serif" font-size="10" fill="{SUBTLE}" text-anchor="end">generated {escape(generated_at)}</text>')
    parts.append(
        f'<a href="{SKILL_URL}" target="_blank" rel="noopener noreferrer">'
        f'<text x="{LEFT:.1f}" y="714" font-family="Arial, sans-serif" font-size="10" fill="{BLUE}" text-anchor="start">'
        f'{escape(SKILL_LINK_TEXT)}</text></a>'
    )
    parts.append("</svg>")
    output.write_text("\n".join(part for part in parts if part), encoding="utf-8")


def infer_log_path(input_path: Path, explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit
    candidate = input_path.parent / "log.md"
    return candidate if candidate.exists() else None


def infer_state_path(input_path: Path, explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit
    candidate = input_path.parent / "state.json"
    return candidate if candidate.exists() else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a two-panel optimization progress SVG from work/progress.tsv plus get_goal snapshots.")
    parser.add_argument("input", type=Path, help="TSV or JSONL with candidate, score/cycles, status/decision, and description columns")
    parser.add_argument("-o", "--output", type=Path, default=Path("work/progress.svg"))
    parser.add_argument("--log", type=Path, help="Log file containing explicit get_goal token snapshots; defaults to input sibling log.md")
    parser.add_argument("--state", type=Path, help="State file with current best/latest usage snapshot; defaults to input sibling state.json")
    parser.add_argument("--target", type=float, help="Target score line, for example 1000 for sub-1000 cycles")
    parser.add_argument("--hide-before-candidate", type=int, default=3, help="Hide early candidate numbers below this value when possible")
    parser.add_argument("--title", default="Optimization Progress")
    parser.add_argument("--ylabel", default="Authoritative metric")
    parser.add_argument("--direction", choices=("lower", "higher"), default="lower")
    parser.add_argument("--x-axis", choices=("candidate", "tokens", "active", "wall"), default="candidate", help="Accepted for compatibility; score panel uses candidate number")
    parser.add_argument("--score-scale", choices=("auto", "log", "linear"), default="auto", help="Score y-axis scale; auto uses log only when all plotted score/target values are positive")
    parser.add_argument("--generated-at", help="Fixed generation timestamp for deterministic SVG output; ISO-8601, normalized to UTC Z")
    parser.add_argument("--no-generated-at", action="store_true", help="Omit the generated timestamp footer")
    args = parser.parse_args()

    points = read_points(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    render_svg(
        points,
        args.output,
        args.title,
        args.ylabel,
        args.direction,
        args.x_axis,
        infer_log_path(args.input, args.log),
        infer_state_path(args.input, args.state),
        args.target,
        args.hide_before_candidate,
        args.score_scale,
        generated_at_value(args.generated_at, args.no_generated_at),
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
