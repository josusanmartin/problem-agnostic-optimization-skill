# Local Harness API

Use the local PAO harness API when a challenge or benchmark has operational work that would slow the optimizer: login, submit, poll, parse, retry, rate limits, raw logs, progress rows, best tracking, or sidecar refresh. The protocol is generic. Challenge-specific behavior belongs in adapters.

The agent should call the local API and continue optimizing from the normalized result:

```text
generate candidate -> POST /evaluate -> read result -> decide next candidate
```

The API answers what happened during evaluation. It must not become a second optimizer or propose the next candidate.

## Version

All v1 responses include:

```json
{
  "api_version": "pao-harness.v1"
}
```

Clients should rely only on `pao-harness.v1` fields.

## Discovery

`pao_harness_server.py` writes:

```text
work/optimization_harness/server.json
```

Example:

```json
{
  "api_version": "pao-harness.v1",
  "base_url": "http://127.0.0.1:8765",
  "adapter": "adapters.local_command:Adapter",
  "mode": "fast",
  "work_dir": "work/optimization_harness",
  "started_at": "2026-06-10T00:00:00Z"
}
```

Use the client wrapper instead of hand-writing HTTP when possible:

```bash
PAO="${CODEX_HOME:-$HOME/.codex}/skills/problem-agnostic-optimization"
python "$PAO/scripts/pao_harness_client.py" health
python "$PAO/scripts/pao_harness_client.py" contract
python "$PAO/scripts/pao_harness_client.py" evaluate \
  --candidate cand_0042 \
  --artifact submissions/cand_0042.py \
  --parent cand_0037 \
  --label "remove redundant normalization pass" \
  --mechanism "work deletion"
```

## Start Server

Use JSON config to avoid extra dependencies:

```json
{
  "api_version": "pao-harness.v1",
  "server": {
    "host": "127.0.0.1",
    "port": 8765
  },
  "project_root": ".",
  "work_dir": "work/optimization_harness",
  "mode": "fast",
  "metric": {
    "name": "score",
    "direction": "lower"
  },
  "adapter": {
    "import": "adapters.local_command:Adapter",
    "config": {
      "command": "python benchmark.py {artifact_path}",
      "metric_regex": "score:\\s*([0-9.]+)",
      "correct_regex": "correct:\\s*true"
    }
  },
  "rate_limit": {
    "min_seconds_between_evaluations": 2
  },
  "sidecar": {
    "refresh_policy": "checkpoint_only",
    "every_n_candidates": 25
  }
}
```

Start from the target project root:

```bash
PAO="${CODEX_HOME:-$HOME/.codex}/skills/problem-agnostic-optimization"
python "$PAO/scripts/pao_harness_server.py" --config pao_harness.json
```

The server binds to `127.0.0.1`.

## Endpoints

### GET /health

Response:

```json
{
  "ok": true,
  "api_version": "pao-harness.v1",
  "adapter": "adapters.local_command:Adapter",
  "mode": "fast"
}
```

### GET /contract

Response:

```json
{
  "api_version": "pao-harness.v1",
  "objective": "minimize score",
  "metric_name": "score",
  "direction": "lower",
  "mode": "fast",
  "artifact_type": "file",
  "supports_async": false,
  "rate_limit": {
    "min_seconds_between_evaluations": 2
  },
  "work_dir": "work/optimization_harness"
}
```

### POST /evaluate

Request:

```json
{
  "candidate_id": "cand_0042",
  "artifact_path": "submissions/cand_0042.py",
  "parent": "cand_0037",
  "label": "remove redundant normalization pass",
  "mechanism": "work deletion"
}
```

Measured response:

```json
{
  "ok": true,
  "api_version": "pao-harness.v1",
  "candidate_id": "cand_0042",
  "status": "measured",
  "correct": true,
  "metric_name": "score",
  "score": 5281,
  "direction": "lower",
  "decision_hint": "promote",
  "best_score": 5281,
  "best_candidate": "cand_0042",
  "progress_written": true,
  "raw_log_path": "work/optimization_harness/raw_logs/cand_0042.json",
  "message": "accepted"
}
```

Error candidate response:

```json
{
  "ok": false,
  "api_version": "pao-harness.v1",
  "candidate_id": "cand_0043",
  "status": "compile_error",
  "correct": false,
  "metric_name": "score",
  "score": null,
  "direction": "lower",
  "decision_hint": "bug",
  "best_score": 5281,
  "best_candidate": "cand_0042",
  "progress_written": true,
  "raw_log_path": "work/optimization_harness/raw_logs/cand_0043.json",
  "message": "compiler error: undefined symbol foo"
}
```

### GET /best

Response:

```json
{
  "ok": true,
  "best_candidate": "cand_0042",
  "best_score": 5281,
  "metric_name": "score",
  "direction": "lower",
  "artifact_path": "submissions/cand_0042.py"
}
```

### POST /refresh

Request:

```json
{
  "artifacts": ["dashboard", "chart", "review"]
}
```

Response:

```json
{
  "ok": true,
  "api_version": "pao-harness.v1",
  "refreshed": [
    "work/optimization_harness/progress.svg",
    "work/optimization_harness/dashboard.html"
  ]
}
```

## Status

Normalized statuses:

- `measured`
- `wrong_answer`
- `compile_error`
- `runtime_error`
- `timeout`
- `rate_limited`
- `submission_error`
- `blocked`
- `internal_error`

## Decision Hint

Decision hints are simple score/status hints. The agent still owns strategy.

- `promote`
- `keep`
- `reject`
- `bug`
- `blocked`
- `unknown`

Good API behavior: `score improved; decision_hint = promote`.

Bad API behavior: `try loop unrolling next`.

## Modes

- `fast`: default for active search. Evaluate, write one progress row, update best, save raw result, return response. No dashboard refresh per candidate.
- `standard`: use fast path per candidate and refresh sidecar artifacts only at configured checkpoints or explicit `/refresh`.
- `audit`: write richer candidate result artifacts before important decisions. Do not force audit work for every candidate unless configured.

## Security

- Bind to `127.0.0.1`.
- Reject `artifact_path` values outside `project_root`.
- Read secrets from environment variables, not committed config.
- Do not write tokens or cookies to `progress.tsv`.
- Redact configured secret strings from raw logs.
- Keep raw logs under the isolated harness directory.

## Agent Boundary

If `work/optimization_harness/server.json` exists or the `/goal` provides a PAO harness API, use it as the canonical evaluation path. Do not bypass it for direct challenge calls unless the API is broken or the user asks.
