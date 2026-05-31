---
name: problem-agnostic-optimization
description: "Use when improving a measured artifact under a correctness or scoring contract: performance, latency, throughput, leaderboard score, GPU/CPU kernel time, or stochastic policy quality. Runs an evidence loop: define objective, reproduce baseline, protect best artifact, model the bottleneck, test one hypothesis at a time, promote only authoritative wins, and escape local optima by changing representation, primitive, route, or specialization level."
---

# Problem-Agnostic Optimization

Use this skill as a measured search loop:

```text
contract -> baseline -> bottleneck model -> candidate -> validate/measure -> decide -> iterate or escape
```

Only the authoritative metric promotes. Everything else explains.

## Core Laws

1. The authoritative metric promotes; profiles, counters, local benchmarks, and static models only explain.
2. Correctness comes before speed unless the platform only exposes correctness through submit.
3. Preserve the current best artifact before editing.
4. Define editable and immutable files before the first candidate.
5. Test one hypothesis per candidate; keep the diff surgical.
6. Classify the mechanism before trusting the result.
7. When repeated same-family candidates tie or regress, stop tuning and change hill.
8. Never use wrong answers, leaked answers, stale state, hidden-harness bugs, invalid contracts, grader edits, or harness manipulation as optimization wins.

## Entry Protocol

Record before changing code:

- Objective and target.
- Mode: `production` or `clean leaderboard`.
- Authoritative metric and command, submit path, dashboard, or scorer.
- Baseline artifact, score, command, hardware/system, and result ID.
- Reproduce or establish the baseline before the first candidate; if unknown, mark it `unknown, reproduce first`.
- Editable files and immutable reference, harness, scoring, data, and contract files.
- Budget and stopping rule.
- Validation method.
- Profiling, counter, trace, statistical, or static evidence available.

If no target is given, find a public best, prior local best, paper result, production SLO, or theoretical/resource floor. If none is available, set an ambitious measurable floor and label the uncertainty.

Use minimal mode for small one-shot tasks: keep the best artifact plus command/result notes. Use harness mode for multi-candidate, noisy, remote, budget-limited, or autonomous runs: create `work/best.md`, `work/log.md`, `work/plan.md`, and `work/state.json`; read `references/harness.md`.

## Bottleneck Model

Before choosing a candidate, explain the gap:

- Case split: which shapes, seeds, workloads, regimes, or scenarios matter.
- Resource or statistical floor: unavoidable bytes, ops, launches, latency, variance, or sample budget.
- Profile/counter confidence: `strong`, `medium`, `weak`, or `none`.
- Tail and dependency risk: synchronization, allocation, scratch lifetime, aliasing, serialization, finalization, cold start, or variance tail.
- What likely will not help.
- Cheapest falsifiable probe.

Classify the current gap:

- `floor gap`: the current operation graph or policy family cannot reach target even with perfect scheduling.
- `schedule gap`: the graph can reach target, but runtime is lost to packing, dependencies, tail, allocation, synchronization, resource pressure, or variance.
- `evidence gap`: profiling, counters, logs, traces, or statistics are too weak; run a cheap model or ablation first.
- `statistical gap`: the apparent delta may be noise; use matched scenarios, repeated runs, SEM/tails, or a stricter promotion gate.

Do not micro-tune when the target is below the current floor. Move to work deletion, fusion, specialization, representation change, primitive change, route change, or valid approximation inside tolerance.

## Candidate Protocol

For each candidate, state:

- Parent best.
- Hypothesis.
- Mechanism class.
- Expected signal.
- Kill criterion.
- Smallest edit that can falsify the hypothesis.

Mechanism classes:

- Work deletion.
- Resource transfer.
- Tail/dependency reshaping.
- Scheduler/variance.
- Representation change.
- Primitive change.
- Route/library/config change.
- Contract specialization.
- Approximation inside tolerance.
- Forbidden shortcut.

Validate correctness first when possible, then measure with the authoritative metric. If the authoritative signal is unavailable, use a clearly labeled screening metric and do not promote from it.

Decide:

- `PROMOTE`: correct and improves the authoritative target outside the required noise or stability gate.
- `KEEP VARIANT`: correct and useful for one lane, shape, hardware, seed regime, or future composition.
- `REJECT`: correct but worse, noisier, too complex, or aimed at the wrong bottleneck.
- `BUG`: correctness failed; performance is not meaningful.
- `BLOCKED`: the platform or tooling failed before evaluating the candidate cleanly.

Near ties favor the simpler, smaller, less stateful artifact.

Log the result and learning. After a promotion or surprising regression, update the bottleneck model before choosing the next candidate.

## Plateau And Escape Protocol

Trigger a local-optimum audit after repeated parity, ties, regressions, same-knob failures, or a lower-bound proof that the current family cannot hit target.

The audit must name:

- Current hill.
- Why it looked promising.
- Plateau evidence.
- Floor, tail, dependency, or statistical blocker.
- At least three different hills.
- Cheapest off-hill probe.

After repeated same-family failures, spend the next candidate off-hill by default.

Official hill changes:

- Change representation.
- Change route, library, configuration, or target split.
- Invert the primitive: replace a compact toxic primitive with a decomposed version when the compact form is microcoded, serialized, frontend-heavy, or target-hostile.
- Specialize the contract when the public or production contract proves the restriction.
- Run a negative audit: prove or find a counterexample for a seductive shortcut before investing in it. A failed proof can be a successful experiment.

## Mode And Integrity

- `production`: correctness, maintainability, observability, rollback safety, and stable p95/p99 beat benchmark-only tricks.
- `clean leaderboard`: benchmark-contract specialization is allowed only when the public contract proves it; never use wrong-answer speed, stale state, leaked answers, hidden-harness bugs, or grader changes as clean wins.

Before promoting, ask: does this compute the required output for all valid inputs under the stated contract; did it pass the required correctness scope; is the speedup outside noise; is the objective evidence current; and would the method remain valid if input order, warmup count, seed, hardware, or hidden cases changed within the contract?

When the answer is uncertain, keep the candidate separate and report the risk.

## Reference Routing

- Read `references/harness.md` for persistent long/noisy/remote/multi-candidate runs, fixed budgets, crash handling, git-backed keep/discard, and result tables.
- Read `references/resource-models.md` for resource floors, floor-versus-runtime diagnosis, schedule-versus-op-graph gaps, tail audits, primitive inversion, negative audits, and local-optimum audits.
- Read `references/evidence-loop.md` for measurement integrity, objective evidence, profiling confidence, variance, promotion gates, and platform-blocker handling.
- Read `references/stochastic-policy-search.md` only for policy, controller, simulator, hidden-seed, scenario-set, or randomized-search targets.
- Read `references/gpu-architecture.md` for GPU-specific probes and traps across CUDA, ROCm/HIP, Triton, device discovery, profiling, and cross-GPU transfer checks.
- Read `references/cpu-architecture.md` for CPU-specific probes and traps across startup overhead, SIMD, memory-level parallelism, counters, service/load benchmarks, and low-level artifact transfer.
- Read `references/problem-families.md` for target-family playbooks.
- Read `references/templates.md` when creating logs, reports, ledgers, audits, or handoffs.
