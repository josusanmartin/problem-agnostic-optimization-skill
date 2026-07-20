#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import posixpath
import re
import sys
from typing import Any, NamedTuple

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised by users without deps.
    yaml = None


ROUTE_HEADING = "## Route First"
CONTRACT_HEADING = "## Contract"
ROUTER_TABLES = {
    "### Primary Route": frozenset({"policy", "service", "fixed-resource", "gpu", "cpu", "other"}),
    "### GPU Kernel Shape": frozenset(
        {
            "elementwise",
            "reduction-scan",
            "stencil-convolution",
            "matrix",
            "histogram",
            "quantized",
            "attention-moe",
        }
    ),
    "### Evidence-Triggered Add-ons": frozenset(
        {"measurement", "variance", "technique", "resource", "plateau", "frontier", "runtime"}
    ),
}
ROUTER_IDS_WITHOUT_MODULE = frozenset({"other"})
ROUTED_REFERENCE_RE = re.compile(r"`(references/[^`\n]+\.md(?:#[^`\n]+)?)`")
ROUTE_ID_RE = re.compile(r"`([a-z0-9-]+)`")
VALID_REFERENCE_PATH_RE = re.compile(r"(?:[a-z0-9][a-z0-9._-]*/)*[a-z0-9][a-z0-9._-]*\.md")
EXPLICIT_REFERENCE_RE = re.compile(
    r"(?<![A-Za-z0-9_:/.-])references/[A-Za-z0-9_./-]+\.md(?:#[A-Za-z0-9_.-]+)?"
)
MARKDOWN_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+\.md(?:#[^)]*)?)\)")
CODE_MD_RE = re.compile(r"`([^`\n\s]+\.md(?:#[^`\n\s]+)?)`")
BARE_MD_RE = re.compile(
    r"(?<![A-Za-z0-9_./:-])((?:[a-z0-9][a-z0-9._-]*/)*[a-z0-9][a-z0-9._-]*\.md(?:#[A-Za-z0-9_.-]+)?)"
)
MAX_SKILL_WORDS = 1500
MAX_REFERENCE_WORDS = 2200
MAX_SHAPE_WORDS = 450


class ValidationError(Exception):
    pass


class RouterRow(NamedTuple):
    section: str
    route_id: str
    reference: str | None
    line: str


def fail(message: str) -> None:
    raise ValidationError(message)


def require_yaml() -> Any:
    if yaml is None:
        fail("PyYAML is required; install with `python3 -m pip install pyyaml`")
    return yaml


def display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def read_ascii(path: Path, root: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {display_path(path, root)}")
    if not path.is_file():
        fail(f"required path is not a file: {display_path(path, root)}")

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        fail(f"{display_path(path, root)} is not valid UTF-8: {exc}")
    bad = sorted(set(ch for ch in text if ord(ch) > 127))
    if bad:
        chars = "".join(bad)
        fail(f"{display_path(path, root)} has non-ASCII characters: {chars!r}")
    return text


def parse_skill_frontmatter(text: str) -> dict[str, Any]:
    parser = require_yaml()
    if not text.startswith("---\n"):
        fail("SKILL.md missing YAML frontmatter")

    try:
        _start, frontmatter, _body = text.split("---\n", 2)
    except ValueError:
        fail("SKILL.md frontmatter is malformed")

    try:
        data = parser.safe_load(frontmatter) or {}
    except Exception as exc:
        fail(f"SKILL.md frontmatter is invalid YAML: {exc}")
    if not isinstance(data, dict):
        fail("SKILL.md frontmatter must be a mapping")
    if set(data) != {"name", "description"}:
        fail("SKILL.md frontmatter must contain only name and description")
    for key in ("name", "description"):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            fail(f"SKILL.md frontmatter missing required key: {key}")
    return data


def parse_openai_yaml(text: str) -> dict[str, Any]:
    parser = require_yaml()
    try:
        data = parser.safe_load(text) or {}
    except Exception as exc:
        fail(f"agents/openai.yaml is invalid YAML: {exc}")
    if not isinstance(data, dict):
        fail("agents/openai.yaml must be a mapping")

    interface = data.get("interface")
    if not isinstance(interface, dict):
        fail("agents/openai.yaml missing interface mapping")
    for key in ("display_name", "short_description", "default_prompt"):
        value = interface.get(key)
        if not isinstance(value, str) or not value.strip():
            fail(f"agents/openai.yaml missing interface.{key}")
    return data


def one_exact_heading(lines: list[str], heading: str) -> int:
    positions = [index for index, line in enumerate(lines) if line == heading]
    if not positions:
        fail(f"SKILL.md missing exact heading: {heading}")
    if len(positions) > 1:
        fail(f"SKILL.md duplicates exact heading: {heading}")
    return positions[0]


def parse_reference_path(token: str) -> str:
    if "#" in token:
        fail(f"router reference must load a whole module, not an anchor: {token}")
    if not token.startswith("references/"):
        fail(f"invalid router reference: {token}")

    relative = token.removeprefix("references/")
    pure = PurePosixPath(relative)
    if (
        not relative
        or relative.startswith("/")
        or "\\" in relative
        or any(part in {"", ".", ".."} for part in pure.parts)
        or not VALID_REFERENCE_PATH_RE.fullmatch(relative)
    ):
        fail(f"invalid router reference path: {token}")
    return pure.as_posix()


def table_cells(line: str) -> list[str]:
    if not line.startswith("|") or not line.endswith("|"):
        return []
    return [cell.strip() for cell in line[1:-1].split("|")]


def parse_router_rows(skill_text: str) -> list[RouterRow]:
    lines = skill_text.splitlines()
    route_index = one_exact_heading(lines, ROUTE_HEADING)
    contract_index = one_exact_heading(lines, CONTRACT_HEADING)
    h2_positions = [index for index, line in enumerate(lines) if line.startswith("## ")]

    if not h2_positions or h2_positions[0] != route_index:
        fail("SKILL.md router must be the first H2 section")
    if route_index > contract_index:
        fail("SKILL.md router must precede the optimization contract")
    if len(h2_positions) < 2 or h2_positions[1] != contract_index:
        fail("SKILL.md contract must immediately follow the router section")

    router_lines = lines[route_index:contract_index]
    if not any("Do not read every reference" in line for line in router_lines):
        fail("SKILL.md router must forbid bulk reference loading")

    subsection_positions: dict[str, int] = {}
    for heading in ROUTER_TABLES:
        positions = [index for index, line in enumerate(router_lines) if line == heading]
        if len(positions) != 1:
            fail(f"router must contain exactly one {heading} section")
        subsection_positions[heading] = positions[0]

    ordered_headings = list(ROUTER_TABLES)
    if [subsection_positions[heading] for heading in ordered_headings] != sorted(subsection_positions.values()):
        fail("router subsections are out of order")

    rows: list[RouterRow] = []
    for section_index, heading in enumerate(ordered_headings):
        start = subsection_positions[heading] + 1
        end = (
            subsection_positions[ordered_headings[section_index + 1]]
            if section_index + 1 < len(ordered_headings)
            else len(router_lines)
        )
        table_lines = [line for line in router_lines[start:end] if line.startswith("|")]
        if len(table_lines) < 3:
            fail(f"router section {heading} is missing a Markdown table")

        data_lines = table_lines[2:]
        seen_ids: set[str] = set()
        for line in data_lines:
            cells = table_cells(line)
            if len(cells) < 3:
                fail(f"malformed router row in {heading}: {line}")
            id_match = ROUTE_ID_RE.fullmatch(cells[0])
            if id_match is None:
                fail(f"router row in {heading} needs a backticked id: {line}")
            route_id = id_match.group(1)
            if route_id in seen_ids:
                fail(f"duplicate router id in {heading}: {route_id}")
            seen_ids.add(route_id)

            tokens = ROUTED_REFERENCE_RE.findall(line)
            if route_id in ROUTER_IDS_WITHOUT_MODULE:
                if tokens:
                    fail(f"router id {route_id} must not load a module")
                reference = None
            else:
                if len(tokens) != 1:
                    fail(f"router id {route_id} must load exactly one module")
                reference = parse_reference_path(tokens[0])
            rows.append(RouterRow(heading, route_id, reference, line))

        required_ids = ROUTER_TABLES[heading]
        missing_ids = sorted(required_ids - seen_ids)
        unknown_ids = sorted(seen_ids - required_ids)
        if missing_ids:
            fail(f"router section {heading} missing ids: {', '.join(missing_ids)}")
        if unknown_ids:
            fail(f"router section {heading} has unknown ids: {', '.join(unknown_ids)}")

    references = [row.reference for row in rows if row.reference is not None]
    duplicates = sorted(reference for reference in set(references) if references.count(reference) > 1)
    if duplicates:
        fail(f"reference modules routed more than once: {', '.join(duplicates)}")
    return rows


def actual_reference_paths(reference_dir: Path) -> list[str]:
    if not reference_dir.exists() or not reference_dir.is_dir():
        fail("missing required directory: references")
    return sorted(path.relative_to(reference_dir).as_posix() for path in reference_dir.rglob("*.md") if path.is_file())


def normalize_module_target(target: str, module_name: str) -> str | None:
    raw = target.strip("<>").split("#", 1)[0]
    if not raw or "://" in raw or raw.startswith("/"):
        return None
    if raw.startswith("references/"):
        virtual = posixpath.normpath(raw)
    else:
        module_dir = posixpath.dirname(posixpath.join("references", module_name))
        virtual = posixpath.normpath(posixpath.join(module_dir, raw))
    if not virtual.startswith("references/"):
        return None
    return virtual.removeprefix("references/")


def recursive_reference_targets(text: str, module_name: str, actual: set[str]) -> list[str]:
    targets: set[str] = set(EXPLICIT_REFERENCE_RE.findall(text))
    candidates = MARKDOWN_MD_LINK_RE.findall(text) + CODE_MD_RE.findall(text) + BARE_MD_RE.findall(text)
    for candidate in candidates:
        normalized = normalize_module_target(candidate, module_name)
        if candidate.startswith("references/") or (normalized is not None and normalized in actual):
            targets.add(candidate)
    return sorted(targets)


def validate_size_budgets(skill_text: str, module_texts: dict[str, str], rows: list[RouterRow]) -> None:
    skill_words = len(skill_text.split())
    if skill_words > MAX_SKILL_WORDS:
        fail(f"SKILL.md exceeds {MAX_SKILL_WORDS} words: {skill_words}")

    shape_modules = {
        row.reference
        for row in rows
        if row.section == "### GPU Kernel Shape" and row.reference is not None
    }
    for name, text in module_texts.items():
        words = len(text.split())
        limit = MAX_SHAPE_WORDS if name in shape_modules else MAX_REFERENCE_WORDS
        if words > limit:
            fail(f"references/{name} exceeds {limit} words: {words}")


def validate_skill(skill_dir: Path) -> None:
    skill_dir = skill_dir.resolve()
    if not skill_dir.exists():
        fail(f"skill directory does not exist: {skill_dir}")
    if not skill_dir.is_dir():
        fail(f"skill path is not a directory: {skill_dir}")

    skill_text = read_ascii(skill_dir / "SKILL.md", skill_dir)
    openai_text = read_ascii(skill_dir / "agents" / "openai.yaml", skill_dir)
    parse_skill_frontmatter(skill_text)
    parse_openai_yaml(openai_text)
    rows = parse_router_rows(skill_text)

    reference_dir = skill_dir / "references"
    actual = actual_reference_paths(reference_dir)
    routed = sorted(row.reference for row in rows if row.reference is not None)
    missing = sorted(set(routed) - set(actual))
    if missing:
        fail(f"missing routed reference modules: {', '.join(missing)}")
    unrouted = sorted(set(actual) - set(routed))
    if unrouted:
        fail(f"unrouted reference modules: {', '.join(unrouted)}")

    module_texts: dict[str, str] = {}
    for name in actual:
        module_text = read_ascii(reference_dir / name, skill_dir)
        module_texts[name] = module_text
        nested = recursive_reference_targets(module_text, name, set(actual))
        if nested:
            fail(f"reference module {name} links recursively: {', '.join(nested)}")

    validate_size_budgets(skill_text, module_texts, rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the problem-agnostic optimization skill.")
    parser.add_argument("skill_dir", type=Path, help="Path to skills/problem-agnostic-optimization")
    args = parser.parse_args(argv)

    try:
        validate_skill(args.skill_dir)
    except ValidationError as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1

    print("Skill validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
