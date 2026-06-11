# Adapter Interface

Adapters connect the generic PAO harness API to a specific evaluator. The protocol is generic; adapters are specific. Keep login, submit, poll, parser, retry, rate-limit, and platform quirks out of the skill core.

The built-in interface lives under:

```text
scripts/adapters/base.py
```

## Interface

```python
from __future__ import annotations

from typing import Any, Protocol


class ChallengeAdapter(Protocol):
    def contract(self) -> dict[str, Any]:
        """Return metric, direction, artifact expectations, and limits."""
        ...

    def evaluate(self, request: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a candidate and return a normalized result without progress writing."""
        ...
```

The adapter constructor receives the `adapter.config` object from `pao_harness.json`.

```python
class Adapter:
    def __init__(self, config: dict):
        self.config = config
```

## Contract

Return the fields the agent needs before evaluating candidates:

```json
{
  "metric_name": "score",
  "direction": "lower",
  "artifact_type": "file",
  "supports_async": false
}
```

Use `direction: "lower"` for latency, cycles, loss, or cost. Use `direction: "higher"` for accuracy, reward, or leaderboard points.

## Evaluate Request

The generic server validates paths before calling the adapter and passes a normalized request:

```json
{
  "candidate_id": "cand_0042",
  "artifact_path": "submissions/cand_0042.py",
  "artifact_path_abs": "/project/submissions/cand_0042.py",
  "project_root": "/project",
  "parent": "cand_0037",
  "label": "remove redundant normalization pass",
  "mechanism": "work deletion"
}
```

Adapters may ignore unknown fields. They should not write progress rows, best state, dashboards, candidate JSON, or sidecar artifacts.

## Evaluate Result

Return a normalized result without server-added fields:

```json
{
  "ok": true,
  "status": "measured",
  "correct": true,
  "metric_name": "score",
  "score": 5281,
  "direction": "lower",
  "message": "accepted",
  "raw": {
    "challenge_submission_id": "abc123"
  }
}
```

The generic server adds:

- `api_version`
- `candidate_id`
- `best_score`
- `best_candidate`
- `progress_written`
- `raw_log_path`
- `decision_hint`

## Adapter Responsibilities

Specific adapters own:

- login and session setup
- artifact submission
- result polling
- result parsing
- platform error mapping
- challenge-specific retries
- challenge-specific rate-limit quirks
- raw challenge identifiers in `raw`

The generic server owns:

- endpoint schema
- request validation
- safe artifact path checks
- progress row writing
- raw log writing
- best tracking
- sidecar refresh policy
- normalized API responses

## Status Mapping

Use these statuses:

- `measured`: correct result with a numeric score
- `wrong_answer`: evaluator rejected correctness
- `compile_error`: build, import, or syntax failure
- `runtime_error`: candidate crashed while running
- `timeout`: evaluation exceeded the configured timeout
- `rate_limited`: platform rejected the request for rate or quota
- `submission_error`: submission or parsing failed without a better category
- `blocked`: external precondition is missing
- `internal_error`: adapter bug or unexpected failure

Set `correct` to `false` for every status except a valid measured result. `ok` should be true only when the candidate is measured and correct.

## Local Command Adapter

The built-in local adapter is useful for end-to-end tests and simple local benchmarks:

```json
{
  "adapter": {
    "import": "adapters.local_command:Adapter",
    "config": {
      "command": "python benchmark.py {artifact_path}",
      "metric_regex": "score:\\s*([0-9.]+)",
      "correct_regex": "correct:\\s*true",
      "timeout_seconds": 30
    }
  },
  "metric": {
    "name": "score",
    "direction": "lower"
  }
}
```

Available format fields:

- `{artifact_path}`: validated path relative to `project_root`
- `{artifact_path_abs}`: absolute validated path
- `{candidate_id}`: candidate id

The built-in adapter shell-quotes request-derived placeholder values before formatting the command string. Keep command templates under repo/config control; do not construct templates from candidate content.

## External Adapter Repos

Challenge adapters should live in a separate package, for example:

```text
problem-agnostic-optimization-adapters/
  src/pao_adapters/
    highload.py
    vliw.py
  configs/
  tests/
  docs/
```

Install locally with:

```bash
python -m pip install -e ../problem-agnostic-optimization-adapters
```

Then point config at the adapter:

```json
{
  "adapter": {
    "import": "pao_adapters.highload:Adapter",
    "config": {
      "token_env": "HIGHLOAD_TOKEN"
    }
  }
}
```

Do not commit real secrets. Parser tests should use fixtures and mocked HTTP/session behavior, not live platforms.
