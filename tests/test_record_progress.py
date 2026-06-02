from __future__ import annotations

from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
RECORD_PROGRESS_SCRIPT = REPO_ROOT / "skills" / "problem-agnostic-optimization" / "scripts" / "record_progress.py"


def run_record_progress(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RECORD_PROGRESS_SCRIPT), *args],
        check=True,
        text=True,
        capture_output=True,
    )


def test_record_progress_creates_metric_specific_tsv_with_utc_timestamp(tmp_path: Path) -> None:
    progress = tmp_path / "work" / "progress.tsv"

    run_record_progress(
        "--progress",
        str(progress),
        "--timestamp",
        "2026-06-01T02:18:00+02:00",
        "--candidate",
        "cand_0007",
        "--metric",
        "cycles=2226",
        "--decision",
        "promote",
        "--tokens-total",
        "4500",
        "--tokens-delta",
        "1400",
        "--wall-seconds",
        "1080",
        "--label",
        "dependency-list scheduled vector kernel",
    )

    assert progress.read_text(encoding="utf-8") == (
        "timestamp\tcandidate\tcycles\tdecision\ttokens_total\ttokens_delta\twall_seconds\tlabel\n"
        "2026-06-01T00:18:00Z\tcand_0007\t2226\tpromote\t4500\t1400\t1080\tdependency-list scheduled vector kernel\n"
    )


def test_record_progress_appends_and_preserves_blank_token_fields(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"

    run_record_progress(
        "--progress",
        str(progress),
        "--timestamp",
        "2026-06-01T00:00:00Z",
        "--candidate",
        "cand_0000",
        "--score",
        "1.0",
        "--decision",
        "baseline",
        "--tokens-total",
        "1000",
        "--label",
        "baseline",
    )
    run_record_progress(
        "--progress",
        str(progress),
        "--timestamp",
        "2026-06-01T00:05:00Z",
        "--candidate",
        "cand_0001",
        "--score",
        "0.9",
        "--decision",
        "promote",
        "--tokens-total",
        "2400",
        "--wall-seconds",
        "300",
        "--label",
        "win",
    )

    assert progress.read_text(encoding="utf-8") == (
        "timestamp\tcandidate\tscore\tdecision\ttokens_total\ttokens_delta\twall_seconds\tlabel\n"
        "2026-06-01T00:00:00Z\tcand_0000\t1.0\tbaseline\t1000\t\t\tbaseline\n"
        "2026-06-01T00:05:00Z\tcand_0001\t0.9\tpromote\t2400\t1400\t300\twin\n"
    )


def test_record_progress_writes_blank_metric_for_bug_rows(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"

    run_record_progress(
        "--progress",
        str(progress),
        "--timestamp",
        "2026-06-01T00:00:00Z",
        "--candidate",
        "cand_0002",
        "--metric-name",
        "cycles",
        "--decision",
        "bug",
        "--label",
        "correctness failure",
    )

    assert progress.read_text(encoding="utf-8") == (
        "timestamp\tcandidate\tcycles\tdecision\ttokens_total\ttokens_delta\twall_seconds\tlabel\n"
        "2026-06-01T00:00:00Z\tcand_0002\t\tbug\t\t\t\tcorrectness failure\n"
    )


def test_record_progress_rejects_metric_mismatch_with_existing_header(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"
    progress.write_text(
        "timestamp\tcandidate\tscore\tdecision\ttokens_total\ttokens_delta\twall_seconds\tlabel\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(RECORD_PROGRESS_SCRIPT),
            "--progress",
            str(progress),
            "--candidate",
            "cand_0001",
            "--metric",
            "cycles=2226",
            "--decision",
            "promote",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "missing metric column 'cycles'" in result.stderr


def test_record_progress_supports_candidate_number_when_creating_file(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"

    run_record_progress(
        "--progress",
        str(progress),
        "--timestamp",
        "2026-06-01T00:00:00Z",
        "--candidate",
        "exp-2026-06-01",
        "--candidate-number",
        "7",
        "--metric",
        "cycles=2226",
        "--decision",
        "promote",
        "--label",
        "date-like candidate id",
    )

    assert progress.read_text(encoding="utf-8") == (
        "timestamp\tcandidate\tcandidate_number\tcycles\tdecision\ttokens_total\ttokens_delta\twall_seconds\tlabel\n"
        "2026-06-01T00:00:00Z\texp-2026-06-01\t7\t2226\tpromote\t\t\t\tdate-like candidate id\n"
    )


def test_record_progress_rejects_candidate_number_when_existing_header_lacks_column(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"
    progress.write_text(
        "timestamp\tcandidate\tscore\tdecision\ttokens_total\ttokens_delta\twall_seconds\tlabel\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(RECORD_PROGRESS_SCRIPT),
            "--progress",
            str(progress),
            "--candidate",
            "exp-2026-06-01",
            "--candidate-number",
            "7",
            "--score",
            "0.9",
            "--decision",
            "promote",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "missing candidate_number column" in result.stderr


def test_record_progress_writes_blank_candidate_number_when_header_has_column(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"
    progress.write_text(
        "timestamp\tcandidate\tcandidate_number\tscore\tdecision\ttokens_total\ttokens_delta\twall_seconds\tlabel\n",
        encoding="utf-8",
    )

    run_record_progress(
        "--progress",
        str(progress),
        "--timestamp",
        "2026-06-01T00:00:00Z",
        "--candidate",
        "cand_0001",
        "--score",
        "0.9",
        "--decision",
        "promote",
        "--label",
        "normal candidate id",
    )

    assert progress.read_text(encoding="utf-8") == (
        "timestamp\tcandidate\tcandidate_number\tscore\tdecision\ttokens_total\ttokens_delta\twall_seconds\tlabel\n"
        "2026-06-01T00:00:00Z\tcand_0001\t\t0.9\tpromote\t\t\t\tnormal candidate id\n"
    )


def test_record_progress_rejects_multiline_tsv_cells(tmp_path: Path) -> None:
    progress = tmp_path / "progress.tsv"

    result = subprocess.run(
        [
            sys.executable,
            str(RECORD_PROGRESS_SCRIPT),
            "--progress",
            str(progress),
            "--candidate",
            "cand_0001",
            "--score",
            "0.9",
            "--decision",
            "promote",
            "--label",
            "first line\nsecond line",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "--label cannot contain tabs or newlines" in result.stderr
    assert not progress.exists()
