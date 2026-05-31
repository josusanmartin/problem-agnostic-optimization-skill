#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised by users without deps.
    yaml = None


REQUIRED_REFERENCES = [
    "cpu-architecture.md",
    "evidence-loop.md",
    "gpu-architecture.md",
    "harness.md",
    "problem-families.md",
    "resource-models.md",
    "stochastic-policy-search.md",
    "templates.md",
]

REQUIRED_SKILL_SCRIPTS = [
    "progress_chart.py",
    "record_event.py",
]


class ValidationError(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def require_yaml() -> Any:
    if yaml is None:
        fail("PyYAML is required; install with `python3 -m pip install pyyaml`")
    return yaml


def read_ascii(path: Path, root: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(root)}")
    if not path.is_file():
        fail(f"required path is not a file: {path.relative_to(root)}")

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        fail(f"{path.relative_to(root)} is not valid UTF-8: {exc}")
    bad = sorted(set(ch for ch in text if ord(ch) > 127))
    if bad:
        chars = "".join(bad)
        fail(f"{path.relative_to(root)} has non-ASCII characters: {chars!r}")
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


def required_files(skill_dir: Path) -> list[Path]:
    files = [
        skill_dir / "SKILL.md",
        skill_dir / "agents" / "openai.yaml",
    ]
    files.extend(skill_dir / "references" / name for name in REQUIRED_REFERENCES)
    files.extend(skill_dir / "scripts" / name for name in REQUIRED_SKILL_SCRIPTS)
    return files


def validate_skill(skill_dir: Path) -> None:
    skill_dir = skill_dir.resolve()
    if not skill_dir.exists():
        fail(f"skill directory does not exist: {skill_dir}")
    if not skill_dir.is_dir():
        fail(f"skill path is not a directory: {skill_dir}")

    files = required_files(skill_dir)
    contents = {path: read_ascii(path, skill_dir) for path in files}

    parse_skill_frontmatter(contents[skill_dir / "SKILL.md"])
    parse_openai_yaml(contents[skill_dir / "agents" / "openai.yaml"])


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
