#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skill_dir="$repo_root/skills/problem-agnostic-optimization"

python3 "$repo_root/scripts/validate_skill.py" "$skill_dir"
