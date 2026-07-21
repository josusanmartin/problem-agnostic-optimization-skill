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

SKILL_TEXT = (SKILL_SRC / "SKILL.md").read_text(encoding="utf-8")
ROUTER_ROWS = tuple(validate_skill.parse_router_rows(SKILL_TEXT))
ROUTER_ROWS_WITH_MODULE = tuple(row for row in ROUTER_ROWS if row.reference is not None)
ROUTED_REFERENCES = tuple(sorted(row.reference for row in ROUTER_ROWS_WITH_MODULE))


def copy_skill(tmp_path: Path) -> Path:
    skill_dir = tmp_path / "problem-agnostic-optimization"
    shutil.copytree(SKILL_SRC, skill_dir)
    return skill_dir


def remove_router_row(skill_dir: Path, row: validate_skill.RouterRow) -> None:
    skill_path = skill_dir / "SKILL.md"
    lines = skill_path.read_text(encoding="utf-8").splitlines()
    assert row.line in lines
    lines.remove(row.line)
    skill_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def reference_text(name: str) -> str:
    return (SKILL_SRC / "references" / name).read_text(encoding="utf-8")


def primary_loaded_context_words() -> dict[str, int]:
    shape_modules = {
        row.reference
        for row in ROUTER_ROWS
        if row.section == "### GPU Kernel Shape" and row.reference is not None
    }
    max_shape_words = max(len(reference_text(name).split()) for name in shape_modules)
    contexts: dict[str, int] = {}
    for row in ROUTER_ROWS:
        if row.section != "### Primary Route":
            continue
        words = len(SKILL_TEXT.split())
        if row.reference is not None:
            words += len(reference_text(row.reference).split())
        if row.route_id == "gpu":
            words += max_shape_words
        contexts[row.route_id] = words
    return contexts


def test_valid_skill_passes(tmp_path: Path) -> None:
    validate_skill.validate_skill(copy_skill(tmp_path))


def test_core_skill_is_lean_and_search_policy_is_unambiguous() -> None:
    assert len(SKILL_TEXT.split()) <= validate_skill.MAX_SKILL_WORDS
    required = (
        "Scope before floors:",
        "Structure before local tuning:",
        "Screen many, gate few:",
        "full correctness and authority gate every promotion",
        "Use `/goal` when the user requests a substantial run.",
        "A search epoch opens only after the authoritative baseline",
        "A candidate miss is one valid, comparable authoritative decision",
        "Screen rejections, `BUG`, `BLOCKED`",
        "Three consecutive comparable same-family candidate decisions miss.",
        "At least three measured attempts have occurred and ten percent of the active contract budget has been consumed",
        "Samples count as attempts, while the bounded sweep outcome is one candidate-family decision.",
        "before every sweep or screening round",
        "do not increment or reset the miss streak",
        "an explained implementation bug leaves a faithful test untried",
        "spend the next measured candidate off-hill by default",
        "meaningful authoritative promotion",
        "A plateau is not a floor proof.",
        "One mechanism may require coordinated edits.",
    )
    for phrase in required:
        assert phrase in SKILL_TEXT
    assert "Random search is a finisher, not an architect" not in SKILL_TEXT
    assert "Use `/goal` for substantial work." not in SKILL_TEXT


def test_router_precedence_uses_scored_artifact_semantics() -> None:
    primary = [row for row in ROUTER_ROWS if row.section == "### Primary Route"]

    assert [row.route_id for row in primary] == [
        "policy",
        "service",
        "fixed-resource",
        "gpu",
        "cpu",
        "other",
    ]
    assert "Scored-artifact semantics outrank" in SKILL_TEXT
    assert "even when implemented on CPU/GPU" in primary[0].line
    assert "request/response" in primary[1].line
    assert "HighLoad" not in primary[1].line
    assert "generated schedule" in primary[2].line
    assert "VLIW" in primary[2].line
    assert "Schedule, cycle count" not in primary[2].line
    assert "profiling-protocol uncertainty" in next(row for row in ROUTER_ROWS if row.route_id == "measurement").line
    assert "profiling need" not in next(row for row in ROUTER_ROWS if row.route_id == "measurement").line
    assert "Use this table only with the `gpu` primary route." in SKILL_TEXT
    assert "Replace stale modules when the bottleneck changes" in SKILL_TEXT
    assert "do not accumulate routes." in SKILL_TEXT


def test_gpu_and_service_routes_are_isolated() -> None:
    gpu = reference_text("gpu-architecture.md")
    cpu = reference_text("cpu-architecture.md")
    service = reference_text("service-throughput.md")

    assert "production GPU services" not in gpu
    assert "Route end-to-end request services separately." in gpu
    assert "HighLoad" not in gpu
    assert "HighLoad" not in cpu
    assert "HighLoad" in service


def test_default_prompt_explicitly_invokes_skill() -> None:
    text = (SKILL_SRC / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert "$problem-agnostic-optimization" in text
    assert "route this challenge first" in text


def test_every_reference_is_routed_once() -> None:
    actual = tuple(validate_skill.actual_reference_paths(SKILL_SRC / "references"))

    assert ROUTED_REFERENCES == actual
    assert len(ROUTED_REFERENCES) == len(set(ROUTED_REFERENCES))
    assert "problem-families.md" not in actual


def test_reference_size_budgets_cover_every_module() -> None:
    shape_modules = {
        row.reference
        for row in ROUTER_ROWS
        if row.section == "### GPU Kernel Shape" and row.reference is not None
    }
    for name in ROUTED_REFERENCES:
        words = len(reference_text(name).split())
        limit = validate_skill.SPECIAL_REFERENCE_WORD_LIMITS.get(
            name,
            validate_skill.MAX_SHAPE_WORDS if name in shape_modules else validate_skill.MAX_REFERENCE_WORDS,
        )
        assert words <= limit, f"{name}: {words} > {limit}"


@pytest.mark.parametrize("reference_name", sorted(validate_skill.SPECIAL_REFERENCE_WORD_LIMITS))
def test_special_reference_size_budget_fails(tmp_path: Path, reference_name: str) -> None:
    skill_dir = copy_skill(tmp_path)
    reference = skill_dir / "references" / reference_name
    limit = validate_skill.SPECIAL_REFERENCE_WORD_LIMITS[reference_name]
    overflow_words = limit - len(reference.read_text(encoding="utf-8").split()) + 1
    assert overflow_words > 0
    reference.write_text(
        reference.read_text(encoding="utf-8") + "\n" + "filler " * overflow_words,
        encoding="utf-8",
    )

    with pytest.raises(
        validate_skill.ValidationError,
        match=rf"references/{reference_name} exceeds {limit} words",
    ):
        validate_skill.validate_skill(skill_dir)


def test_primary_route_loaded_context_budget_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    skill_dir = copy_skill(tmp_path)
    route_id, loaded_words = max(primary_loaded_context_words().items(), key=lambda item: item[1])
    limit = loaded_words - 1
    monkeypatch.setattr(validate_skill, "MAX_PRIMARY_CONTEXT_WORDS", limit)

    with pytest.raises(
        validate_skill.ValidationError,
        match=rf"primary route {route_id} exceeds {limit} loaded words",
    ):
        validate_skill.validate_skill(skill_dir)


def test_primary_plus_measurement_loaded_context_budget_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    skill_dir = copy_skill(tmp_path)
    measurement_words = len(reference_text("evidence-loop.md").split())
    route_id, loaded_words = max(
        (
            (route_id, route_words + measurement_words)
            for route_id, route_words in primary_loaded_context_words().items()
        ),
        key=lambda item: item[1],
    )
    limit = loaded_words - 1
    monkeypatch.setattr(validate_skill, "MAX_PRIMARY_MEASUREMENT_CONTEXT_WORDS", limit)

    with pytest.raises(
        validate_skill.ValidationError,
        match=rf"primary route {route_id} plus measurement exceeds {limit} loaded words",
    ):
        validate_skill.validate_skill(skill_dir)


def test_long_references_have_contents_map() -> None:
    for name in ROUTED_REFERENCES:
        text = reference_text(name)
        if len(text.splitlines()) > 100:
            assert "## Contents" in text, name


@pytest.mark.parametrize("reference_name", ROUTED_REFERENCES)
def test_missing_reference_fails(tmp_path: Path, reference_name: str) -> None:
    skill_dir = copy_skill(tmp_path)
    (skill_dir / "references" / reference_name).unlink()

    with pytest.raises(validate_skill.ValidationError, match="missing routed reference modules"):
        validate_skill.validate_skill(skill_dir)


@pytest.mark.parametrize("row", ROUTER_ROWS_WITH_MODULE, ids=lambda row: row.route_id)
def test_missing_router_row_fails(tmp_path: Path, row: validate_skill.RouterRow) -> None:
    skill_dir = copy_skill(tmp_path)
    remove_router_row(skill_dir, row)

    with pytest.raises(validate_skill.ValidationError, match="missing ids"):
        validate_skill.validate_skill(skill_dir)


@pytest.mark.parametrize("row", ROUTER_ROWS_WITH_MODULE, ids=lambda row: row.route_id)
def test_paired_module_and_router_row_deletion_still_fails(
    tmp_path: Path, row: validate_skill.RouterRow
) -> None:
    skill_dir = copy_skill(tmp_path)
    assert row.reference is not None
    (skill_dir / "references" / row.reference).unlink()
    remove_router_row(skill_dir, row)

    with pytest.raises(validate_skill.ValidationError, match="missing ids"):
        validate_skill.validate_skill(skill_dir)


def test_prose_reference_outside_router_does_not_duplicate_route(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8")
        + "\nCompatibility prose may mention `references/gpu-architecture.md` without routing it.\n",
        encoding="utf-8",
    )

    validate_skill.validate_skill(skill_dir)


def test_duplicate_router_row_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    row = ROUTER_ROWS_WITH_MODULE[0]
    text = skill.read_text(encoding="utf-8")
    skill.write_text(text.replace(row.line, f"{row.line}\n{row.line}", 1), encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="duplicate router id"):
        validate_skill.validate_skill(skill_dir)


def test_other_route_cannot_load_a_module(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    row = next(row for row in ROUTER_ROWS if row.route_id == "other")
    replacement = row.line.replace(
        "No primary module; use the core until evidence selects one",
        "`references/cpu-architecture.md`",
    )
    skill.write_text(
        skill.read_text(encoding="utf-8").replace(row.line, replacement, 1),
        encoding="utf-8",
    )

    with pytest.raises(validate_skill.ValidationError, match="other must not load a module"):
        validate_skill.validate_skill(skill_dir)


def test_same_module_cannot_be_routed_twice(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    source = next(row for row in ROUTER_ROWS_WITH_MODULE if row.route_id == "elementwise")
    target = next(row for row in ROUTER_ROWS_WITH_MODULE if row.route_id == "matrix")
    assert source.reference is not None
    assert target.reference is not None
    replacement = source.line.replace(
        f"`references/{source.reference}`",
        f"`references/{target.reference}`",
    )
    skill.write_text(
        skill.read_text(encoding="utf-8").replace(source.line, replacement, 1),
        encoding="utf-8",
    )

    with pytest.raises(validate_skill.ValidationError, match="reference modules routed more than once"):
        validate_skill.validate_skill(skill_dir)


def test_router_row_cannot_load_two_modules(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    row = next(row for row in ROUTER_ROWS_WITH_MODULE if row.route_id == "measurement")
    assert row.reference is not None
    replacement = row.line.replace(
        f"`references/{row.reference}`",
        f"`references/{row.reference}` and `references/resource-models.md`",
    )
    skill.write_text(
        skill.read_text(encoding="utf-8").replace(row.line, replacement, 1),
        encoding="utf-8",
    )

    with pytest.raises(validate_skill.ValidationError, match="measurement must load exactly one module"):
        validate_skill.validate_skill(skill_dir)


def test_router_subsections_must_keep_order(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    text = text.replace("### Primary Route", "@@PRIMARY@@", 1)
    text = text.replace("### Evidence-Triggered Add-ons", "### Primary Route", 1)
    text = text.replace("@@PRIMARY@@", "### Evidence-Triggered Add-ons", 1)
    skill.write_text(text, encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="router subsections are out of order"):
        validate_skill.validate_skill(skill_dir)


def test_nested_dangling_router_path_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    row = ROUTER_ROWS_WITH_MODULE[0]
    assert row.reference is not None
    text = skill.read_text(encoding="utf-8")
    skill.write_text(
        text.replace(f"references/{row.reference}", "references/nested/missing.md", 1),
        encoding="utf-8",
    )

    with pytest.raises(validate_skill.ValidationError, match="missing routed reference modules: nested/missing.md"):
        validate_skill.validate_skill(skill_dir)


def test_router_path_traversal_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    row = ROUTER_ROWS_WITH_MODULE[0]
    assert row.reference is not None
    text = skill.read_text(encoding="utf-8")
    skill.write_text(
        text.replace(f"references/{row.reference}", "references/../escape.md", 1),
        encoding="utf-8",
    )

    with pytest.raises(validate_skill.ValidationError, match="invalid router reference path"):
        validate_skill.validate_skill(skill_dir)


def test_router_anchor_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    row = ROUTER_ROWS_WITH_MODULE[0]
    assert row.reference is not None
    text = skill.read_text(encoding="utf-8")
    skill.write_text(
        text.replace(f"references/{row.reference}", f"references/{row.reference}#section", 1),
        encoding="utf-8",
    )

    with pytest.raises(validate_skill.ValidationError, match="must load a whole module"):
        validate_skill.validate_skill(skill_dir)


def test_route_heading_must_be_exact_h2(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    text = skill.read_text(encoding="utf-8").replace("## Route First", "### Route First", 1)
    skill.write_text(text, encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="missing exact heading: ## Route First"):
        validate_skill.validate_skill(skill_dir)


def test_contract_heading_must_be_exact_h2(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    text = skill.read_text(encoding="utf-8").replace("## Contract", "### Contract", 1)
    skill.write_text(text, encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="missing exact heading: ## Contract"):
        validate_skill.validate_skill(skill_dir)


def test_router_must_be_first_h2(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    text = skill.read_text(encoding="utf-8").replace("## Route First", "## Prelude\n\n## Route First", 1)
    skill.write_text(text, encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="router must be the first H2"):
        validate_skill.validate_skill(skill_dir)


def test_contract_must_immediately_follow_router(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    text = skill.read_text(encoding="utf-8").replace("## Contract", "## Interlude\n\n## Contract", 1)
    skill.write_text(text, encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="contract must immediately follow"):
        validate_skill.validate_skill(skill_dir)


def test_router_must_forbid_bulk_loading(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    text = skill.read_text(encoding="utf-8").replace("Do not read every reference", "Avoid bulk loading", 1)
    skill.write_text(text, encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="must forbid bulk reference loading"):
        validate_skill.validate_skill(skill_dir)


def test_explicit_recursive_reference_with_anchor_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    module = skill_dir / "references" / "gpu-architecture.md"
    module.write_text(
        module.read_text(encoding="utf-8") + "\nRead references/service-throughput.md#contract.\n",
        encoding="utf-8",
    )

    with pytest.raises(validate_skill.ValidationError, match="gpu-architecture.md links recursively"):
        validate_skill.validate_skill(skill_dir)


def test_markdown_recursive_reference_with_anchor_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    module = skill_dir / "references" / "gpu-architecture.md"
    module.write_text(
        module.read_text(encoding="utf-8") + "\nRead [service](service-throughput.md#contract).\n",
        encoding="utf-8",
    )

    with pytest.raises(validate_skill.ValidationError, match="gpu-architecture.md links recursively"):
        validate_skill.validate_skill(skill_dir)


def test_backticked_actual_module_name_is_recursive(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    module = skill_dir / "references" / "gpu-architecture.md"
    module.write_text(
        module.read_text(encoding="utf-8") + "\nRead `service-throughput.md`.\n",
        encoding="utf-8",
    )

    with pytest.raises(validate_skill.ValidationError, match="gpu-architecture.md links recursively"):
        validate_skill.validate_skill(skill_dir)


def test_plain_actual_module_name_is_recursive(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    module = skill_dir / "references" / "gpu-architecture.md"
    module.write_text(
        module.read_text(encoding="utf-8") + "\nRead service-throughput.md before continuing.\n",
        encoding="utf-8",
    )

    with pytest.raises(validate_skill.ValidationError, match="gpu-architecture.md links recursively"):
        validate_skill.validate_skill(skill_dir)


def test_relative_reference_traversal_back_into_modules_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    module = skill_dir / "references" / "gpu-architecture.md"
    module.write_text(
        module.read_text(encoding="utf-8")
        + "\nRead [service](../references/service-throughput.md#contract).\n",
        encoding="utf-8",
    )

    with pytest.raises(validate_skill.ValidationError, match="gpu-architecture.md links recursively"):
        validate_skill.validate_skill(skill_dir)


def test_harmless_md_prose_is_allowed(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    module = skill_dir / "references" / "gpu-architecture.md"
    module.write_text(
        module.read_text(encoding="utf-8") + "\nKeep compact notes in `notes.md` only when requested.\n",
        encoding="utf-8",
    )

    validate_skill.validate_skill(skill_dir)


def test_external_url_ending_in_module_name_is_allowed(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    module = skill_dir / "references" / "gpu-architecture.md"
    module.write_text(
        module.read_text(encoding="utf-8")
        + "\nBackground: https://example.com/docs/service-throughput.md\n",
        encoding="utf-8",
    )

    validate_skill.validate_skill(skill_dir)


def test_unrouted_reference_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    (skill_dir / "references" / "orphan.md").write_text("# Orphan\n", encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="unrouted reference modules: orphan.md"):
        validate_skill.validate_skill(skill_dir)


def test_non_ascii_reference_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    ref = skill_dir / "references" / "evidence-loop.md"
    ref.write_text(ref.read_text(encoding="utf-8") + "\nCafe e\N{COMBINING ACUTE ACCENT}\n", encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="references/evidence-loop.md has non-ASCII"):
        validate_skill.validate_skill(skill_dir)


def test_invalid_utf8_fails_without_traceback(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    (skill_dir / "references" / "evidence-loop.md").write_bytes(b"\xff")

    with pytest.raises(validate_skill.ValidationError, match="references/evidence-loop.md is not valid UTF-8"):
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


def test_skill_frontmatter_rejects_extra_keys(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    skill = skill_dir / "SKILL.md"
    text = skill.read_text(encoding="utf-8").replace("description:", "version: 1\ndescription:", 1)
    skill.write_text(text, encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="must contain only name and description"):
        validate_skill.validate_skill(skill_dir)


def test_invalid_openai_yaml_fails(tmp_path: Path) -> None:
    skill_dir = copy_skill(tmp_path)
    (skill_dir / "agents" / "openai.yaml").write_text("interface: [unterminated\n", encoding="utf-8")

    with pytest.raises(validate_skill.ValidationError, match="agents/openai.yaml is invalid YAML"):
        validate_skill.validate_skill(skill_dir)


def test_split_modules_keep_common_loads_narrow() -> None:
    evidence = reference_text("evidence-loop.md")
    resources = reference_text("resource-models.md")

    assert "## Variance Handling" not in evidence
    assert "see Variance Handling" not in evidence
    assert "load the `variance` add-on through the router" in evidence
    assert "## Promotion Gates" not in evidence
    assert "## Forbidden Shortcut Screen" not in evidence
    assert "## Breakthrough Mining" not in evidence
    assert "## Plateau Rules" not in resources
    assert "## Sweep Contract" in reference_text("variance-and-sweeps.md")
    assert "## Breakthrough Mining" in reference_text("technique-intake.md")
    assert "## Reassess Before Closing" in reference_text("plateau-escape.md")


def test_sweep_and_plateau_modules_share_epoch_reset_rule() -> None:
    variance = reference_text("variance-and-sweeps.md")
    plateau = reference_text("plateau-escape.md")

    assert "meaningful authoritative promotion or a genuine hill change" in variance
    assert "meaningful authoritative promotion or a genuine hill change" in SKILL_TEXT
    assert "A genuine hill change resets the search epoch" in plateau
    assert "promotion drought" not in plateau


def test_search_escape_modules_stay_lean_and_scope_local_search() -> None:
    plateau = reference_text("plateau-escape.md")
    portfolio = reference_text("multi-agent-portfolio.md")

    assert len(plateau.split()) <= validate_skill.SPECIAL_REFERENCE_WORD_LIMITS["plateau-escape.md"]
    assert len(portfolio.split()) <= validate_skill.SPECIAL_REFERENCE_WORD_LIMITS["multi-agent-portfolio.md"]
    for phrase in (
        "Pick A Distinct Family Or Scale",
        "broad discovery may start immediately",
        "may predeclare one budgeted larger-radius probe",
        "stays in the same family",
        "resets neither the miss streak nor epoch",
        "contract-valid specialization",
        "external method intake",
        "negative proof",
        "every survivor needs full correctness and authoritative measurement",
    ):
        assert phrase in plateau
    assert "Scope before floors:" not in plateau
    assert "Structure before local tuning:" not in plateau
    assert "Random search is a finisher, not an architect" not in plateau


def test_gpu_modules_preserve_named_baselines() -> None:
    assert all(name in reference_text("kernel-matrix.md") for name in ("cuBLASLt", "cuBLAS", "CUTLASS", "Triton"))
    assert "CUB" in reference_text("kernel-reductions-scans.md")
    assert "float4" in reference_text("kernel-elementwise.md")
    assert "exact FP32" in reference_text("kernel-matrix.md")
    assert "residual TF32/BF16" in reference_text("kernel-matrix.md")


def test_frontier_reference_preserves_integrated_search_doctrine() -> None:
    text = reference_text("frontier-introspection.md")
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


def test_skill_defaults_to_no_logging_and_defines_scorebench_activation() -> None:
    required = (
        "Default behavior is no logging subsystem.",
        "Normal benchmark output, profiler captures, submitted artifacts",
        "Scorebench is active when the user invokes it",
        "Derive attempts, budget use, promotions, and best state there",
        "Do not mirror PAO logs, dashboards, or token accounting",
        "A logger failure must not block optimization",
    )
    for phrase in required:
        assert phrase in SKILL_TEXT


def test_multi_agent_coordinator_contract_is_lean() -> None:
    portfolio = reference_text("multi-agent-portfolio.md")

    assert "load the `portfolio` add-on" in SKILL_TEXT
    assert "Multi-agent mode with parallel mechanism families" in SKILL_TEXT
    assert "independently or adversarially review high-risk claims" in portfolio
    assert "Parallelism Must Buy Overlap" in portfolio
    assert "Delegate Experiments, Not Narration" in portfolio
    assert "Serialize Promotion, Not Exploration" in portfolio
    assert "If coordination costs more than candidate work, collapse to solo." in portfolio
    assert "Fix the shared contract and protected parent" in portfolio
    assert "Before the first concrete return, share validated facts" in portfolio
    assert "equivalent in strength to the original target" in portfolio
    assert "new fact required to reopen it" in portfolio
    assert "invalidates stale parents" in portfolio
    assert "Serialize promotion" in portfolio
    assert "Status-only reports earn no follow-up budget." in portfolio
    assert "full-checks only plausible survivors" in portfolio
    assert "claimed proof or counterexample" in portfolio
    assert "candidate or information yield" in portfolio
    assert "Cross-pollinate only after evidence." in portfolio
    assert "do not mirror them locally" in portfolio
    assert portfolio.count("```text") == 1


def test_readme_keeps_router_and_observability_boundaries_clear() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "Scorebench exclusively owns" in text
    assert "5,000 measured configurations consumes 5,000 attempts" in text
    assert "## Route First" in text
    assert "scored-artifact semantics" in text
    assert "variance-and-sweeps.md" in text
    assert "plateau-escape.md" in text
    assert "multi-agent-portfolio.md" in text
    assert "both at least three measured attempts and 10% of the contract budget" in text
    assert "Screen rejections, bugs, blockers" in text
    assert "Whether the next candidate must be off-hill" not in text
    assert "Progress chart: on" not in text
    assert "scripts/init_harness.py" not in text
