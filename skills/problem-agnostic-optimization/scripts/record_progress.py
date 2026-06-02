#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


REQUIRED_COLUMNS = ["timestamp", "candidate", "decision", "tokens_total", "tokens_delta", "wall_seconds", "label"]
DEFAULT_METRIC = "score"
OPTIONAL_CANDIDATE_NUMBER = "candidate_number"
RESERVED_METRIC_COLUMNS = set(REQUIRED_COLUMNS) | {OPTIONAL_CANDIDATE_NUMBER, "candidate_index"}


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


def clean_column(name: str, source: str) -> str:
    column = name.strip()
    if not column:
        raise SystemExit(f"{source} column name cannot be empty")
    if any(ch in column for ch in "\t\r\n"):
        raise SystemExit(f"{source} column name cannot contain tabs or newlines")
    if column in RESERVED_METRIC_COLUMNS:
        raise SystemExit(f"{source} column name {column!r} is reserved")
    return column


def clean_cell(value: str | None, source: str, *, allow_empty: bool = True) -> str:
    text = "" if value is None else value.strip()
    if not text and not allow_empty:
        raise SystemExit(f"{source} cannot be empty")
    if any(ch in text for ch in "\t\r\n"):
        raise SystemExit(f"{source} cannot contain tabs or newlines")
    return text


def decimal_value(value: str, source: str) -> Decimal:
    try:
        number = Decimal(value.replace(",", ""))
    except InvalidOperation as exc:
        raise SystemExit(f"{source} must be numeric") from exc
    if not number.is_finite():
        raise SystemExit(f"{source} must be finite")
    return number


def numeric_cell(value: str | None, source: str, *, allow_empty: bool = True) -> str:
    text = clean_cell(value, source, allow_empty=allow_empty)
    if text:
        decimal_value(text, source)
    return text


def format_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(int(normalized))
    return format(normalized, "f")


def parse_metric(args: argparse.Namespace) -> tuple[str, str]:
    selected = [value is not None for value in (args.score, args.metric, args.metric_name)]
    if sum(selected) > 1:
        raise SystemExit("use only one of --score, --metric, or --metric-name")
    if args.metric is not None:
        if "=" not in args.metric:
            raise SystemExit("--metric must be NAME=VALUE, for example --metric cycles=2226")
        name, value = args.metric.split("=", 1)
        return clean_column(name, "--metric"), numeric_cell(value, "--metric value")
    if args.metric_name is not None:
        return clean_column(args.metric_name, "--metric-name"), ""
    return DEFAULT_METRIC, numeric_cell(args.score, "--score")


def create_header(progress: Path, metric_name: str, include_candidate_number: bool) -> list[str]:
    header = ["timestamp", "candidate"]
    if include_candidate_number:
        header.append(OPTIONAL_CANDIDATE_NUMBER)
    header.extend([metric_name, "decision", "tokens_total", "tokens_delta", "wall_seconds", "label"])
    progress.parent.mkdir(parents=True, exist_ok=True)
    with progress.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f, delimiter="\t", lineterminator="\n").writerow(header)
    return header


def read_header(progress: Path) -> list[str] | None:
    if not progress.exists() or progress.stat().st_size == 0:
        return None
    with progress.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        try:
            header = next(reader)
        except StopIteration:
            return None
    return header


def header_for_append(progress: Path, metric_name: str, candidate_number: str) -> list[str]:
    header = read_header(progress)
    if header is None:
        return create_header(progress, metric_name, bool(candidate_number))

    duplicates = sorted({column for column in header if header.count(column) > 1})
    if duplicates:
        raise SystemExit(f"{progress} has duplicate columns: {', '.join(duplicates)}")

    missing = [column for column in REQUIRED_COLUMNS if column not in header]
    if missing:
        raise SystemExit(f"{progress} is missing required columns: {', '.join(missing)}")
    if metric_name not in header:
        raise SystemExit(f"{progress} is missing metric column {metric_name!r}; use the existing metric column or start a new progress file")
    if candidate_number and OPTIONAL_CANDIDATE_NUMBER not in header:
        raise SystemExit(f"{progress} is missing candidate_number column; use an existing candidate_number column or start a new progress file")
    return header


def previous_tokens_total(progress: Path, header: list[str]) -> Decimal | None:
    if not progress.exists() or "tokens_total" not in header:
        return None
    previous: Decimal | None = None
    with progress.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            value = clean_cell(row.get("tokens_total"), "previous tokens_total")
            if value:
                previous = decimal_value(value, "previous tokens_total")
    return previous


def token_delta(args: argparse.Namespace, progress: Path, header: list[str], tokens_total: str) -> str:
    explicit = numeric_cell(args.tokens_delta, "--tokens-delta")
    if explicit or not tokens_total:
        return explicit
    previous = previous_tokens_total(progress, header)
    if previous is None:
        return ""
    return format_decimal(decimal_value(tokens_total, "--tokens-total") - previous)


def progress_row(args: argparse.Namespace, progress: Path, header: list[str], metric_name: str, metric_value: str, candidate_number: str) -> dict[str, str]:
    tokens_total = numeric_cell(args.tokens_total, "--tokens-total")
    row = {
        "timestamp": utc_timestamp(args.timestamp),
        "candidate": clean_cell(args.candidate, "--candidate", allow_empty=False),
        OPTIONAL_CANDIDATE_NUMBER: candidate_number,
        metric_name: metric_value,
        "decision": clean_cell(args.decision, "--decision", allow_empty=False),
        "tokens_total": tokens_total,
        "tokens_delta": token_delta(args, progress, header, tokens_total),
        "wall_seconds": numeric_cell(args.wall_seconds, "--wall-seconds"),
        "label": clean_cell(args.label, "--label"),
    }
    return row


def append_row(progress: Path, header: list[str], row: dict[str, str]) -> None:
    with progress.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(description="Append one canonical row to work/progress.tsv.")
    parser.add_argument("--progress", type=Path, default=Path("work/progress.tsv"))
    parser.add_argument("--timestamp", help="ISO-8601 timestamp; normalized to UTC Z. Defaults to current UTC time.")
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--score", help="Authoritative score value for the default score column")
    parser.add_argument("--metric", help="Authoritative metric as NAME=VALUE, for example cycles=2226")
    parser.add_argument("--metric-name", help="Metric column to use with a blank value, for bug/crash rows without a numeric result")
    parser.add_argument("--candidate-number", help="Explicit numeric candidate position for ambiguous candidate names")
    parser.add_argument("--tokens-total")
    parser.add_argument("--tokens-delta")
    parser.add_argument("--wall-seconds")
    parser.add_argument("--label", default="")
    args = parser.parse_args()

    clean_cell(args.candidate, "--candidate", allow_empty=False)
    clean_cell(args.decision, "--decision", allow_empty=False)
    clean_cell(args.label, "--label")
    numeric_cell(args.tokens_total, "--tokens-total")
    numeric_cell(args.tokens_delta, "--tokens-delta")
    numeric_cell(args.wall_seconds, "--wall-seconds")
    metric_name, metric_value = parse_metric(args)
    candidate_number = numeric_cell(args.candidate_number, "--candidate-number")
    header = header_for_append(args.progress, metric_name, candidate_number)
    append_row(args.progress, header, progress_row(args, args.progress, header, metric_name, metric_value, candidate_number))
    print(args.progress)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
