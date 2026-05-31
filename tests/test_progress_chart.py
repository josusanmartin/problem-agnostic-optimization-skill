from __future__ import annotations

from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
CHART_SCRIPT = REPO_ROOT / "skills" / "problem-agnostic-optimization" / "scripts" / "progress_chart.py"


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
