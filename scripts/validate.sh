#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skill_dir="$repo_root/skills/problem-agnostic-optimization"
validator="$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py"

if [[ -f "$validator" ]]; then
  python3 "$validator" "$skill_dir"
else
  python3 - "$skill_dir" <<'PY'
from pathlib import Path
import sys

skill_dir = Path(sys.argv[1])
skill = skill_dir / "SKILL.md"
if not skill.exists():
    raise SystemExit("missing SKILL.md")

text = skill.read_text()
if not text.startswith("---\n"):
    raise SystemExit("SKILL.md missing YAML frontmatter")
if "\nname:" not in text and "\nname: " not in text:
    raise SystemExit("SKILL.md frontmatter missing name")
if "\ndescription:" not in text and "\ndescription: " not in text:
    raise SystemExit("SKILL.md frontmatter missing description")
print("Basic skill validation passed")
PY
fi

python3 - "$skill_dir" <<'PY'
from pathlib import Path
import sys

skill_dir = Path(sys.argv[1])
paths = [skill_dir / "SKILL.md", skill_dir / "agents" / "openai.yaml"]
paths.extend(sorted((skill_dir / "references").glob("*.md")))

for path in paths:
    text = path.read_text()
    bad = sorted(set(ch for ch in text if ord(ch) > 127))
    if bad:
        chars = "".join(bad)
        raise SystemExit(f"{path.relative_to(skill_dir)} has non-ASCII characters: {chars!r}")
    print(f"{path.relative_to(skill_dir)}: ASCII clean")
PY
