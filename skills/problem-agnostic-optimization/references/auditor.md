# Auditor Mode

Use this reference when a second Codex session reviews an active optimization run while the first session continues working.

Auditor mode is read-mostly:

```text
Observe the run, verify progress integrity, identify drift, and write one audit report. Do not optimize.
```

## Start Prompt

```text
Use problem-agnostic-optimization in auditor mode.

Read the current run artifacts and write/update only work/audit.md.
Do not edit candidate code, harness files, work/best.md, work/log.md, work/plan.md, work/state.json, work/events.jsonl, or work/progress.tsv.
Do not launch new candidates, submissions, benchmarks, or long-running jobs unless I explicitly ask.

Audit whether the active optimization run is making valid progress under the recorded contract.
Check authoritative-metric promotion, correctness evidence, token/time burn, stagnation, blocker state, and whether the next planned candidate follows from the evidence.
```

## Inputs

Read these, if present:

- `work/best.md`
- `work/state.json`
- `work/events.jsonl`
- `work/progress.svg`
- `work/review.md`
- `work/log.md`
- `work/plan.md`
- raw result paths referenced by the ledger
- official problem statement, benchmark contract, or target dashboard

If `isolation.fresh_run` is true, do not inspect sibling workspaces, old submissions, prior run folders, cached solutions, or private notes unless they are listed in `isolation.allowed_prior_sources` or the user explicitly permits it.

## Audit Checks

Check the run against the recorded contract:

- Contract: objective, authoritative metric, validation, budget, editable files, immutable files, and isolation setting are explicit.
- Baseline: baseline was reproduced or marked `unknown, reproduce first`.
- Best protection: `work/best.md`, `work/state.json`, and the ledger agree on the current best.
- Promotion integrity: every promoted candidate is correct and promoted by the authoritative metric, not by a profile, local proxy, stale result, or wrong-answer speed.
- Ledger integrity: events are chronological, scores use the same direction/unit, failures are not encoded as fake zero-score wins, and token/time fields are monotonic when present.
- Chart/review freshness: `work/progress.svg` and `work/review.md` reflect the latest event when charting is enabled.
- Search health: recent candidates test one hypothesis each, mechanism classes are not repeating blindly, and closed hills are not being retried without a new premise.
- Reassessment triggers: token burn without improvement, rising bug/crash rate, repeated same-family rejects, mispredicted bottleneck model, exhausted budget, or stale pending jobs.
- Next action: the planned next candidate is justified by the bottleneck model, or the run should reassess/change hill.

## Verdict

Use one verdict:

- `ON TRACK`: progress and plan are coherent.
- `NEEDS REASSESSMENT`: run is still valid but should pause candidate generation and update the model/plan.
- `BLOCKED`: external dependency, budget, rate limit, missing data, or tooling prevents meaningful progress.
- `INVALIDATED`: current best or recent promotion violates correctness, metric, isolation, or integrity rules.
- `NEEDS USER DECISION`: multiple valid paths exist and the contract does not decide between them.

## `work/audit.md`

Write a compact report:

```markdown
# Optimization Audit

- Verdict:
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

Do not overwrite useful prior audit history. Append a new dated section if `work/audit.md` already exists.

## Escalation

Only interrupt the optimizer when the audit finds one of these:

- A promoted result appears invalid.
- The run is spending budget while blocked or outside the contract.
- The first session is editing immutable files or violating isolation.
- The same closed hill is being retried without new evidence.
- The chart, ledger, and best state disagree about the current best.
