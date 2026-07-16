from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_SRC = REPO_ROOT / "skills" / "problem-agnostic-optimization"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_skill.py"

spec = importlib.util.spec_from_file_location("validate_skill", VALIDATOR_PATH)
assert spec is not None
validate_skill = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate_skill)


def copy_skill(tmp_path: Path) -> Path:
    skill_dir = tmp_path / "problem-agnostic-optimization"
    shutil.copytree(SKILL_SRC, skill_dir)
    return skill_dir


def test_valid_skill_passes(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)

    validate_skill.validate_skill(skill_dir)


def test_missing_openai_yaml_is_structured_error(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    (skill_dir / "agents" / "openai.yaml").unlink()

    with pytest.raises(validate_skill.ValidationError, match="missing required file: agents/openai.yaml"):
        validate_skill.validate_skill(skill_dir)


def test_invalid_skill_frontmatter_yaml_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    skill.write_text("---\nname: [unterminated\ndescription: bad\n---\n# Body\n", encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="frontmatter is invalid YAML"):
        validate_skill.validate_skill(skill_dir)


def test_invalid_openai_yaml_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    (skill_dir / "agents" / "openai.yaml").write_text("interface: [unterminated\n", encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="agents/openai.yaml is invalid YAML"):
        validate_skill.validate_skill(skill_dir)


def test_non_ascii_reference_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    ref = skill_dir / "references" / "evidence-loop.md"
    ref.write_text(ref.read_text(encoding="utf-8") + "\nCafe é\n", encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="references/evidence-loop.md has non-ASCII"):
        validate_skill.validate_skill(skill_dir)


def test_invalid_utf8_fails_without_traceback(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    (skill_dir / "references" / "evidence-loop.md").write_bytes(b"\xff")

    with pytest.raises(validate_skill.ValidationError, match="references/evidence-loop.md is not valid UTF-8"):
        validate_skill.validate_skill(skill_dir)


@pytest.mark.parametrize("reference_name", ["evidence-loop.md", "gpu-architecture.md"])
def test_missing_reference_fails(tmp_path: Path, reference_name: str) -> None:
    skill_dir = copy_skill(tmp_path)
    (skill_dir / "references" / reference_name).unlink()

    with pytest.raises(validate_skill.ValidationError, match=f"missing required file: references/{reference_name}"):
        validate_skill.validate_skill(skill_dir)


def test_skill_payload_has_no_bundled_logging_module() -> None:
    forbidden = [
        "references/auditor.md",
        "references/harness.md",
        "references/templates.md",
        "scripts/init_harness.py",
        "scripts/progress_chart.py",
        "scripts/progress_dashboard.py",
        "scripts/render_progress.py",
        "scripts/record_event.py",
        "scripts/record_progress.py",
    ]

    assert not [relative for relative in forbidden if (SKILL_SRC / relative).exists()]


def test_skill_defaults_to_no_logging_and_delegates_scorebench() -> None:
    text = (SKILL_SRC / "SKILL.md").read_text(encoding="utf-8")

    assert "Default behavior is no logging subsystem." in text
    assert "When Scorebench is active" in text
    assert "Do not create parallel PAO logs or dashboards" in text
