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
