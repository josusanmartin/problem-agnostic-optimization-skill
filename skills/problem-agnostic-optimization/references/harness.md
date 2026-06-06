# Optimization Harness

Use this reference when an optimization run may span multiple turns, many candidates, noisy measurements, remote jobs, or rate limits. The harness is a persistent contract:

```text
Preserve the best, test one hypothesis at a time, log every result, and reject exploit-like shortcuts outright.
```

## Fast Bootstrap

For any substantial `/goal` run, deploy the harness before baseline or candidate work. Use the bundled initializer when it is available:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
python "$CODEX_HOME/skills/problem-agnostic-optimization/scripts/init_harness.py" \
  --objective "<objective>" \
  --metric "<authoritative metric>" \
  --baseline "<baseline or unknown, reproduce first>" \
  --budget "<budget / stopping rule>" \
  --validation "<validation command or protocol>"
```

Run this from the target repository root so it creates the local `work/` directory for that optimization run. Add `--progress-chart off` only when the contract says `Progress chart: off`. Add `--fresh-run-isolation off` only when the user has allowed prior-run transfer. Add `--multi-agent-mode on` only when the `/goal` says `Multi-agent mode: on` or the user explicitly asks for parallel workers.

If the initializer is unavailable, create the same files manually before candidate work. Do not wait until after the first result to create the ledger.

## Minimal Harness

For small projects, create only:

```text
work/
  audit.md
  best.md
  breakthroughs.md            # frontier mechanisms, co-binders, calibrated screens
  checkpoints/
    progress.json              # phase/checkpoint state for resume
  candidates/
    _template.result.json      # typed candidate result template
  dashboard.html             # static dashboard for local or remote review
  events.jsonl               # optional compatibility event ledger
  log.md
  plan.md
  progress.tsv              # small-run table or derived export
  progress.svg
  promotion_ladder.md
  review.md
  schemas/
    candidate_result.schema.json
  state.json
  verifier.md
```

For longer projects, use:

```text
project/
  submission.*             # current submit-ready entrypoint, if required
  reference.*              # correctness reference, if available
  eval.*                   # local validation, if available
  candidates/
    cand_0001.*
    cand_0002.*
  work/
    audit.md
    best.md
    breakthroughs.md
    checkpoints/
      progress.json
    candidates/
      _template.result.json
      cand_0001.result.json
      cand_0001.md
    dashboard.html
    events.jsonl
    log.md
    plan.md
    progress.tsv
    progress.svg
    promotion_ladder.md
    state.json
    verifier.md
    schemas/
      candidate_result.schema.json
    profiles/
      baseline.profile.txt
      cand_0001.profile.txt
    results/
      cand_0001.json
    raw_logs/
      cand_0001.out
  scripts/
    validate.sh
    benchmark.sh
    submit.sh
    summarize.*
```

Adapt names to the repository. The important part is that best state, history, active plan, and machine-readable state survive chat compaction and process crashes.

## Typed Candidate Artifacts

For substantial or high-risk runs, every measured candidate should have a normalized JSON artifact under `work/candidates/`, even when the candidate is rejected. Use `work/candidates/_template.result.json` when the initializer created it.

Recommended normalized shape:

```json
{
  "schema_version": 1,
  "candidate": "cand_0007",
  "parent": "cand_0006",
  "parent_hash": "git-or-file-hash",
  "mode": "TUNE",
  "mechanism_class": "representation/primitive/route change",
  "duplicate_check": "why this is not the same hill or worker packet as an existing attempt",
  "hypothesis": "one concrete hypothesis",
  "artifact_paths": ["candidates/cand_0007.py"],
  "raw_log_paths": ["work/raw_logs/cand_0007.out"],
  "commands": {
    "apply_or_build": "...",
    "correctness": "...",
    "authoritative_metric": "...",
    "regression_or_adversarial": "...",
    "fresh_verifier": "..."
  },
  "correctness": "pass",
  "authoritative_metric": {
    "score": 2226,
    "unit": "cycles",
    "direction": "lower",
    "raw_result_path": "work/results/cand_0007.json"
  },
  "escape": {
    "status": "tracking",
    "stuck_signal": null,
    "closed_hill": null,
    "divergence_probe": null,
    "new_hill": null,
    "mechanism_signal": "",
    "commitment_budget": null,
    "kill_criterion": null
  },
  "promotion_ladder": {},
  "verifier": {},
  "decision": "REJECT",
  "learning": ""
}
```

Do not use the JSON artifact as a second score ledger. `work/progress.tsv` remains the compact score ledger; candidate JSON preserves the richer evidence, raw paths, verifier verdict, and promotion-ladder state.

## Breakthrough Ledger

Use `work/breakthroughs.md` for plateaued, high-stakes, public-leaderboard, or multi-agent runs. It is the durable frontier map: public breakthroughs, local breakthrough rows, phase owners, calibrated screens, validation islands, closed hills, new-hill commitments, and negative breakthroughs. Keep it compact; raw outputs still belong under `work/raw_logs/`, `work/results/`, or `work/profiles/`.

Minimum sections:

```text
Frontier Sources
Breakthrough Rows
Phase Owners / Co-Binders
Screen Calibration
Validation Islands / Selectors
Closed Hills / New-Hill Commitments
Negative Breakthroughs
```

Update it when any of these happen:

- A public result or local candidate changes a resource tier or active floor.
- A profile, trace, or phase label identifies the peak/tail owner.
- A cheap screen is created, calibrated, downgraded, or retired.
- A selector, seed, nonce, validation island, or route choice is used to land a candidate.
- A local-optimum audit closes or narrows a hill, opens a divergence burst, or commits a short budget to a new hill.
- A tempting route is ruled out by measured resource tradeoff.

Do not promote from `work/breakthroughs.md`; it explains search direction. Candidate JSON plus the promotion ladder still hold promotion evidence.

## Phase Checkpoints

Use `work/checkpoints/progress.json` to make long runs resumable. It tracks phase status, completed shards, terminal results, and the current phase. Resume should skip only completed terminal phases. Retry failed, blocked, or partial phases after checking their raw logs.

Recommended phases:

```text
contract -> baseline -> candidate -> validation -> measurement -> fresh_verifier -> promotion -> handoff
```

For parallel or sharded work, record completed worker/shard ids and their result paths. A shard is terminal only when it has a candidate JSON artifact or an explicit no-result record with evidence. Do not mark a phase complete because a chat message said it finished.

## Fresh Verifier Gate

Promotions should pass a fresh verifier gate whenever the result matters: leaderboard submissions, production changes, security-sensitive code, surprising speedups, exploit-boundary questions, remote/noisy measurements, or any candidate that changes stateful behavior.

Verifier contract:

- Start from a clean checkout, fresh container, reset process, or equivalent independent environment when possible.
- Transfer only the candidate artifact or diff, the recorded contract, validation command, and measurement command.
- Rerun correctness before the authoritative metric.
- Reproduce the authoritative metric with the same official command, submission path, or public result source.
- Record `PASS`, `FAIL`, `INCONCLUSIVE`, or `SKIPPED_WITH_LIMITATION` in the candidate JSON and summarize limitations in `work/log.md`.

If a true fresh environment is impossible, run the cleanest independent retest available and make the limitation visible. A candidate may be kept as `KEEP VARIANT`; it should not become the stable best unless the user accepts that limitation or the contract explicitly allows it.

## Promotion Ladder

Use `work/promotion_ladder.md` and the candidate JSON `promotion_ladder` object to separate gating evidence from advisory evidence.

Gating steps:

1. `apply_or_build`: patch applies, code builds, or the artifact loads.
2. `correctness`: required reference, shape, seed, or test checks pass.
3. `authoritative_metric`: official metric improves outside the recorded noise gate.
4. `regression_or_adversarial`: targeted regressions, hidden-risk cases, no-exploit audit, or overfit checks pass when applicable.
5. `fresh_verifier`: independent retest passes or the limitation is explicitly accepted by the contract.
6. `promote`: update stable best, state, ledgers, chart, and plan.

Advisory steps include profiles, counters, local screening, style, readability, or implementation neatness. Advisory evidence can explain or prioritize work; it cannot promote a candidate by itself.

## Execution Boundary

When executing untrusted/generated target code, attacker-controlled inputs, fuzzing harnesses, or external benchmark artifacts, use a constrained execution boundary when practical:

- clean environment
- no API keys, wallet keys, tokens, or unrelated credentials
- no access to unrelated host files
- restricted egress or no network when the task does not require it
- fresh process/container for verifier runs

Prompts and immutable-file rules are not a security boundary. If the environment cannot enforce the boundary, record the limitation in `work/state.json.execution_boundary.notes` and in the candidate JSON.

## Draft Patch Mode

For security-sensitive, production-sensitive, or user-requested review-first work, set `work/state.json.execution_boundary.draft_patch_only` to `true`. In draft patch mode, generate inert diffs or patch files under `work/PATCHES/` or `work/candidates/`; do not apply them to the live tree unless the user explicitly asks. Still validate the patch concept where possible in a separate sandbox or copied checkout.

## Progress Monitor

For substantial optimization runs, maintain a live progress surface by default. The score ledger is `work/progress.tsv`; token history comes from explicit `get_goal` snapshots in `work/log.md`, with the latest snapshot copied into `work/state.json`.

```text
work/log.md          # human log plus explicit get_goal token snapshots
work/dashboard.html  # static dashboard for review and handoff
work/progress.tsv   # one row per measured candidate
work/progress.svg   # chart regenerated after each result unless Progress chart: off
work/review.md      # short human review snapshot unless Progress chart: off
work/state.json      # current best and latest usage snapshot
```

Render the two-panel chart from `work/progress.tsv`:

```bash
python skills/problem-agnostic-optimization/scripts/progress_chart.py work/progress.tsv \
  -o work/progress.svg \
  --ylabel "Authoritative metric" \
  --direction lower

python skills/problem-agnostic-optimization/scripts/progress_chart.py work/progress.tsv \
  -o work/progress.svg \
  --ylabel cycles \
  --direction lower \
  --target 1000
```

Use `--direction higher` for scores where larger is better. The score panel always uses candidate number on the x-axis. The score y-axis defaults to `--score-scale auto`: log scale when all plotted score and target values are positive, otherwise linear scale. The token panel uses elapsed wall time from recorded `get_goal` snapshots. For deterministic artifacts or exact snapshot tests, set `--generated-at <iso timestamp>`, `--no-generated-at`, or `SOURCE_DATE_EPOCH`.

The rendered SVG and static dashboard footer show the full URL for the bundled `problem-agnostic-optimization` skill source.

Render the static dashboard:

```bash
python skills/problem-agnostic-optimization/scripts/progress_dashboard.py work/progress.tsv \
  -o work/dashboard.html \
  --ylabel "Authoritative metric" \
  --direction lower
```

The static dashboard is the safest remote-server path: regenerate `work/dashboard.html`, then open, download, or attach that file. For live local review, run:

```bash
python skills/problem-agnostic-optimization/scripts/progress_dashboard.py work/progress.tsv \
  --serve \
  --host 127.0.0.1 \
  --port 8765
```

`progress_dashboard.py` passes `--target`, `--hide-before-candidate`, `--score-scale`, `--generated-at`, `--no-generated-at`, and `SOURCE_DATE_EPOCH` through to the embedded SVG renderer.

On a remote server, keep the server bound to `127.0.0.1` and open a tunnel from the local machine:

```bash
ssh -L 8765:127.0.0.1:8765 <user>@<remote-host>
```

`work/progress.tsv` should be tab-separated. New runs must include `timestamp`, `candidate`, `score` or another authoritative metric column, `decision`, `tokens_total`, `tokens_delta`, `wall_seconds`, and `label` in every row. `timestamp` must be a UTC snapshot in `YYYY-MM-DDTHH:MM:SSZ` form. `wall_seconds` is cumulative elapsed wall time since the run start, or since the first recorded snapshot if the true run start is unavailable. Token/time values may be blank when unavailable, but do not omit the columns. If candidate names contain unrelated digits, include `candidate_number`; otherwise the chart only parses pure numeric IDs and `cand_0001`-style IDs as candidate numbers. Do not put fabricated token deltas into this table.

Use the bundled writer when available so the row shape is deterministic:

```bash
python skills/problem-agnostic-optimization/scripts/record_progress.py \
  --progress work/progress.tsv \
  --candidate cand_0007 \
  --metric cycles=2226 \
  --decision promote \
  --tokens-total 4500 \
  --tokens-delta 1400 \
  --wall-seconds 1080 \
  --label "dependency-list scheduled vector kernel"
```

Use `--score 0.992` for a default `score` column, `--metric name=value` for metric-specific columns such as `cycles`, and `--metric-name cycles` for bug/crash rows where the metric column must exist but the value is unavailable. Hand-write TSV rows only if `record_progress.py` is missing.

Use `--candidate-number 7` when the candidate name has unrelated digits and the TSV has a `candidate_number` column. If `--candidate-number` is provided for an existing TSV that lacks that column, the writer fails instead of silently changing a live schema. If `--tokens-total` is provided and `--tokens-delta` is omitted, the writer computes `tokens_delta` from the previous nonblank cumulative token total when available; otherwise it leaves the field blank.

```text
timestamp	candidate	cycles	decision	tokens_total	tokens_delta	wall_seconds	label
2026-06-01T00:00:00Z	0	147734	baseline	1200	1200	0	scalar starter baseline
2026-06-01T00:10:00Z	1	3360	promote	3100	1900	600	vectorized full gather, scratch values and paths
2026-06-01T00:18:00Z	2	2226	promote	4500	1400	1080	dependency-list scheduled vector kernel
```

Token snapshots must be explicit. In Codex, always try to call `get_goal` after each measured candidate and append the raw or structured snapshot to `work/log.md` with UTC timestamp, elapsed wall time, total tokens, token delta since the previous snapshot when known, and all available token fields: input, cached input, output, reasoning output, cache creation, and cache read. Copy the latest snapshot into `work/state.json` under `progress.latest_usage_snapshot`. If early token history is missing, show it as unknown; do not interpolate or invent per-candidate token usage.

`work/events.jsonl` is retained for backward compatibility with older runs and `record_event.py`. New runs should use `work/progress.tsv` for score rows and `work/log.md` for token snapshots. Legacy token columns in TSV or JSONL may be read for compatibility only; they are lower-confidence than explicit `get_goal` snapshots, should be labeled as legacy when charted, and should not be used as new-run doctrine.

Only `baseline`, `promote`, and `promoted` rows update the protected-best curve. Use `keep` for retained evidence or ties that did not pass the canonical promotion gate.

The dashboard is diagnostic. It can trigger push/reassess decisions, but it never replaces correctness checks or the authoritative promotion gate.

To disable chart rendering, record `Progress chart: off` in the `/goal` contract and set `progress.chart_enabled` to `false` in `work/state.json`. Continue appending `work/progress.tsv` and `work/log.md` unless the user explicitly disables progress logging too.

After every measured candidate:

- Always try to capture current token/time usage with `get_goal`.
- Append `work/progress.tsv` with `record_progress.py` when available, using the authoritative metric result and token/time fields when available.
- Append the raw or structured UTC usage snapshot to `work/log.md`.
- Copy the latest usage snapshot to `work/state.json`.
- Regenerate `work/progress.svg` and `work/dashboard.html` unless charting is disabled.
- Update `work/review.md` unless charting is disabled. Include current best, last 5-10 candidates, token burn since last promotion, stagnation count, open blockers, and next candidate.
- Treat high token burn without authoritative improvement, rising bug/crash rate, or many same-family rejects as evidence for reassessment.

## Edit Surface

Before the first candidate, write the mutable and immutable file sets into `work/best.md` or `work/state.json`.

- Editable files: candidate implementation files, candidate-local scripts, notes, and generated outputs.
- Immutable files: reference implementations, evaluation harnesses, data generators, scoring code, benchmark wrappers, and submission protocol files unless the user explicitly asks to change them.
- Touch only files required by the candidate hypothesis. Do not refactor adjacent code, normalize formatting, or clean unrelated dead code during optimization.
- If the evaluator or harness appears wrong, log a platform or harness issue and ask before modifying it. A faster result from changing the grader is not an optimization result.
- When two candidates tie within noise, prefer the smaller and simpler diff.

## Fresh-Run Isolation

Fresh-run isolation defaults to `on`. In a new assigned workspace, use only the current workspace, user-provided context, and official target artifacts. Do not mine sibling workspaces, old candidate logs, prior submissions, cached solutions, or dashboard snapshots unless `/goal` says `Fresh-run isolation: off` or the user explicitly asks for prior-run transfer.

When isolation is `on`:

- Reading the current workspace, current git history, official problem statement, and user-provided links is allowed.
- Reading sibling workspaces, archived `work/` directories, old submissions, or private prior notes is not allowed unless they are listed as allowed sources.
- If prior work appears relevant, ask or log a transfer note instead of silently importing it.

Record the setting in `work/state.json` as `isolation.fresh_run`.

## Multi-Agent Search

Use only when `Multi-agent mode: on` is present in the `/goal` or the user explicitly asks for parallel workers. Use this mode when several independent hypotheses can be tested from the same protected parent. It is a throughput tool, not a promotion shortcut: workers explore in parallel, while the coordinator serializes canonical writes and promotions.

### Canonical Roles

- **Coordinator**: owns the canonical workspace, `work/state.json`, `work/best.md`, `work/breakthroughs.md`, `work/log.md`, `work/progress.tsv`, charts, dashboard, and final promotion decisions.
- **Worker**: operates in an isolated worktree or copied sandbox from a named parent artifact/hash. A worker may run screening and local validation, but cannot mutate the canonical ledger or declare a promotion.
- **Auditor**: optional read-only reviewer. Use `references/auditor.md` after a batch, a surprising result, repeated bugs, or suspected drift.

### Batch Protocol

1. Freeze a parent: current best path, score, hash, ledger index, and bottleneck model.
2. Issue one candidate packet per worker: parent, parent hash, hill status (`OPEN`, `NARROWED`, or `CLOSED`), target lane, duplicate check, push budget, hypothesis, mechanism class, expected signal, kill criterion, smallest edit, validation, screening metric, authoritative metric, budget, editable files, and immutable files.
3. Workers run only in their isolated sandboxes and save raw outputs under worker-local paths.
4. Workers return a patch/diff, evidence summary, candidate JSON or enough fields to create it, raw output paths, token/time usage if available, parent hash, duplicate-check result, and recommendation.
5. Coordinator triages results, rejects wrong or stale outputs, and applies at most one candidate at a time to the canonical workspace.
6. Coordinator reruns correctness and the authoritative metric in the canonical environment before any promotion.
7. Coordinator appends every result to the ledger and refreshes charts/dashboard/review after the batch.

### Worker Restrictions

Workers must not edit canonical `work/state.json`, `work/best.md`, `work/breakthroughs.md`, `work/log.md`, `work/events.jsonl`, `work/progress.tsv`, charts, dashboard, benchmark harnesses, immutable files, or final submission files. They must not promote from screening metrics, stale parents, wrong-answer speedups, modified graders, or private leaked results.

Workers also must not mark canonical checkpoints complete. The coordinator alone updates `work/checkpoints/progress.json`, creates canonical candidate result JSON files, and runs the fresh verifier gate.

### Search Allocation

Use parallelism to reduce duplicate thinking:

- Assign some workers to exploit the active hill only while recent evidence predicts improvement.
- Assign at least one worker off-hill after plateau evidence: representation, primitive, route/library/config, target split, or contract specialization.
- Use workers to diversify search allocation, not to multiply the same local tweak.
- Record closed hills and duplicate attempts so future batches do not retry them without a new premise.
- Near ties still favor the smaller, simpler, less stateful artifact after canonical retest.

## Audit Surface

For long runs, a second Codex session may audit progress without becoming a second optimizer. Use `references/auditor.md` for the audit protocol.

Default auditor contract:

- Read current run artifacts and official target context.
- Write or append only `work/audit.md`.
- Do not edit candidate code, harness files, `work/best.md`, `work/log.md`, `work/plan.md`, `work/state.json`, `work/events.jsonl`, or `work/progress.tsv`.
- Do not launch new candidates, submissions, benchmarks, or long-running jobs unless explicitly asked.
- Report one verdict: `ON TRACK`, `NEEDS REASSESSMENT`, `BLOCKED`, `INVALIDATED`, or `NEEDS USER DECISION`.

## Profiling Plan

Write the profiling plan into `work/best.md` or `work/state.json` before deep tuning:

- Authoritative metric and command.
- Available profiling surfaces: target profiler, hardware counters, traces, flamegraphs, per-case timings, logs, public profiles, static analyzers, or none.
- Profiling strength: `strong`, `medium`, `weak`, or `none`.
- Profile command, permissions, target hardware, and output paths.
- What each profile can and cannot prove.
- Fallback evidence when profiling is absent or not target-faithful.

Use profiles to choose experiments:

- Profile or counter-sample the baseline/current best when the cost is reasonable.
- Compare parent and candidate with the same workload and command.
- Save raw profile output under `work/profiles/` or an equivalent durable path.
- Summarize only the decision-relevant deltas in `work/log.md`.
- Re-profile after promotions and surprising regressions; the bottleneck map may change.

If strong profiling is unavailable:

- Mark `profiling_strength` as `weak` or `none`.
- Replace it with resource floors, per-case timings, controlled ablations, static models, and repeated authoritative measurements.
- Treat the bottleneck model as a hypothesis. Escalate to structural probes sooner when weak evidence keeps mispredicting results.

## Git-Backed Experiment Loop

When git is available and the run has many candidates, use it as the keep/discard mechanism:

1. Start from the protected best on a named experiment branch.
2. Make one candidate change.
3. Commit or snapshot the candidate before running the expensive measurement.
4. Keep the commit only if promotion gates pass.
5. Revert or reset losing candidates after logging their result.

Keep noisy ledgers such as `work/log.md`, `work/state.json`, raw logs, and TSV summaries untracked if the repository should only preserve winning code. Keep them tracked when the project expects reproducible experiment history.

## Fixed-Budget Experiments

Some tasks are defined by a fixed budget instead of fastest wall time: five minutes of training, 30 public submissions per day, one Modal run, a GPU-hour cap, an API spend cap, or a maximum memory envelope.

- Record the fixed budget in `work/best.md` and `work/state.json`.
- Judge candidates by the official metric under that same budget.
- Do not compare a longer or more expensive run against the baseline unless the contract allows it.
- Treat timeout, OOM, daily submission exhaustion, and spend limits as first-class results.
- If the user asks for autonomous operation, keep looping within the recorded budget and stop only at the agreed limit, an external blocker, or a verified objective.

## File Roles

### `work/best.md`

Stable promoted state only:

- Objective and target.
- Mode and objective source.
- Current best stable artifact and score.
- Current benchmark-only best, if different.
- Fixed budget and allowed edit surface.
- Seed protocol and statistical promotion gate for stochastic targets.
- Validation commands and result IDs.
- Profile commands, availability, confidence, and artifact paths.
- Why the best wins.
- Confirmed bottlenecks.
- Exhausted branches that must not be retried without a new premise.
- Open directions.

Do not put every experiment here.

### `work/log.md`

Append-only experiment ledger. Every candidate, including failures, gets:

```markdown
## <timestamp> :: <candidate_id>

- candidate:
- parent:
- mode: SEED | EXPLORE | TUNE | RECOVER | VERIFY | CLOSE
- branch:
- hypothesis:
- change summary:
- expected signal:
- validation command:
- benchmark/submit command:
- profile command:
- result:
- correctness:
- usage snapshot UTC:
- wall_seconds:
- tokens_total:
- tokens_delta:
- profile/counter delta:
- stability:
- improved best:
- decision: PROMOTE | REJECT | RERUN | RECOVER | CLOSE
- learning:
- raw result paths:
```

Failures should kill or narrow families of ideas, not just individual files.

### `work/plan.md`

Mutable active strategy:

- Target and current best.
- Stagnation count.
- Active branches with hypothesis, next probe, expected signal, and budget.
- Frozen/closed branches with reasons.
- Escape ladder state: stuck signal, divergence burst, and active new-hill commitment.
- Escalation rule for local-optimum audit or structural reset.

### `work/audit.md`

Auditor-mode report from a second Codex session. The optimizer should read it as feedback, not as a candidate ledger.

- Current audit verdict.
- Contract and promotion-integrity findings.
- Progress since last audit.
- Token/time burn and stagnation risk.
- Blockers or invalidation risks.
- Recommended next action.

Append dated sections instead of overwriting useful prior audit history.

### `work/state.json`

Small machine-readable state:

```json
{
  "target_score": null,
  "score_unit": null,
  "mode": null,
  "objective_source": null,
  "theoretical_floor": null,
  "best_stable_candidate": null,
  "best_stable_score": null,
  "best_benchmark_candidate": null,
  "best_benchmark_score": null,
  "fixed_budget": null,
  "seed_protocol": {},
  "scenario_sets": {},
  "statistical_gate": null,
  "profiling": {
    "strength": null,
    "available_surfaces": [],
    "unavailable_surfaces": [],
    "commands": {},
    "artifact_paths": [],
    "confidence": null,
    "fallback_evidence": []
  },
  "editable_files": [],
  "immutable_files": [],
  "isolation": {
    "fresh_run": true,
    "allowed_prior_sources": []
  },
  "escape": {
    "status": "tracking",
    "stuck_signal": null,
    "closed_hills": [],
    "divergence_budget": null,
    "active_burst": [],
    "committed_hill": null,
    "commitment_budget": null,
    "kill_criterion": null
  },
  "multi_agent": {
    "enabled": false,
    "mode": "off",
    "coordinator_workspace": "canonical",
    "worker_isolation": "worktree_or_copied_sandbox",
    "active_workers": [],
    "completed_workers": [],
    "promotion_policy": "coordinator_only_authoritative_gate"
  },
  "round": 0,
  "iterations": 0,
  "stagnation_count": 0,
  "next_candidate_id": 1,
  "active_branches": [],
  "exhausted_branches": [],
  "rate_limits": {},
  "pending_jobs": [],
  "progress": {
    "logging_enabled": true,
    "chart_enabled": true,
    "events": "work/events.jsonl",
    "dashboard": "work/dashboard.html",
    "table": "work/progress.tsv",
    "chart": "work/progress.svg",
    "review": "work/review.md",
    "x_axis": "candidate",
    "tokens_total": 0,
    "tokens_since_promotion": 0,
    "token_budget": null,
    "usage_source": "explicit get_goal snapshots in work/log.md",
    "usage_gap": null,
    "latest_usage_snapshot": {
      "source": "get_goal",
      "recorded_at": null,
      "wall_seconds": null,
      "total_tokens": null,
      "input_tokens": null,
      "cached_input_tokens": null,
      "output_tokens": null,
      "reasoning_output_tokens": null,
      "cache_creation_input_tokens": null,
      "cache_read_input_tokens": null
    }
  },
  "audit": {
    "enabled": true,
    "report": "work/audit.md",
    "write_surface": ["work/audit.md"],
    "last_audited_at": null,
    "last_verdict": null
  },
  "last_updated": null
}
```

Scripts can update this file, but it should remain human-readable.

## Candidate Modes

Use explicit modes:

- `SEED`: import a known baseline into the harness.
- `EXPLORE`: test a new mechanism; a clear signal is useful even without a win.
- `TUNE`: tune a proven mechanism; should improve target or bottleneck shape.
- `RECOVER`: fix a fast branch that failed correctness, ranked stability, or hidden mode.
- `VERIFY`: rerun, cross-check, or fan out a candidate.
- `CLOSE`: mark a branch exhausted with evidence.

## Candidate Lifecycle

Every candidate follows:

```text
idea -> hypothesis -> candidate file -> validation -> measurement -> rerun if needed -> promotion or rejection -> logged learning
```

Checklist:

- Name the parent candidate.
- State exactly one hypothesis.
- Predict which shape, row, counter, or metric should improve.
- Validate correctness first when possible.
- Measure with the same command used for comparable candidates.
- Rerun if the result is close to noise or surprisingly good.
- Promote only if it beats the stable baseline under the required validation mode.
- Update `best.md`, `log.md`, `plan.md`, and `state.json`.

## Crash Handling

A crash is still a result:

- If it is a trivial implementation mistake, such as a typo, missing import, wrong include, or obvious build flag, fix it once and rerun the same hypothesis.
- If the crash is intrinsic to the idea, such as OOM, timeout, illegal memory access, compiler failure from unsupported codegen, or shape-incompatible logic, log `crash` or `bug` and move on.
- Always inspect the tail of the raw log before classifying the crash.
- Do not promote speed from failed, wrong-answer, or partial-run states.
- Use repeated OOM/timeout crashes as resource-floor evidence against that branch.

## Branch Management

Each branch should have:

- Name.
- Hypothesis.
- Owner route, shape, system, or primitive.
- Known wins.
- Known failures.
- Next probe.
- Budget and stop condition.

Close branches aggressively when evidence is strong. Reopen only if a new mechanism changes the premise.

## Stagnation Rule

After repeated same-route failures, stop making variants.

Default rule:

```text
If 5 consecutive candidates fail to improve the stable best, require a topology refresh:
1. rewrite the bottleneck map
2. list closed branches
3. identify the primitive that must change
4. propose 3 structural alternatives
5. spend the next round only on structural probes
```

This complements the local-optimum audit in `resource-models.md`.

## Optional Coordinator

For remote leaderboards, scripts should enforce queue and rate-limit discipline:

- Max active submissions: usually 2-3 unless the platform says otherwise.
- Do not submit a comparable candidate while one is pending.
- Store raw output for every job.
- Parse completed jobs into `work/results/<candidate>.json`.
- Update `work/log.md`, `work/state.json`, and `work/best.md` only when promotion gates pass.

Coordinator loop:

```text
read state.json
poll pending jobs
parse completed results
update log/results
promote if gates pass
select next candidate from plan.md
validate
submit if rate limits allow
sleep or exit
```

## Results Table

For autonomous or overnight runs, maintain a compact tab-separated results table. Tabs are deliberate because descriptions often contain commas.

```text
candidate	score	memory_or_cost	status	description
cand_0000	37.900	0.0	baseline	baseline
cand_0001	36.700	0.0	promote	exact-shape route
cand_0002	0.000	0.0	crash	OOM on larger tile
cand_0003	38.200	0.0	discard	graph wrapper regressed
```

Use status values like `baseline`, `promote`, `keep`, `discard`, `crash`, `bug`, `blocked`, and `verify`. The score column should be the authoritative metric when available; otherwise label it as a screening metric in the description.

## Extended Candidate JSON

Use this as an extension of the typed candidate artifact, not a replacement for it. Keep the required fields from `work/schemas/candidate_result.schema.json`, then add domain-specific result blocks as needed:

```json
{
  "schema_version": 1,
  "candidate": "cand_0008",
  "file": "candidates/cand_0008.py",
  "parent": "cand_0007",
  "parent_hash": "git-or-file-hash",
  "branch": "m16-specialized-reduce",
  "mode": "TUNE",
  "mechanism_class": "representation/primitive/route change",
  "duplicate_check": "not the same hill as cand_0007 because it changes the reduction primitive",
  "timestamp": "2026-05-29T00:00:00Z",
  "commands": {
    "apply_or_build": "...",
    "correctness": "...",
    "authoritative_metric": "...",
    "regression_or_adversarial": "...",
    "fresh_verifier": "...",
    "validate": "...",
    "benchmark": "...",
    "profile": "...",
    "submit": "..."
  },
  "correctness": "pass",
  "benchmark": {
    "score": null,
    "unit": null,
    "per_shape": {}
  },
  "profiling": {
    "strength": null,
    "artifacts": [],
    "key_deltas": {},
    "interpretation": "",
    "fallback_evidence": []
  },
  "escape": {
    "status": "tracking",
    "stuck_signal": null,
    "closed_hill": null,
    "divergence_probe": null,
    "new_hill": null,
    "mechanism_signal": "",
    "commitment_budget": null,
    "kill_criterion": null
  },
  "ranked": {
    "score": null,
    "status": "not_run"
  },
  "promotion_ladder": {
    "apply_or_build": "pass",
    "correctness": "pass",
    "authoritative_metric": "fail",
    "regression_or_adversarial": "not_run",
    "fresh_verifier": "not_run",
    "promote": "fail"
  },
  "verifier": {
    "mode": "fresh_environment_when_possible",
    "verdict": "SKIPPED_WITH_LIMITATION",
    "evidence": "",
    "limitations": ["candidate did not pass authoritative metric"]
  },
  "stochastic_policy": {
    "scenario_set": "validation_v03",
    "num_scenarios": 1000,
    "matched_parent": "cand_0007",
    "seed_policy": "fixed common-random-numbers",
    "score": {
      "mean": null,
      "median": null,
      "std": null,
      "sem": null,
      "min": null,
      "p05": null,
      "p95": null,
      "max": null,
      "win_rate_vs_parent": null
    },
    "regime_buckets": {},
    "decomposition": {
      "benign_reward": null,
      "adversarial_loss": null,
      "opportunity_cost": null,
      "tail_loss": null,
      "constraint_cost": null
    },
    "constraints": {
      "runtime_ok": null,
      "memory_ok": null,
      "storage_ok": null,
      "compute_or_gas_ok": null,
      "invalid_action_rate": null,
      "exception_rate": null
    },
    "overfit_checks": {
      "train_validation_gap": null,
      "holdout_checked": false,
      "sharp_parameter_spike": null,
      "same_artifact_rerun": false
    }
  },
  "decision": "REJECT",
  "learning": ""
}
```

## What To Do Each Turn

At the start:

- Read `work/best.md`.
- Read `work/breakthroughs.md` if it exists and the run is plateaued, public-leaderboard driven, multi-agent, or near a resource tier.
- Read the tail of `work/log.md`.
- Read `work/plan.md`.
- Read `work/state.json`.
- Read recent rows from `work/progress.tsv` and the latest token snapshots in `work/log.md` if `progress.logging_enabled` is not `false`.
- Open `work/dashboard.html`, `work/progress.svg`, and `work/review.md` if `progress.chart_enabled` is not `false`.
- Check pending jobs if using a remote system.

Before editing:

- State candidate parent.
- State parent hash when available.
- State mode.
- State one hypothesis.
- State mechanism class and duplicate check.
- State expected signal.
- State profiling basis and fallback if no useful profiler is available.
- State validation and measurement command.
- Create or plan the candidate JSON path under `work/candidates/`.

After running:

- Append `work/log.md`.
- Save or update the candidate JSON artifact under `work/candidates/`.
- Always try to capture current token/time usage with `get_goal`.
- Append the measured candidate to `work/progress.tsv` with `record_progress.py` if `progress.logging_enabled` is not `false` and the script is available, using token/time fields when available.
- Append the UTC snapshot, wall time, `tokens_total`, and `tokens_delta` to `work/log.md`, and copy the latest snapshot to `work/state.json`.
- Save raw and normalized outputs.
- Save profile/counter artifacts when available.
- Update `work/breakthroughs.md` when the result changes a tier, identifies a co-binder, calibrates a screen, uses a validation island, or rules out a tempting route.
- Update `work/plan.md` and `work/breakthroughs.md` when a hill is closed, an escape burst starts, or a divergence probe earns a new-hill commitment budget.
- Update `work/state.json`.
- Update `work/checkpoints/progress.json` with the current phase and terminal result when appropriate.
- Run or record the fresh verifier gate before any stable promotion.
- If `progress.chart_enabled` is not `false`, regenerate `work/progress.svg`, regenerate `work/dashboard.html`, and refresh `work/review.md`.
- Update `work/best.md` only if promotion rules pass.
- Update `work/plan.md` with next branch status.

## Structural Reset Prompt

Use when the search stalls:

```markdown
Stop generating variants of the current route.

Do a topology refresh:
1. Summarize the current best and why it wins.
2. List the last 10 failed candidates and what they prove.
3. Identify the hot primitive or bottleneck shape that still dominates.
4. Mark exhausted branches as CLOSED.
5. Propose 3 structural alternatives that replace the primitive or route.
6. Create only one probe per alternative.
7. If one probe opens a new hill, commit a short follow-up budget before scattering again.
8. Preserve the current best unchanged.
```
