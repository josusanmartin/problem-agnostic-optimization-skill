#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from progress_chart import infer_log_path, infer_state_path, read_points, render_svg


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def utc_timestamp(value: str | None) -> str:
    if not value:
        return utc_now()
    text = value.strip()
    candidate = f"{text[:-1]}+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise SystemExit("--timestamp must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_value(text: str) -> object:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def add_extra_field(record: dict[str, object], field: str) -> None:
    if "=" not in field:
        raise SystemExit(f"--field must be KEY=VALUE, got {field!r}")
    key, raw_value = field.split("=", 1)
    key = key.strip()
    if not key:
        raise SystemExit("--field key cannot be empty")
    record[key] = json_value(raw_value.strip())


def compact_record(args: argparse.Namespace) -> dict[str, object]:
    record: dict[str, object] = {
        "timestamp": utc_timestamp(args.timestamp),
        "candidate": args.candidate,
        "decision": args.decision,
        "tokens_total": args.tokens_total,
        "tokens_delta": args.tokens_delta,
        "active_seconds": args.active_seconds,
        "wall_seconds": args.wall_seconds,
    }
    optional = {
        "score": args.score,
        "label": args.label,
        "parent": args.parent,
        "branch": args.branch,
        "mode": args.mode,
        "correctness": args.correctness,
        "validation_command": args.validation_command,
        "measurement_command": args.measurement_command,
        "raw_result_path": args.raw_result_path,
    }
    record.update({key: value for key, value in optional.items() if value is not None})
    for field in args.field:
        add_extra_field(record, field)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a progress event and optionally refresh progress.svg.")
    parser.add_argument("--events", type=Path, default=Path("work/optimization_harness/events.jsonl"))
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--score", type=float)
    parser.add_argument("--tokens-total", type=float)
    parser.add_argument("--tokens-delta", type=float)
    parser.add_argument("--active-seconds", type=float)
    parser.add_argument("--wall-seconds", type=float)
    parser.add_argument("--label")
    parser.add_argument("--parent")
    parser.add_argument("--branch")
    parser.add_argument("--mode")
    parser.add_argument("--correctness")
    parser.add_argument("--validation-command")
    parser.add_argument("--measurement-command")
    parser.add_argument("--raw-result-path")
    parser.add_argument("--timestamp")
    parser.add_argument("--field", action="append", default=[], help="Extra KEY=JSON_VALUE field")
    parser.add_argument("--chart", type=Path, help="Render progress chart after appending")
    parser.add_argument("--title", default="Optimization Progress")
    parser.add_argument("--ylabel", default="Authoritative metric")
    parser.add_argument("--direction", choices=("lower", "higher"), default="lower")
    parser.add_argument("--x-axis", choices=("candidate", "tokens", "active", "wall"), default="candidate")
    args = parser.parse_args()

    args.events.parent.mkdir(parents=True, exist_ok=True)
    record = compact_record(args)
    with args.events.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True, separators=(",", ":")))
        f.write("\n")

    if args.chart is not None:
        args.chart.parent.mkdir(parents=True, exist_ok=True)
        points = read_points(args.events)
        render_svg(
            points,
            args.chart,
            args.title,
            args.ylabel,
            args.direction,
            args.x_axis,
            infer_log_path(args.events, None),
            infer_state_path(args.events, None),
        )
        print(args.chart)
    else:
        print(args.events)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
