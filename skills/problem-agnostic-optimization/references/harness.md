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

Run this from the target repository root so it creates the local `work/` directory for that optimization run. Add `--progress-chart off` only when the contract says `Progress chart: off`. Add `--fresh-run-isolation off` only when the user has allowed prior-run transfer.

If the initializer is unavailable, create the same files manually before candidate work. Do not wait until after the first result to create the ledger.

## Minimal Harness

For small projects, create only:

```text
work/
  audit.md
  best.md
  dashboard.html             # static dashboard for local or remote review
  events.jsonl               # canonical progress ledger for long runs
  log.md
  plan.md
  progress.tsv              # small-run table or derived export
  progress.svg
  review.md
  state.json
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
    dashboard.html
    events.jsonl
    log.md
    plan.md
    progress.tsv
    progress.svg
    state.json
    candidates/
      cand_0001.md
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

## Progress Monitor

For substantial optimization runs, maintain a live progress surface by default. The canonical long-run record is `work/events.jsonl`; `work/progress.tsv` is a small-run format or derived export.

```text
work/events.jsonl   # one JSON object per baseline, candidate, failure, blocker, or handoff
work/dashboard.html  # static dashboard for review and handoff
work/progress.tsv   # one row per measured candidate for small/manual runs or exports
work/progress.svg   # chart regenerated after each result unless Progress chart: off
work/review.md      # short human review snapshot unless Progress chart: off
```

Render the chart from either ledger:

```bash
python skills/problem-agnostic-optimization/scripts/progress_chart.py work/progress.tsv \
  -o work/progress.svg \
  --ylabel "Authoritative metric" \
  --direction lower

python skills/problem-agnostic-optimization/scripts/progress_chart.py work/events.jsonl \
  -o work/progress.svg \
  --ylabel "Authoritative metric" \
  --direction lower \
  --x-axis tokens
```

Append an event and refresh the chart in one step:

```bash
python skills/problem-agnostic-optimization/scripts/record_event.py \
  --candidate cand_0001 \
  --decision promote \
  --score 0.992 \
  --tokens-total 3100 \
  --tokens-delta 1900 \
  --active-seconds 420 \
  --wall-seconds 900 \
  --chart work/progress.svg \
  --direction lower
```

Use `--direction higher` for scores where larger is better. Use `--x-axis candidate`, `tokens`, `active`, or `wall` to review progress by candidate order, token burn, tracked active time, or wall time. The chart plots all candidates, the running promoted best, and cumulative token usage on the right axis.

Render the static dashboard:

```bash
python skills/problem-agnostic-optimization/scripts/progress_dashboard.py work/events.jsonl \
  -o work/dashboard.html \
  --ylabel "Authoritative metric" \
  --direction lower \
  --x-axis tokens
```

The static dashboard is the safest remote-server path: regenerate `work/dashboard.html`, then open, download, or attach that file. For live local review, run:

```bash
python skills/problem-agnostic-optimization/scripts/progress_dashboard.py work/events.jsonl \
  --serve \
  --host 127.0.0.1 \
  --port 8765
```

On a remote server, keep the server bound to `127.0.0.1` and open a tunnel from the local machine:

```bash
ssh -L 8765:127.0.0.1:8765 <user>@<remote-host>
```

`work/events.jsonl` should append one object after every completed result. Token/time fields are required but nullable: every new event should include `tokens_total`, `tokens_delta`, `active_seconds`, and `wall_seconds`. In Codex, call `get_goal` when available and persist `tokensUsed` as `tokens_total` and `timeUsedSeconds` as `active_seconds`; compute `tokens_delta` from the previous event when possible. If usage is unavailable, set the field to `null` and note the gap in `work/review.md`. Do not omit token fields from new events, invent historical per-candidate usage, or encode failure as a fake zero score.

```json
{"candidate":"cand_0000","decision":"baseline","score":1.0,"tokens_total":1200,"tokens_delta":1200,"active_seconds":30,"wall_seconds":60,"label":"baseline"}
{"candidate":"cand_0001","decision":"promote","score":0.992,"tokens_total":3100,"tokens_delta":1900,"active_seconds":420,"wall_seconds":900,"label":"fused route"}
{"candidate":"cand_0002","decision":"reject","score":0.996,"tokens_total":4500,"tokens_delta":1400,"active_seconds":680,"wall_seconds":1320,"label":"tile too small"}
```

`work/progress.tsv` should be tab-separated:

```text
candidate	score	decision	tokens_total	tokens_delta	label
cand_0000	1.000	baseline	1200	1200	baseline
cand_0001	0.992	promote	3100	1900	fused route
cand_0002	0.996	reject	4500	1400	tile too small
```

To disable chart rendering, record `Progress chart: off` in the `/goal` contract and set `progress.chart_enabled` to `false` in `work/state.json`. Continue appending `work/events.jsonl` unless the user explicitly disables progress logging too.

After every measured candidate:

- Capture current token/time usage when the runtime exposes it.
- Append `work/events.jsonl` with token/time fields; if using TSV, append or regenerate `work/progress.tsv` with `tokens_total` and `tokens_delta` columns.
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
    "usage_source": "runtime goal usage if available",
    "usage_gap": null
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
cand_0000	37.900	0.0	keep	baseline
cand_0001	36.700	0.0	keep	exact-shape route
cand_0002	0.000	0.0	crash	OOM on larger tile
cand_0003	38.200	0.0	discard	graph wrapper regressed
```

Use status values like `keep`, `discard`, `crash`, `bug`, `blocked`, and `verify`. The score column should be the authoritative metric when available; otherwise label it as a screening metric in the description.

## Normalized Result JSON

Store raw outputs, plus a small normalized result:

```json
{
  "candidate": "cand_0008",
  "file": "candidates/cand_0008.py",
  "parent": "cand_0007",
  "branch": "m16-specialized-reduce",
  "mode": "TUNE",
  "timestamp": "2026-05-29T00:00:00Z",
  "commands": {
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
  "ranked": {
    "score": null,
    "status": "not_run"
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
- Read the tail of `work/log.md`.
- Read `work/plan.md`.
- Read `work/state.json`.
- Read the tail of `work/events.jsonl` if `progress.logging_enabled` is not `false`.
- Open `work/dashboard.html`, `work/progress.svg`, and `work/review.md` if `progress.chart_enabled` is not `false`.
- Check pending jobs if using a remote system.

Before editing:

- State candidate parent.
- State mode.
- State one hypothesis.
- State expected signal.
- State profiling basis and fallback if no useful profiler is available.
- State validation and measurement command.

After running:

- Append `work/log.md`.
- Capture current token/time usage and append `work/events.jsonl` with `tokens_total`, `tokens_delta`, `active_seconds`, and `wall_seconds` if `progress.logging_enabled` is not `false`.
- Save raw and normalized outputs.
- Save profile/counter artifacts when available.
- Update `work/state.json`.
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
7. Preserve the current best unchanged.
```
