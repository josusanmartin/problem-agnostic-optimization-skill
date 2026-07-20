from __future__ import annotations

import importlib.util
from pathlib import Path
import re
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

    assert len(text.split()) < 1400
    assert "Ten percent of the active contract budget" in text
    assert "Three consecutive same-family measured candidates" in text
    assert "wrapping thousands of evaluations in one candidate does not reset stagnation" in text
    assert "A plateau is not a floor proof." in text
    assert "One mechanism may require coordinated edits." in text
    assert "checkpoint" in text.lower()
    assert "operational work, not optimization candidates or promotions" in text
    assert "spend the next measured candidate off-hill" in text
    assert "The user may override either direction" in text
    assert "A written sweep or family attempt budget is exhausted" in text


def test_default_prompt_explicitly_invokes_skill() -> None:
    text = (SKILL_SRC / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert "$problem-agnostic-optimization" in text
    assert "route this challenge first" in text


def test_router_is_first_and_forbids_bulk_loading() -> None:
    text = (SKILL_SRC / "SKILL.md").read_text(encoding="utf-8")

    assert text.index("## Route First") < text.index("## Contract")
    assert "select exactly one primary route" in text
    assert "Do not read every reference" in text
    assert "References are opt-in modules, not a reading list." in text
    assert "follow references recursively" in text


def test_gpu_and_service_routes_are_isolated() -> None:
    text = (SKILL_SRC / "SKILL.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    gpu_row = next(line for line in lines if "CUDA, HIP/ROCm" in line)
    service_row = next(line for line in lines if "HighLoad-style" in line)

    assert "references/gpu-architecture.md" in gpu_row
    assert "cpu-architecture" not in gpu_row
    assert "service-throughput" not in gpu_row
    assert "references/service-throughput.md" in service_row
    assert "gpu-architecture" not in service_row

    gpu = (SKILL_SRC / "references" / "gpu-architecture.md").read_text(encoding="utf-8")
    cpu = (SKILL_SRC / "references" / "cpu-architecture.md").read_text(encoding="utf-8")
    service = (SKILL_SRC / "references" / "service-throughput.md").read_text(encoding="utf-8")
    assert "highload" not in gpu.lower()
    assert "highload" not in cpu.lower()
    assert "highload" in service.lower()


def test_every_reference_is_routed_once_without_recursive_links() -> None:
    text = (SKILL_SRC / "SKILL.md").read_text(encoding="utf-8")
    routed_matches = re.findall(r"`references/([a-z0-9-]+\.md)`", text)
    routed = set(routed_matches)
    actual = {path.name for path in (SKILL_SRC / "references").glob("*.md")}

    assert len(routed_matches) == len(routed)
    assert routed == actual
    assert "problem-families.md" not in actual
    for path in (SKILL_SRC / "references").glob("*.md"):
        module_text = path.read_text(encoding="utf-8")
        assert not re.search(r"(?:references/)?[a-z0-9-]+\.md", module_text), path.name


def test_operation_modules_stay_small() -> None:
    module_names = [
        "fixed-resource-scheduling.md",
        "kernel-attention-moe.md",
        "kernel-elementwise.md",
        "kernel-histogram.md",
        "kernel-matrix.md",
        "kernel-quantized.md",
        "kernel-reductions-scans.md",
        "kernel-stencils-convolution.md",
        "runtime-overhead.md",
        "service-throughput.md",
    ]

    for name in module_names:
        text = (SKILL_SRC / "references" / name).read_text(encoding="utf-8")
        assert len(text.split()) < 400, name


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


def test_unrouted_reference_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    (skill_dir / "references" / "orphan.md").write_text("# Orphan\n", encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="unrouted reference modules: orphan.md"):
        validate_skill.validate_skill(skill_dir)


def test_recursive_reference_link_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    module = skill_dir / "references" / "gpu-architecture.md"
    module.write_text(
        module.read_text(encoding="utf-8") + "\nRead `service-throughput.md`.\n",
        encoding="utf-8",
    )

    with pytest.raises(validate_skill.ValidationError, match="gpu-architecture.md links recursively"):
        validate_skill.validate_skill(skill_dir)


def test_router_must_precede_contract(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    text = text.replace("## Route First", "## Deferred Router", 1)
    skill.write_text(text + "\n## Route First\n", encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="router must precede"):
        validate_skill.validate_skill(skill_dir)


def test_frontier_reference_preserves_integrated_search_doctrine() -> None:
    text = (SKILL_SRC / "references" / "frontier-introspection.md").read_text(encoding="utf-8")

    required = (
        "## Triangulate Multiple Frontiers",
        "`mapping-negative`",
        "`availability-negative`",
        "## Write The Phase Contract",
        "## Keep A Precision Ledger",
        "## Reserve An Architecture Budget",
        "## Diagnose With Stage Cuts",
    )
    for phrase in required:
        assert phrase in text


@pytest.mark.parametrize(
    "reference_name",
    ["evidence-loop.md", "frontier-introspection.md", "gpu-architecture.md", "service-throughput.md"],
)
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
    assert "Search-health accounting is active decision state, not a logging requirement." in text
    assert "When Scorebench is active" in text
    assert "derive attempts, budget use, promotion history, and best state from Scorebench" in text
    assert "Do not create parallel PAO logs or dashboards" in text


def test_readme_keeps_scorebench_boundary_and_attempt_accounting_clear() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "Scorebench exclusively owns" in text
    assert "5,000 measured configurations consumes 5,000 attempts" in text
    assert "Progress chart: on" not in text
    assert "scripts/init_harness.py" not in text
    assert "## Route First" in text
    assert "does not load CPU, HighLoad/service" in text
