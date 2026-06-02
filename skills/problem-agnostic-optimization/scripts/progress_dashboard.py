#!/usr/bin/env python3
from __future__ import annotations

import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
from typing import Iterable

from progress_chart import BAD_DECISIONS, BEST_DECISIONS, SKILL_LINK_TEXT, SKILL_URL, Point, TokenSnapshot, generated_at_value, infer_log_path, infer_state_path, read_points, read_token_snapshots, render_svg, state_snapshot


def fmt_number(value: float | None, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    if abs(value) >= 1000:
        return f"{value:,.0f}{suffix}"
    return f"{value:.4g}{suffix}"


def fmt_seconds(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value >= 3600:
        return f"{value / 3600:.2f}h"
    if value >= 60:
        return f"{value / 60:.2f}m"
    return f"{value:.0f}s"


def best_point(points: Iterable[Point], direction: str) -> Point | None:
    best: Point | None = None
    for point in points:
        if point.score is None:
            continue
        eligible = point.decision in BEST_DECISIONS or (point.row == 0 and not point.decision)
        if not eligible:
            continue
        if best is None:
            best = point
        elif best.score is not None and direction == "lower" and point.score < best.score:
            best = point
        elif best.score is not None and direction == "higher" and point.score > best.score:
            best = point
    return best


def last_promotion(points: list[Point]) -> Point | None:
    for point in reversed(points):
        if point.decision in BEST_DECISIONS:
            return point
    return None


def decision_counts(points: list[Point]) -> dict[str, int]:
    counts = {"promoted": 0, "rejected": 0, "bug_blocked": 0, "other": 0}
    for point in points:
        if point.decision in BEST_DECISIONS:
            counts["promoted"] += 1
        elif point.decision in BAD_DECISIONS:
            counts["bug_blocked"] += 1
        elif point.decision in {"reject", "rejected", "discard", "discarded"}:
            counts["rejected"] += 1
        else:
            counts["other"] += 1
    return counts


def inline_chart(
    input_path: Path,
    points: list[Point],
    title: str,
    ylabel: str,
    direction: str,
    x_axis: str,
    target: float | None,
    hide_before_candidate: int,
    score_scale: str,
    generated_at: str | None,
) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        chart_path = Path(tmp) / "progress.svg"
        render_svg(
            points,
            chart_path,
            title,
            ylabel,
            direction,
            x_axis,
            infer_log_path(input_path, None),
            infer_state_path(input_path, None),
            target,
            hide_before_candidate,
            score_scale,
            generated_at,
        )
        return chart_path.read_text(encoding="utf-8")


def summary_cards(points: list[Point], direction: str, usage: TokenSnapshot | None) -> str:
    latest = points[-1]
    best = best_point(points, direction)
    promotion = last_promotion(points)
    counts = decision_counts(points)
    tokens_total = usage.total_tokens if usage is not None and usage.total_tokens is not None else latest.tokens_total
    tokens_since_promotion = None
    if tokens_total is not None and promotion is not None and promotion.tokens_total is not None:
        tokens_since_promotion = max(0.0, tokens_total - promotion.tokens_total)
    if tokens_since_promotion is not None:
        token_sub = f"{fmt_number(tokens_since_promotion)} since promotion"
    elif usage is not None and usage.total_tokens is not None:
        token_sub = f"latest {usage.source} snapshot"
    elif latest.tokens_total is not None:
        token_sub = "legacy token total"
    else:
        token_sub = "since promotion n/a"
    wall_seconds = usage.wall_seconds if usage is not None and usage.wall_seconds is not None else latest.wall_seconds

    cards = [
        ("Best", fmt_number(best.score if best else None), best.candidate if best else "no promoted score"),
        ("Latest", latest.candidate, latest.decision or "no decision"),
        ("Candidates", str(len(points)), f"{counts['promoted']} promoted / {counts['rejected']} rejected"),
        ("Tokens", fmt_number(tokens_total), token_sub),
        ("Active Time", fmt_seconds(latest.active_seconds), "tracked agent time"),
        ("Wall Time", fmt_seconds(wall_seconds), "elapsed from first snapshot/event"),
        ("Bugs/Blocked", str(counts["bug_blocked"]), "needs attention" if counts["bug_blocked"] else "none"),
    ]
    return "\n".join(
        f"""
        <section class="card">
          <div class="card-label">{escape(label)}</div>
          <div class="card-value">{escape(value)}</div>
          <div class="card-sub">{escape(sub)}</div>
        </section>
        """
        for label, value, sub in cards
    )


def rows(points: list[Point], limit: int) -> str:
    visible = points[-limit:]
    return "\n".join(
        f"""
        <tr>
          <td>{point.row}</td>
          <td>{escape(point.candidate)}</td>
          <td><span class="pill {escape(point.decision or 'unknown')}">{escape(point.decision or 'unknown')}</span></td>
          <td>{escape(fmt_number(point.score))}</td>
          <td>{escape(fmt_number(point.tokens_total))}</td>
          <td>{escape(fmt_seconds(point.active_seconds))}</td>
          <td>{escape(fmt_seconds(point.wall_seconds))}</td>
          <td>{escape(point.label)}</td>
        </tr>
        """
        for point in visible
    )


def render_dashboard(
    input_path: Path,
    title: str,
    ylabel: str,
    direction: str,
    x_axis: str,
    row_limit: int,
    refresh_seconds: int | None = None,
    target: float | None = None,
    hide_before_candidate: int = 3,
    score_scale: str = "auto",
    generated_at: str | None = None,
) -> str:
    points = read_points(input_path)
    usage, _, _ = state_snapshot(infer_state_path(input_path, None))
    snapshots = read_token_snapshots(infer_log_path(input_path, None))
    if snapshots:
        latest_snapshot = snapshots[-1]
        if usage is None:
            usage = latest_snapshot
        else:
            if usage.total_tokens is None:
                usage.total_tokens = latest_snapshot.total_tokens
            if usage.wall_seconds is None:
                usage.wall_seconds = latest_snapshot.wall_seconds
    chart = inline_chart(input_path, points, title, ylabel, direction, x_axis, target, hide_before_candidate, score_scale, generated_at)
    refresh = f'<meta http-equiv="refresh" content="{refresh_seconds}">' if refresh_seconds else ""
    latest = points[-1]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {refresh}
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f7f2;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #697386;
      --line: #ded8cc;
      --green: #188a50;
      --blue: #2563eb;
      --red: #c2410c;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 24px 28px 14px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: 24px;
      letter-spacing: 0;
    }}
    .meta {{
      color: var(--muted);
      font-size: 13px;
    }}
    main {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 18px 18px 36px;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin-bottom: 16px;
    }}
    .card, .chart, .table-wrap {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .card {{
      padding: 12px 14px;
    }}
    .card-label {{
      color: var(--muted);
      font-size: 12px;
    }}
    .card-value {{
      font-size: 23px;
      line-height: 1.15;
      margin-top: 5px;
      font-weight: 700;
    }}
    .card-sub {{
      margin-top: 5px;
      color: var(--muted);
      font-size: 12px;
    }}
    .chart {{
      overflow-x: auto;
      padding: 10px;
      margin-bottom: 16px;
    }}
    .chart svg {{
      display: block;
      max-width: 100%;
      height: auto;
      margin: 0 auto;
    }}
    .table-wrap {{
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      padding: 9px 10px;
      border-bottom: 1px solid #eee9df;
      text-align: left;
      vertical-align: top;
      white-space: nowrap;
    }}
    td:last-child, th:last-child {{
      white-space: normal;
      min-width: 220px;
    }}
    th {{
      color: var(--muted);
      font-weight: 650;
      background: #fbfaf7;
    }}
    .pill {{
      display: inline-block;
      border-radius: 999px;
      padding: 2px 8px;
      background: #ece7dc;
      color: var(--ink);
      font-size: 12px;
    }}
    .promote, .promoted, .keep, .kept, .baseline {{
      background: #dff3e8;
      color: var(--green);
    }}
    .bug, .crash, .blocked {{
      background: #ffedd5;
      color: var(--red);
    }}
    footer {{
      margin-top: 16px;
      color: var(--muted);
      font-size: 12px;
    }}
    footer a {{
      color: var(--blue);
      text-decoration: none;
    }}
    footer a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{escape(title)}</h1>
    <div class="meta">Source: {escape(str(input_path))} | latest event: {escape(latest.candidate)} | x-axis: {escape(x_axis)}</div>
  </header>
  <main>
    <div class="cards">
      {summary_cards(points, direction, usage)}
    </div>
    <section class="chart">{chart}</section>
    <section class="table-wrap">
      <table>
        <thead>
          <tr><th>#</th><th>Candidate</th><th>Decision</th><th>Score</th><th>Tokens</th><th>Active</th><th>Wall</th><th>Label</th></tr>
        </thead>
        <tbody>{rows(points, row_limit)}</tbody>
      </table>
    </section>
    <footer>Regenerate this file after new events, or run the dashboard server with SSH port forwarding for live remote review: ssh -L 8765:127.0.0.1:8765 &lt;user&gt;@&lt;remote-host&gt;. Built with <a href="{SKILL_URL}" target="_blank" rel="noopener noreferrer">{escape(SKILL_LINK_TEXT)}</a>.</footer>
  </main>
</body>
</html>
"""


def serve_dashboard(args: argparse.Namespace) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path not in {"/", "/dashboard.html"}:
                self.send_error(404)
                return
            try:
                html = render_dashboard(
                    args.input,
                    args.title,
                    args.ylabel,
                    args.direction,
                    args.x_axis,
                    args.rows,
                    args.refresh_seconds,
                    args.target,
                    args.hide_before_candidate,
                    args.score_scale,
                    generated_at_value(args.generated_at, args.no_generated_at),
                )
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(html, encoding="utf-8")
            except Exception as exc:  # pragma: no cover - exercised manually.
                self.send_error(500, str(exc))
                return
            payload = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"http://{args.host}:{args.port}")
    print(f"remote tunnel: ssh -L {args.port}:127.0.0.1:{args.port} <user>@<remote-host>")
    server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="Render or serve a zero-dependency optimization progress dashboard.")
    parser.add_argument("input", type=Path, nargs="?", default=Path("work/progress.tsv"))
    parser.add_argument("-o", "--output", type=Path, default=Path("work/dashboard.html"))
    parser.add_argument("--title", default="Optimization Dashboard")
    parser.add_argument("--ylabel", default="Authoritative metric")
    parser.add_argument("--direction", choices=("lower", "higher"), default="lower")
    parser.add_argument("--x-axis", choices=("candidate", "tokens", "active", "wall"), default="candidate")
    parser.add_argument("--target", type=float, help="Target score line for the embedded SVG")
    parser.add_argument("--hide-before-candidate", type=int, default=3, help="Hide early candidate numbers below this value when possible")
    parser.add_argument("--score-scale", choices=("auto", "log", "linear"), default="auto", help="Score y-axis scale for the embedded SVG")
    parser.add_argument("--generated-at", help="Fixed generation timestamp for deterministic embedded SVG output; ISO-8601, normalized to UTC Z")
    parser.add_argument("--no-generated-at", action="store_true", help="Omit the embedded SVG generated timestamp footer")
    parser.add_argument("--rows", type=int, default=30, help="Recent rows to include in the table")
    parser.add_argument("--serve", action="store_true", help="Serve live HTML and regenerate on each request")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--refresh-seconds", type=int, default=15)
    args = parser.parse_args()

    if args.serve:
        serve_dashboard(args)
        return 0

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
        generated_at_value(args.generated_at, args.no_generated_at),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
