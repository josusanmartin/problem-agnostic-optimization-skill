from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
CHART_SCRIPT = REPO_ROOT / "skills" / "problem-agnostic-optimization" / "scripts" / "progress_chart.py"
RUN_DASHBOARD_SCRIPT = REPO_ROOT / "skills" / "problem-agnostic-optimization" / "scripts" / "progress_dashboard.py"
RECORD_SCRIPT = REPO_ROOT / "skills" / "problem-agnostic-optimization" / "scripts" / "record_event.py"


def test_progress_chart_renders_svg_with_tokens_axis(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"
    log = tmp_path / "log.md"
    state = tmp_path / "state.json"
    progress.write_text(
        "\t".join(["timestamp", "candidate", "score", "decision", "tokens_total", "tokens_delta", "label"]) + "\n"
        + "2026-06-01T00:00:00Z\tcand_0000\t1.000\tbaseline\t1000\t1000\tbaseline\n"
        + "2026-06-01T00:05:00Z\tcand_0001\t0.990\tpromote\t2500\t1500\tfirst win\n"
        + "2026-06-01T00:10:00Z\tcand_0002\t0.995\treject\t3600\t1100\tbad branch\n"
        + "2026-06-01T00:15:00Z\tcand_0003\t0.982\tkeep\t5200\t1600\tsecond win\n",
        encoding="utf-8",
    )
    log.write_text(
        "# Optimization Log\n\n"
        "## get_goal usage snapshot C1\n"
        '{"tokensUsed":2500,"timeUsedSeconds":300,"input_tokens":2000,"cached_input_tokens":1200,"output_tokens":500,"reasoning_output_tokens":300,"best_score":0.990}\n'
        "## get_goal usage snapshot C3\n"
        '{"tokensUsed":5200,"timeUsedSeconds":900,"input_tokens":4200,"cached_input_tokens":3000,"output_tokens":1000,"reasoning_output_tokens":600,"best_score":0.982}\n',
        encoding="utf-8",
    )
    state.write_text(
        json.dumps(
            {
                "best_stable_score": 0.982,
                "progress": {
                    "latest_usage_snapshot": {
                        "total_tokens": 5200,
                        "wall_seconds": 900,
                        "input_tokens": 4200,
                        "cached_input_tokens": 3000,
                        "output_tokens": 1000,
                        "reasoning_output_tokens": 600,
                    }
                },
            }
        ),
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
    assert "Recorded Token Usage" in svg
    assert "Cumulative tokens" in svg
    assert "Candidate number" in svg
    assert "protected best" in svg
    assert "current usage snapshot" in svg
    assert "second win" in svg
    assert "dashed token category lines" in svg
    assert ">-" not in svg


def test_progress_chart_reads_cycles_status_description_tsv(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"
    progress.write_text(
        "timestamp\tcandidate\tcycles\tstatus\ttokens_total\ttokens_delta\tdescription\n"
        "2026-06-01T00:00:00Z\t0\t147734\tbaseline\t1200\t1200\tscalar starter baseline\n"
        "2026-06-01T00:10:00Z\t1\t3360\tpromote\t3100\t1900\tvectorized full gather, scratch values and paths\n"
        "2026-06-01T00:18:00Z\t2\t2226\tpromote\t4500\t1400\tdependency-list scheduled vector kernel\n"
        "2026-06-01T00:25:00Z\t3\t2117\tpromote\t5900\t1400\tdepth-1 runtime-loaded two-node lookup\n"
        "2026-06-01T00:34:00Z\t4\t2104\tpromote\t7600\t1700\tdepth-2 four-node affine lookup\n"
        "2026-06-01T00:44:00Z\t5\t1788\tpromote\t9700\t2100\tglobal cross-round dependency scheduler\n"
        "2026-06-01T00:53:00Z\t6\t1779\tpromote\t11200\t1500\tpacked vector-constant initialization\n"
        "2026-06-01T01:00:00Z\t7\t1771\tpromote\t12600\t1400\troot assignment with bit extract\n"
        "2026-06-01T01:09:00Z\t8\t1751\tpromote\t14500\t1900\troute one vector block through scalar ALU\n"
        "2026-06-01T01:18:00Z\t9\t1708\tpromote\t16100\t1600\tbracket scalar ALU split\n"
        "2026-06-01T01:27:00Z\t10\t1587\tpromote\t18100\t2000\tdepth-2 lookup via flow vselect\n"
        "2026-06-01T01:35:00Z\t11\t1561\tpromote\t19800\t1700\tround-robin depth-2 temp vectors\n"
        "2026-06-01T01:42:00Z\t12\t1560\tpromote\t21100\t1300\tremove unused zero vector initialization\n"
        "2026-06-01T01:50:00Z\t13\t1547\tpromote\t22700\t1600\tdepth-1 flow vselect lookup\n"
        "2026-06-01T01:57:00Z\t14\t1544\tpromote\t24100\t1400\tre-bracket depth-2 temp count\n"
        "2026-06-01T02:06:00Z\t15\t1542\tpromote\t25900\t1800\tswitch deeper paths to absolute forest addresses\n"
        "2026-06-01T02:15:00Z\t16\t1541\tpromote\t27400\t1500\troute first four blocks through scalar ALU\n"
        "2026-06-01T02:24:00Z\t17\t1536\tpromote\t29200\t1800\tre-bracket scalar split with front blocks\n"
        "2026-06-01T02:32:00Z\t18\t1533\tpromote\t30900\t1700\tre-bracket depth-2 temp count with five scalar blocks\n"
        "2026-06-01T02:42:00Z\t19\t1501\tpromote\t32900\t2000\tscreen scalar block placement\n",
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
            "Cycle Progress",
            "--ylabel",
            "Cycles",
            "--direction",
            "lower",
            "--x-axis",
            "wall",
            "--target",
            "1000",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    svg = output.read_text(encoding="utf-8")
    assert "Cycle Progress" in svg
    assert "Cycles" in svg
    assert "Candidate number" in svg
    assert "Recorded Token Usage" in svg
    assert "Cumulative tokens" in svg
    assert "legacy token columns" in svg
    assert "target &lt;1000" in svg
    assert "Candidates 0-2 hidden for scale" in svg
    assert "screen scalar block placement" in svg


def test_progress_chart_uses_legacy_token_columns_when_no_snapshots_exist(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"
    progress.write_text(
        "timestamp\tcandidate\tscore\tstatus\ttokens_total\twall_seconds\tdescription\n"
        "2026-06-01T00:00:00Z\tcand_0000\t1.0\tbaseline\t1000\t0\tbaseline\n"
        "2026-06-01T00:03:00Z\tcand_0001\t0.9\tpromote\t2400\t180\tlegacy win\n"
        "2026-06-01T00:05:00Z\tcand_0002\t0.91\treject\t3100\t300\tlegacy reject\n",
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
            "Legacy Tokens",
            "--ylabel",
            "Score",
            "--direction",
            "lower",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    svg = output.read_text(encoding="utf-8")
    assert "legacy token columns" in svg
    assert "no explicit get_goal token snapshots" not in svg
    assert "legacy win" in svg


def test_progress_chart_auto_uses_linear_for_zero_and_negative_scores(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"
    progress.write_text(
        "candidate\tscore\tstatus\tdescription\n"
        "cand_0000\t0.0\tbaseline\tzero baseline\n"
        "cand_0001\t-0.2\tpromote\tnegative win\n"
        "cand_0002\t-0.1\treject\tnegative reject\n",
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
            "Signed Score Progress",
            "--ylabel",
            "Delta",
            "--direction",
            "lower",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    svg = output.read_text(encoding="utf-8")
    assert "Delta, linear scale" in svg
    assert "zero baseline" in svg
    assert "negative win" in svg


def test_progress_chart_rejects_log_scale_for_non_positive_scores(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"
    progress.write_text(
        "candidate\tscore\tstatus\tdescription\n"
        "cand_0000\t0.0\tbaseline\tzero baseline\n"
        "cand_0001\t-0.2\tpromote\tnegative win\n",
        encoding="utf-8",
    )
    output = tmp_path / "progress.svg"

    result = subprocess.run(
        [
            sys.executable,
            str(CHART_SCRIPT),
            str(progress),
            "-o",
            str(output),
            "--score-scale",
            "log",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "log score scale requires" in result.stderr


def test_progress_chart_uses_row_index_for_ambiguous_candidate_digits(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"
    progress.write_text(
        "candidate\tscore\tstatus\tdescription\n"
        "baseline-v2\t1.0\tbaseline\tbaseline with version suffix\n"
        "exp-2026-06-01\t0.9\tpromote\tdate-like candidate id\n"
        "route4-retry2\t0.91\treject\ttrailing retry id\n",
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
            "Ambiguous Candidates",
            "--ylabel",
            "Score",
            "--direction",
            "lower",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    svg = output.read_text(encoding="utf-8")
    assert "displayed candidates 0-2" in svg
    assert "date-like candidate id" in svg


def test_keep_does_not_update_protected_best(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"
    progress.write_text(
        "candidate\tscore\tstatus\tdescription\n"
        "cand_0000\t1.0\tbaseline\tbaseline\n"
        "cand_0001\t0.9\tpromote\tcanonical promotion\n"
        "cand_0002\t0.8\tkeep\tkept but not promoted\n",
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
            "Keep Semantics",
            "--ylabel",
            "Score",
            "--direction",
            "lower",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    svg = output.read_text(encoding="utf-8")
    assert "protected best: 0.9 Score" in svg
    assert "protected best: 0.8 Score" not in svg


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
    assert "Candidate number" in svg
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


def test_record_event_keeps_nullable_token_and_time_fields(tmp_path: Path) -> None:
    events = tmp_path / "events.jsonl"

    subprocess.run(
        [
            sys.executable,
            str(RECORD_SCRIPT),
            "--events",
            str(events),
            "--candidate",
            "cand_0001",
            "--decision",
            "reject",
            "--score",
            "0.99",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    record = json.loads(events.read_text(encoding="utf-8"))
    assert "tokens_total" in record
    assert "tokens_delta" in record
    assert "active_seconds" in record
    assert "wall_seconds" in record
    assert record["tokens_total"] is None
    assert record["tokens_delta"] is None
    assert record["active_seconds"] is None
    assert record["wall_seconds"] is None


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
