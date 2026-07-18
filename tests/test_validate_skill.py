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


def test_core_skill_keeps_search_policy_concise_and_enforceable() -> None:
    text = (SKILL_SRC / "SKILL.md").read_text(encoding="utf-8")

    assert len(text.split()) < 1600
    assert "Ten percent of the available active-time" in text
    assert "Three consecutive same-family measured candidates" in text
    assert "wrapping thousands of evaluations in one candidate does not reset stagnation" in text
    assert "A plateau is not a floor proof" in text
    assert "Compound changes are appropriate" in text
    assert "checkpoint" in text.lower()
    assert "operational work, not a candidate or promotion" in text


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
    ref = skill_dir / "references" / "templates.md"
    ref.write_text(ref.read_text(encoding="utf-8") + "\nCafe é\n", encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="references/templates.md has non-ASCII"):
        validate_skill.validate_skill(skill_dir)


def test_invalid_utf8_fails_without_traceback(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    (skill_dir / "references" / "templates.md").write_bytes(b"\xff")

    with pytest.raises(validate_skill.ValidationError, match="references/templates.md is not valid UTF-8"):
        validate_skill.validate_skill(skill_dir)


@pytest.mark.parametrize("reference_name", ["auditor.md", "gpu-architecture.md"])
def test_missing_reference_fails(tmp_path: Path, reference_name: str) -> None:
    skill_dir = copy_skill(tmp_path)
    (skill_dir / "references" / reference_name).unlink()

    with pytest.raises(validate_skill.ValidationError, match=f"missing required file: references/{reference_name}"):
        validate_skill.validate_skill(skill_dir)


@pytest.mark.parametrize("script_name", ["init_harness.py", "progress_chart.py", "progress_dashboard.py", "render_progress.py", "record_event.py", "record_progress.py"])
def test_missing_skill_script_fails(tmp_path: Path, script_name: str) -> None:
    skill_dir = copy_skill(tmp_path)
    (skill_dir / "scripts" / script_name).unlink()

    with pytest.raises(validate_skill.ValidationError, match=f"missing required file: scripts/{script_name}"):
        validate_skill.validate_skill(skill_dir)
