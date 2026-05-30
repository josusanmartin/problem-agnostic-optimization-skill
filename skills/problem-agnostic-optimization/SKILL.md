---
name: problem-agnostic-optimization
description: Evidence-driven workflow for improving any measured program, CPU/GPU kernel, benchmark, leaderboard submission, stateful stochastic policy/controller, latency target, or throughput target. Use when Codex needs to optimize performance or policy quality while preserving correctness, set an ambitious objective from prompts, public references, leaderboards, or theoretical floors, diagnose bottlenecks, run controlled experiments, interpret profiler/counter/statistical evidence, handle noisy leaderboards, or produce a reusable handoff across CPU, CUDA, ROCm/HIP, Triton, library, randomized-policy, or challenge platforms.
---

# Problem-Agnostic Optimization

Operate as an optimization loop, not a brainstorming guide: set the objective, protect the best, run the code, measure the authoritative metric, promote only verified wins, and keep iterating until the target, budget, blocker, or plateau rule stops the run.

## Non-Negotiables

- Set the objective before optimizing.
- If the user gave a target, preserve it literally.
- If no target is given, look for public leaderboards, papers, repos, docs, or production references and set the goal at the best known result or slightly better.
- If no public reference exists, compute a theoretical lower bound or resource floor and set an ambitious goal at that floor or the nearest measurable threshold.
- Record objective source, target metric, hardware/system, and budget.
- Select mode early: `production` or `clean leaderboard`. Default to `production` for real products and `clean leaderboard` for challenges.
- Preserve the current best artifact before editing. Every candidate needs a parent, mechanism, rollback path, and result.
- Define the allowed edit surface. Reference, evaluation, harness, data, and scoring files are immutable unless the task explicitly asks to change them.
- Use the authoritative score as the promotion gate. Local benchmarks and counters explain results but do not replace the real scoreboard or production metric.
- If a runnable harness exists, run it before claiming performance progress. Do not rely on static reasoning for performance claims.
- If the score comes from stochastic simulations or hidden seeds, define the seed protocol and statistical promotion gate before tuning.
- Test one hypothesis at a time. Keep diffs surgical; every changed line should trace to the candidate hypothesis.
- Continue candidate loops when the user says to keep iterating. Stop only for target achieved, budget exhausted, external blocker, or plateau audit.
- Prefer the simplest winning change. If two candidates tie, keep the one with less complexity, less statefulness, and a smaller diff.
- Classify candidate mechanisms before trusting them: work deletion, resource transfer, dependency/tail reshaping, scheduler/variance, representation change, contract specialization, approximation, or forbidden shortcut.
- Never use exploit-like shortcuts. Do not implement, test, preserve, submit, or promote candidates that rely on wrong answers, leaked answers, stale state, hidden-harness bugs, invalid contracts, or grader weaknesses.

## First 5 Minutes

1. Set mode and objective.
   - Use the user's explicit target when present.
   - Otherwise search public references or leaderboards for the best known result.
   - If no public target exists, estimate the theoretical minimum from bytes, ops, launches, resource slots, or unavoidable latency.

2. Find the authoritative command.
   - Identify benchmark, submit, validation, test, or production measurement command.
   - If the official signal is remote-only, do not substitute a local benchmark as promotion proof.
   - If the metric is stochastic, identify local seed controls, simulation count, hidden/server seed behavior, and output variance.

3. Run or reproduce the baseline.
   - Run the current artifact when possible.
   - Save score, command, hardware, result ID, and noise notes.

4. Protect the best and define files.
   - Save or name the best artifact.
   - Mark editable files and immutable harness/reference/scoring files.

5. Pick artifact mode.
   - Minimal mode: for tiny one-shot tasks, keep only the best artifact plus command/result notes.
   - Harness mode: for multi-candidate, noisy, remote, budget-limited, or autonomous runs, create `work/best.md`, `work/log.md`, `work/plan.md`, and `work/state.json`; read `references/harness.md`.

## Control Loop

1. Build the contract: inputs, outputs, shapes, dtypes, layouts, seeds, tolerances, source limits, target hardware, budget, scoring formula, hidden/public differences, and edit surface.

2. Build the bottleneck model: split aggregate scores by case, classify the target family, compute resource floors or statistical floors when possible, profile or inspect traces/counters when the runtime is not explained, identify the primary bottleneck, and state what likely will not help.

3. Create one candidate: choose a hypothesis-rich filename, predict the expected metric/counter change, and make the smallest falsifiable edit. Prefer candidates that change a proven bottleneck floor, shorten an audited tail, or unlock a different primitive; avoid tweaks that merely move work into another saturated resource.

4. Validate and measure: correctness first unless the platform only exposes correctness through submit; then measure with the authoritative metric.

5. Decide:
   - `promote`: correct and improves the authoritative target.
   - `keep variant`: correct and useful for a lane, shape, GPU, or future splice.
   - `reject`: correct but slower, noisier, or worse on target.
   - `bug`: correctness failed; performance is not meaningful.
   - `blocked`: platform or tooling failed before evaluating user code.

6. Update the ledger and continue. After any promotion, recompute the bottleneck map before choosing the next candidate.

## Local-Optimum Escapes

- If the score gap is greater than about 2x, assume algorithm, representation, route, or contract-specialization issue before micro-tuning.
- If count or floor improves but runtime worsens, inspect dependencies, tail, scratch lifetime, barriers, aliasing, and resource pressure before discarding or composing.
- If a route repeatedly produces ties, separate "same graph, different schedule" from "lower-count graph that cannot schedule"; use the former for scheduler/variance only when the target gap is within reach, and use the latter to look for dependency or representation changes.
- Use negative audits to close seductive shortcuts: prove or find counterexamples for algebraic omissions, unobserved-state skips, branch/predicate substitutions, and contract specializations before investing in full implementations.
- If previous attempts in a family were about 2x slower or repeatedly tied/regressed, mark that family `CLOSED` until a new premise appears.
- Trigger a local-optimum audit after repeated parity/tie/regression, a lower-bound proof that the current family cannot hit target, or repeated failures of the same knob family.
- The audit must name the current hill, why it is exhausted, at least three different hills, and the cheapest off-hill probe. Spend the next candidate off-hill by default.

## Mode Rules

- `production`: correctness, maintainability, observability, and stable p95/p99 beat benchmark-only tricks.
- `clean leaderboard`: benchmark-contract specialization is allowed only when the public contract proves it; never use wrong-answer speed, stale state, leaked answers, or hidden-harness bugs as clean wins.

## Reference Map

- Read `references/evidence-loop.md` for measurement integrity, objective evidence, logging, promotion gates, variance, and platform-blocker handling.
- Read `references/harness.md` for persistent multi-candidate runs, fixed budgets, autonomous loops, crash handling, git-backed keep/discard, and result tables.
- Read `references/stochastic-policy-search.md` for `stateful-stochastic-policy` targets: simulation-scored policies, controllers, agents, schedulers, hidden seeds, scenario sets, parameter search, regime analysis, and statistical promotion gates.
- Read `references/resource-models.md` for theoretical floors, schedule-versus-op-graph diagnosis, tail audits, local-optimum audits, cheap pre-screen models, and composed resource trades.
- Read `references/problem-families.md` for target-family playbooks: stateful stochastic policy/controller, elementwise, reduction, scan, pooling/stencil, GEMM/library, histogram/atomic, quantized, attention/MoE, runtime/system, and scheduler problems.
- Read `references/gpu-architecture.md` for architecture-agnostic CUDA/ROCm/HIP/Triton tactics, device discovery, profiling, cross-GPU transfer checks, and attention/decode lessons.
- Read `references/cpu-architecture.md` for architecture-agnostic CPU tactics across single-shot process benchmarks, service/load benchmarks, startup overhead, SIMD, memory-level parallelism, counters, and low-level artifact transfer.
- Read `references/templates.md` when creating logs, reports, or handoffs.

## Integrity Boundary

Before promoting, ask: does this compute the required output for all valid inputs under the stated contract; did it pass the required correctness scope; is the speedup outside noise; is the objective evidence current; and would the method remain valid if input order, warmup count, or hidden cases changed within the contract?

When the answer is uncertain, keep the candidate separate and report the risk.
