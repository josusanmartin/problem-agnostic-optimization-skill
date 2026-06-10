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

### Breakthrough Mining Table

```markdown
| row | parent -> candidate | score/resources | active floor | delta | mechanism | proof/invariant | search tool | validation | slack/dependency |
|---:|---|---:|---|---:|---|---|---|---|---|
| 001 | base -> cand |  |  |  |  |  |  |  |  |
```

### Phase-Owner / Co-Binder Table

```markdown
| phase/resource owner | height/cost | next floor | evidence | proposed stack |
|---|---:|---:|---|---|
|  |  |  |  |  |
```

### Screen Calibration Card

```markdown
## Screen: name

- Predicts:
- Known-clean cases reproduced:
- Known-dirty cases rejected:
- Coverage: cases/shapes/seeds/factors modeled
- Stacked-knob calibration:
- False-clean risk:
- False-dirty risk:
- Promotion use: advisory only
- Calibration command/artifact:
```

### Validation Island Card

```markdown
## Island: candidate/selector

- Contract-allowed reason:
- Selector/seed/nonce/route:
- Prior island invalidated by:
- Search command/artifact:
- Full validation command:
- Full validation result:
```

### Negative Breakthrough Card

```markdown
## Negative Breakthrough: idea

- Why it looked promising:
- Measured blocker:
- Resource trade:
- Validation result:
- Reopen condition:
```

### Escape Ladder

```markdown
## Escape Ladder

- Current hill:
- Stuck signal: promotion drought | same-family failures | model mismatch | low novelty | residual-only work | frontier mismatch | floor proof
- Plateau evidence:
- Closed or narrowed branch:
- Divergence budget:
- Budget owner: candidates | workers | submissions | wall time | spend
- Controlled regression allowed: yes | no
- Anti-revisit rule:
- Aspiration rule:

Probe packets:

| probe | operator | hill id | feature cell | new hill | active floor/resource axis | cheapest falsifiable signal | kill criterion | result |
|---|---|---|---|---|---|---|---|---|
| E1 |  |  |  |  |  |  |  |  |
| E2 |  |  |  |  |  |  |  |  |
| E3 |  |  |  |  |  |  |  |  |

Diversity map:

| feature cell | best artifact | best score | operator | signal | status |
|---|---|---:|---|---|---|
|  |  |  |  |  |  |

- Selected new hill:
- Why the signal is real:
- Operator credit update:
- Next action:
```

### New-Hill Commitment

```markdown
## New-Hill Commitment

- Source probe:
- Parent:
- New hill:
- Escape operator:
- Hill id:
- Feature cell:
- Mechanism signal:
- Stepping-stone evidence:
- Current loss or rough edge:
- Commitment budget:
- Follow-up 1:
- Follow-up 2:
- Follow-up 3:
- Kill criterion:
- Anti-revisit rule if closed:
- Operator credit update:
- Promotion gate:
- Reopen condition after closure:
```

### Closed-Hill Memory

```markdown
## Closed Hill: hill-id

- Feature cell:
- Best artifact:
- Best score:
- Why closed:
- Anti-revisit rule:
- Aspiration rule:
- Reopen condition:
```

### Escape Operator Credit

```markdown
| operator | attempts | positive signals | mixed signals | negative signals | last evidence | next allocation |
|---|---:|---:|---:|---:|---|---|
| perturb_reoptimize |  |  |  |  |  |  |
| neighborhood_shift |  |  |  |  |  |  |
| destroy_repair |  |  |  |  |  |  |
| annealed_regression |  |  |  |  |  |  |
| tabu_anti_revisit |  |  |  |  |  |  |
| surrogate_uncertainty |  |  |  |  |  |  |
| diversity_archive |  |  |  |  |  |  |
| adaptive_operator |  |  |  |  |  |  |
| external_intake |  |  |  |  |  |  |
| negative_proof |  |  |  |  |  |  |
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

Use this for compatibility `<harness>/events.jsonl` rows or structured progress exports. Append one JSON object after each baseline, measurement, failure, blocker, or handoff when this file is enabled. The default `<harness>` directory is `work/optimization_harness`.

Required fields: `timestamp`, `candidate`, `decision`, `tokens_total`, `tokens_delta`, `active_seconds`, `wall_seconds`, and `label`. `timestamp` must be UTC in `YYYY-MM-DDTHH:MM:SSZ` form. Token/time fields may be `null` when unavailable, but do not omit them from new events. In Codex, always try to capture `tokensUsed` and `timeUsedSeconds` from `get_goal` after each measured candidate.

```json
{"timestamp":"2026-06-01T00:00:00Z","candidate":"cand_0000","decision":"baseline","score":1.0,"tokens_total":1200,"tokens_delta":1200,"active_seconds":30,"wall_seconds":60,"label":"baseline"}
{"timestamp":"2026-06-01T00:10:00Z","candidate":"cand_0001","decision":"promote","score":0.992,"tokens_total":3100,"tokens_delta":1900,"active_seconds":420,"wall_seconds":900,"label":"fused route"}
{"timestamp":"2026-06-01T00:18:00Z","candidate":"cand_0002","decision":"reject","score":0.996,"tokens_total":4500,"tokens_delta":1400,"active_seconds":680,"wall_seconds":1320,"label":"tile too small"}
```

Optional fields:

```text
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

Use this for small/manual `<harness>/progress.tsv` runs or as a derived export from `<harness>/events.jsonl`. Progress charting is on by default for substantial optimization runs. Use `scripts/record_progress.py` when available. Regenerate `<harness>/progress.svg` and `<harness>/dashboard.html` with `scripts/render_progress.py` at sidecar checkpoints unless `/goal` says `Progress chart: off`.

Required columns: `timestamp`, `candidate`, an authoritative metric column such as `score` or `cycles`, `decision`, `tokens_total`, `tokens_delta`, `wall_seconds`, and `label`. `timestamp` must be a UTC snapshot in `YYYY-MM-DDTHH:MM:SSZ` form.

Optional `candidate_number` should be used for candidate names with unrelated digits.

```bash
python skills/problem-agnostic-optimization/scripts/record_progress.py \
  --progress work/optimization_harness/progress.tsv \
  --candidate cand_0002 \
  --metric cycles=2226 \
  --decision promote \
  --tokens-total 4500 \
  --tokens-delta 1400 \
  --wall-seconds 1080 \
  --label "dependency-list scheduled vector kernel"
```

```text
timestamp	candidate	cycles	decision	tokens_total	tokens_delta	wall_seconds	label
2026-06-01T00:00:00Z	0	147734	baseline	1200	1200	0	scalar starter baseline
2026-06-01T00:10:00Z	1	3360	promote	3100	1900	600	vectorized full gather, scratch values and paths
2026-06-01T00:18:00Z	2	2226	promote	4500	1400	1080	dependency-list scheduled vector kernel
```

### Candidate Result JSON

Use `<harness>/candidates/_template.result.json` when present. Keep this artifact for every measured candidate in substantial runs.

```json
{
  "schema_version": 1,
  "candidate": "cand_0002",
  "parent": "cand_0001",
  "parent_hash": null,
  "mode": "TUNE",
  "mechanism_class": "representation/primitive/route change",
  "duplicate_check": "not the same hill as cand_0001",
  "hypothesis": "one concrete hypothesis",
  "artifact_paths": ["candidates/cand_0002.py"],
  "raw_log_paths": ["work/optimization_harness/raw_logs/cand_0002.out"],
  "commands": {
    "apply_or_build": null,
    "correctness": null,
    "authoritative_metric": null,
    "regression_or_adversarial": null,
    "fresh_verifier": null
  },
  "correctness": null,
  "authoritative_metric": {
    "score": null,
    "unit": null,
    "direction": null,
    "raw_result_path": null
  },
  "escape": {
    "status": "tracking",
    "stuck_signal": null,
    "escape_operator": null,
    "hill_id": null,
    "feature_cell": null,
    "closed_hill": null,
    "divergence_probe": null,
    "new_hill": null,
    "mechanism_signal": "",
    "stepping_stone_signal": null,
    "commitment_budget": null,
    "controlled_regression_allowed": false,
    "anti_revisit_rule": null,
    "aspiration_rule": null,
    "operator_credit_signal": null,
    "kill_criterion": null
  },
  "promotion_ladder": {
    "apply_or_build": "pending",
    "correctness": "pending",
    "authoritative_metric": "pending",
    "regression_or_adversarial": "pending",
    "fresh_verifier": "pending",
    "promote": "pending"
  },
  "verifier": {
    "mode": "fresh_environment_when_possible",
    "verdict": null,
    "evidence": "",
    "limitations": []
  },
  "decision": "PENDING",
  "learning": ""
}
```

### `<harness>/review.md`

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

### `<harness>/dashboard.html`

Generate this from `<harness>/progress.tsv` for local, remote, or handoff review:

```bash
python skills/problem-agnostic-optimization/scripts/render_progress.py work/optimization_harness/progress.tsv \
  --chart-output work/optimization_harness/progress.svg \
  --dashboard-output work/optimization_harness/dashboard.html \
  --direction lower
```

For live remote review, run the dashboard server on the remote host with `--host 127.0.0.1 --port 8765`, then tunnel from your local machine:

```bash
ssh -L 8765:127.0.0.1:8765 <user>@<remote-host>
```

### `<harness>/audit.md`

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

### `<harness>/best.md`

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

### `<harness>/plan.md`

```markdown
# Active Plan

Target:
Current best:
Stagnation:
Harness mode: fast | standard | audit

## Active Branches

- B1:
  - hypothesis:
  - next probe:
  - expected signal:
  - budget:

## Critical Path

- correctness:
- authoritative metric:
- progress row:
- raw evidence path:
- decision:

## Sidecar Queue

- deferred artifacts:
- refresh command:
- next checkpoint:
- must not mutate:

## Frozen Branches

- 

## Escape Ladder

- Stuck signal:
- Escape operator:
- Divergence budget:
- Divergence probes:
- Basin memory:
- Diversity map:
- Operator credit:
- New-hill commitment:
- Controlled regression allowed:
- Anti-revisit rule:
- Aspiration rule:
- Kill criterion:

## Escalation Rule

If <condition>, stop tuning this route and run a local-optimum audit.
```
