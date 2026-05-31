# Templates

Use the default templates for normal optimization runs. Use the extended templates only when the run needs extra profiling, per-case, stochastic, or handoff structure.

## Default Templates

### Contract

```markdown
## Contract

- Mode:
- Objective:
- Authoritative metric:
- Baseline:
- Target or floor:
- Validation:
- Budget / stopping rule:
- Progress chart: on | off
- Fresh-run isolation: on | off
- Editable files:
- Immutable files:
- Evidence available:
```

### Bottleneck Model

```markdown
## Bottleneck Model

- Primary bottleneck:
- Gap class: floor gap | schedule gap | evidence gap | statistical gap
- Evidence:
- Profiling strength: strong | medium | weak | none
- Resource/statistical floors:
- Runtime or score gap versus floor:
- Tail/dependency risk:
- What likely will not help:
- Structural alternatives:
- Next cheapest falsifiable probe:
```

### Candidate Ledger Entry

```markdown
## vNN-short-name

- Parent:
- Hypothesis:
- Mechanism class:
- Expected signal:
- Kill criterion:
- Artifact:
- Correctness:
- Validation command:
- Measurement command:
- Result:
- Decision: PROMOTE | KEEP VARIANT | REJECT | BUG | BLOCKED
- Push/reassess:
- Hill status: OPEN | NARROWED | CLOSED
- Learning:
- Next:
```

### Local-Optimum Audit

```markdown
## Local-Optimum Audit

- Current hill:
- Why it looked promising:
- Best verified result:
- Plateau evidence:
- Floor/resource blocker:
- Tail/dependency/statistical blocker:
- Remaining plausible gain on this hill:
- Why that is not enough:

Different hills:
- Primitive change:
- Representation change:
- Route/library/config change:
- Contract specialization or target split:

Next off-hill probe:
- Artifact:
- Hypothesis:
- Expected signal:
- Kill criterion:
```

## Extended Templates

Use the per-case table when aggregate metrics hide important differences.

### Per-Case Contract Table

```markdown
| Case | Shape/Input | Dtype/Layout/Seed | Current Route | Current Score/Time | Target/Leader | Notes |
|---|---|---|---|---:|---:|---|
```

### Resource Floor Table

```markdown
| Resource | Work Count | Throughput | Floor | Current Pressure | Candidate Delta |
|---|---:|---:|---:|---|---:|
```

### Profiling Inventory

```markdown
## Profiling Inventory

- Authoritative metric:
- Authoritative command:
- Target hardware/system:
- Profiling strength: strong | medium | weak | none
- Available surfaces:
- Unavailable surfaces:
- Profile commands:
- Profile artifact paths:
- What profiles can prove:
- What profiles cannot prove:
- Fallback evidence:
```

### Profile Comparison

```markdown
## Profile Comparison

| Artifact | Score | Runtime/Cycles | Key Profile Counters | What Improved | What Regressed | Confidence |
|---|---:|---:|---|---|---|---|

Interpretation:
- Primary bottleneck:
- Ruled-out knobs:
- New pressure introduced:
- Next candidate hypothesis:
```

### Tail Audit

```markdown
## Tail Audit

- Last-finishing unit/item:
- Saturated resource near end:
- Required waits/barriers:
- Scratch or alias dependencies:
- Stores/finalization pressure:
- Candidate tail risk:
```

### Stateful Stochastic Policy Result

```markdown
## policy-NN

- Parent:
- Hypothesis:
- Mechanism family:
- Candidate type:
- Artifact:
- Evaluation level: L0 | L1 | L2 | L3 | L4 | L5
- Scenario sets:
- Validity / invalid-action rate:
- Train scenarios:
- Validation scenarios:
- Holdout scenarios:
- Mean / median / SEM:
- p05 / p95 / worst decile:
- Win rate vs parent:
- Constraint margins:
- Regime table:
- Decomposition table:
- Overfit checks:
- Public submission:
- Decision:
- Next:
```

```text
candidate	level	mean	sem	p05	p95	win_rate_vs_parent	invalid_rate	status	description
policy_0000	L3	0.000	0.000	0.000	0.000	0.500	0.000	keep	baseline
policy_0001	L3	1.250	0.180	-0.400	2.800	0.620	0.000	verify	better validation, check tail
policy_0002	L4	2.100	0.900	-6.500	8.200	0.480	0.000	discard	train overfit, bad holdout
```

### Per-Case Winner Table

```markdown
| Case | Best Artifact | Best Time | Runner/ID | Why it wins | Risk |
|---|---|---:|---|---|---|
```

### Results TSV

```text
candidate	score	memory_or_cost	status	description
cand_0000	37.900	0.0	keep	baseline
cand_0001	36.700	0.0	keep	exact-shape route
cand_0002	0.000	0.0	crash	OOM on larger tile
cand_0003	38.200	0.0	discard	graph wrapper regressed
```

### Progress Event JSONL

Use this for `work/events.jsonl`, the canonical progress ledger for long-running or dashboarded optimization. Append one JSON object after each baseline, measurement, failure, blocker, or handoff.

Required fields: `candidate`, `decision`, `tokens_total`, `tokens_delta`, `active_seconds`, and `wall_seconds`. Token/time fields may be `null` when unavailable, but do not omit them from new events. In Codex, capture `tokensUsed` and `timeUsedSeconds` from `get_goal` when available.

```json
{"candidate":"cand_0000","decision":"baseline","score":1.0,"tokens_total":1200,"tokens_delta":1200,"active_seconds":30,"wall_seconds":60,"label":"baseline"}
{"candidate":"cand_0001","decision":"promote","score":0.992,"tokens_total":3100,"tokens_delta":1900,"active_seconds":420,"wall_seconds":900,"label":"fused route"}
{"candidate":"cand_0002","decision":"reject","score":0.996,"tokens_total":4500,"tokens_delta":1400,"active_seconds":680,"wall_seconds":1320,"label":"tile too small"}
```

Optional fields:

```text
timestamp
parent
branch
mode
correctness
validation_command
measurement_command
score_unit
blocker
raw_result_path
```

### Progress TSV

Use this for small/manual `work/progress.tsv` runs or as a derived export from `work/events.jsonl`. Progress charting is on by default for substantial optimization runs. Regenerate `work/progress.svg` after appending rows unless `/goal` says `Progress chart: off`.

```text
candidate	score	decision	tokens_total	tokens_delta	label
cand_0000	1.000	baseline	1200	1200	baseline
cand_0001	0.992	promote	3100	1900	fused route
cand_0002	0.996	reject	4500	1400	tile too small
```

### `work/review.md`

```markdown
# Progress Review

- Current best:
- Best score:
- Last promotion:
- Candidates since promotion:
- Tokens since promotion:
- Token burn per promoted improvement:
- Token source:
- Token gap:
- Active time:
- Wall elapsed:
- Stagnation count:
- Bug/crash/blocked rate:
- Open blockers:
- Reassessment trigger:
- Next candidate:
```

### `work/dashboard.html`

Generate this from `work/events.jsonl` for local, remote, or handoff review:

```bash
python skills/problem-agnostic-optimization/scripts/progress_dashboard.py work/events.jsonl \
  -o work/dashboard.html \
  --direction lower \
  --x-axis tokens
```

For live remote review, run the dashboard server on the remote host with `--host 127.0.0.1 --port 8765`, then tunnel from your local machine:

```bash
ssh -L 8765:127.0.0.1:8765 <user>@<remote-host>
```

### `work/audit.md`

Use this for auditor-mode reports from a second Codex session. Append a dated section for each audit.

```markdown
# Optimization Audit

- Verdict: ON TRACK | NEEDS REASSESSMENT | BLOCKED | INVALIDATED | NEEDS USER DECISION
- Audited at:
- Scope:
- Current best:
- Latest event:
- Progress since last audit:
- Token/time burn:
- Contract issues:
- Promotion/integrity issues:
- Search-health issues:
- Blockers:
- Recommended next action:

## Evidence

| Check | Status | Evidence |
|---|---|---|
| Contract explicit | pass/fail/unknown | |
| Baseline reproduced | pass/fail/unknown | |
| Best state consistent | pass/fail/unknown | |
| Promotions authoritative | pass/fail/unknown | |
| Ledger/chart fresh | pass/fail/unknown | |
| Next action justified | pass/fail/unknown | |
```

### Speedup Classification

```markdown
Speedup class:
- [ ] real kernel speedup
- [ ] route/config speedup
- [ ] benchmark-contract specialization
- [ ] approximation inside tolerance
- [ ] variance
- [ ] forbidden shortcut (reject)

Promotion rationale:
Risk:
```

### Final Handoff

```markdown
## Optimization Handoff

- Goal:
- Status:
- Best verified artifact:
- Best authoritative result:
- Correctness evidence:
- Current bottleneck:
- What worked:
- What failed and why:
- Target-specific artifacts:
- Remaining budget/blockers:
- Next experiments:
```

### `work/best.md`

```markdown
# Best Known State

## Objective
Mode:
Target:
Objective source:
Theoretical floor:
Current best stable:
Current best benchmark-only:
Gap to target:

## Best Variant
Candidate:
File:
Parent:
Mechanism:
Validation:
Reliability:
Complexity:

## Why It Won
- 

## Confirmed Bottlenecks
1. 

## Exhausted Branches
- 

## Open Directions
1. 
```

### `work/plan.md`

```markdown
# Active Plan

Target:
Current best:
Stagnation:

## Active Branches

- B1:
  - hypothesis:
  - next probe:
  - expected signal:
  - budget:

## Frozen Branches

- 

## Escalation Rule

If <condition>, stop tuning this route and run a local-optimum audit.
```
