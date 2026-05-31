from __future__ import annotations

from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
CHART_SCRIPT = REPO_ROOT / "skills" / "problem-agnostic-optimization" / "scripts" / "progress_chart.py"
RUN_DASHBOARD_SCRIPT = REPO_ROOT / "skills" / "problem-agnostic-optimization" / "scripts" / "progress_dashboard.py"
RECORD_SCRIPT = REPO_ROOT / "skills" / "problem-agnostic-optimization" / "scripts" / "record_event.py"


def test_progress_chart_renders_svg_with_tokens_axis(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"
    progress.write_text(
        "\t".join(["candidate", "score", "decision", "tokens_total", "label"]) + "\n"
        + "cand_0000\t1.000\tbaseline\t1000\tbaseline\n"
        + "cand_0001\t0.990\tpromote\t2500\tfirst win\n"
        + "cand_0002\t0.995\treject\t3600\tbad branch\n"
        + "cand_0003\t0.982\tkeep\t5200\tsecond win\n",
        encoding="utf-8",
    )
    output = tmp_path / "progress.svg"

    subprocess.run(
        [
            sys.executable,
            str(CHART_SCRIPT),
            str(progress),
            "-o",
            str(output),
            "--title",
            "Test Progress",
            "--ylabel",
            "Validation loss",
            "--direction",
            "lower",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    svg = output.read_text(encoding="utf-8")
    assert "<svg" in svg
    assert "Test Progress" in svg
    assert "Validation loss" in svg
    assert "Cumulative tokens" in svg
    assert "Running best" in svg
    assert "first win" in svg
    assert ">0k<" in svg
    assert ">-" not in svg


def test_progress_chart_reads_events_jsonl_and_active_axis(tmp_path: Path) -> None:
    events = tmp_path / "events.jsonl"
    events.write_text(
        '{"candidate":"cand_0000","decision":"baseline","score":1.0,"tokens_total":1000,"active_seconds":10,"label":"baseline"}\n'
        '{"candidate":"cand_0001","decision":"promote","score":0.99,"tokens_total":2400,"active_seconds":70,"label":"jsonl win"}\n'
        '{"candidate":"cand_0002","decision":"reject","score":0.995,"tokens_total":3100,"active_seconds":120,"label":"jsonl reject"}\n',
        encoding="utf-8",
    )
    output = tmp_path / "progress.svg"

    subprocess.run(
        [
            sys.executable,
            str(CHART_SCRIPT),
            str(events),
            "-o",
            str(output),
            "--title",
            "JSONL Progress",
            "--ylabel",
            "Runtime",
            "--direction",
            "lower",
            "--x-axis",
            "active",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    svg = output.read_text(encoding="utf-8")
    assert "JSONL Progress" in svg
    assert "Tracked active time" in svg
    assert "jsonl win" in svg
    assert "Cumulative tokens" in svg


def test_record_event_appends_jsonl_and_renders_chart(tmp_path: Path) -> None:
    events = tmp_path / "events.jsonl"
    chart = tmp_path / "progress.svg"

    subprocess.run(
        [
            sys.executable,
            str(RECORD_SCRIPT),
            "--events",
            str(events),
            "--candidate",
            "cand_0001",
            "--decision",
            "promote",
            "--score",
            "0.99",
            "--tokens-total",
            "2400",
            "--active-seconds",
            "70",
            "--label",
            "recorded win",
            "--chart",
            str(chart),
            "--direction",
            "lower",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"candidate":"cand_0001"' in events.read_text(encoding="utf-8")
    svg = chart.read_text(encoding="utf-8")
    assert "recorded win" in svg
    assert "Cumulative tokens" in svg


def test_progress_dashboard_renders_static_html(tmp_path: Path) -> None:
    events = tmp_path / "events.jsonl"
    events.write_text(
        '{"candidate":"cand_0000","decision":"baseline","score":1.0,"tokens_total":1000,"active_seconds":10,"wall_seconds":20,"label":"baseline"}\n'
        '{"candidate":"cand_0001","decision":"promote","score":0.99,"tokens_total":2400,"active_seconds":70,"wall_seconds":120,"label":"dashboard win"}\n'
        '{"candidate":"cand_0002","decision":"reject","score":0.995,"tokens_total":3100,"active_seconds":120,"wall_seconds":180,"label":"dashboard reject"}\n',
        encoding="utf-8",
    )
    output = tmp_path / "dashboard.html"

    subprocess.run(
        [
            sys.executable,
            str(RUN_DASHBOARD_SCRIPT),
            str(events),
            "-o",
            str(output),
            "--title",
            "Run Dashboard",
            "--ylabel",
            "Runtime",
            "--direction",
            "lower",
            "--x-axis",
            "tokens",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    html = output.read_text(encoding="utf-8")
    assert "<!doctype html>" in html
    assert "Run Dashboard" in html
    assert "dashboard win" in html
    assert "Cumulative tokens" in html
    assert "ssh -L" in html
