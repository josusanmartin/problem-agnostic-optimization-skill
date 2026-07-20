---
name: problem-agnostic-optimization
description: "Use when improving a measured artifact under a correctness or scoring contract: performance, latency, throughput, leaderboard score, CPU/GPU kernel time, service load, fixed-resource schedules, or stochastic policy quality. Routes first to only the relevant challenge modules, then runs a lean evidence loop with protected-best promotion, measured-attempt accounting, and forced off-hill escapes. Logging and reporting are optional external concerns; when Scorebench is active, Scorebench owns them."
---

# Problem-Agnostic Optimization

Optimize the artifact. Keep process machinery and irrelevant domain guidance off the critical path.

## Route First

Route before planning candidates or opening any reference. The core rules in this file always apply. References are opt-in modules, not a reading list.

1. Classify the scored artifact and select exactly one primary route.
2. Select at most one matching kernel-shape module initially. Add another only when the artifact genuinely spans both shapes.
3. Add a cross-cutting module only when its trigger is present in current evidence.
4. State the selection once as `Route: <primary>; shape: <module or none>; add-ons: <modules or none>` in the active context, not a log file.
5. Do not read every reference, preload modules for possible future use, or follow references recursively. Return to this router when evidence changes the route.

### Primary Route

| Challenge signal | Load exactly this primary module |
|---|---|
| CUDA, HIP/ROCm, Triton, device kernel, GPU library path | `references/gpu-architecture.md` |
| CPU hot loop, SIMD, command benchmark, offline executable | `references/cpu-architecture.md` |
| HighLoad-style or production request service, network/load test | `references/service-throughput.md` |
| Simulator-scored policy, controller, agent, game bot, hidden seeds | `references/stochastic-policy-search.md` |
| VLIW, DSP, packet/instruction scheduler, fixed execution engines | `references/fixed-resource-scheduling.md` |
| Other measured artifact | No primary module; use the core until evidence selects one |

### Kernel-Shape Module

| Operation shape | Optional module |
|---|---|
| Elementwise or streaming transform | `references/kernel-elementwise.md` |
| Reduction, norm, loss, scan, prefix operation | `references/kernel-reductions-scans.md` |
| Pooling, stencil, or convolution | `references/kernel-stencils-convolution.md` |
| GEMM, GEMV, batched matrix composition | `references/kernel-matrix.md` |
| Histogram, atomic aggregation, sparse update | `references/kernel-histogram.md` |
| Quantized format, decode, or block scaling | `references/kernel-quantized.md` |
| Attention, MLA, MoE, paged KV, expert routing | `references/kernel-attention-moe.md` |

### Evidence-Triggered Add-ons

| Current trigger | Load only then |
|---|---|
| Uncertain metric, profiling, variance, platform blocker, technique intake | `references/evidence-loop.md` |
| Floor, tail, resource transfer, co-binder, plateau, or escape design | `references/resource-models.md` |
| Faster external artifact, multiple frontiers, stale negative verdict | `references/frontier-introspection.md` |
| Startup, allocation, JIT, graph, dispatch, I/O, or launch/setup dominates | `references/runtime-overhead.md` |

Keep routes isolated. A GPU kernel does not load CPU or service guidance unless measured host-side behavior becomes the bottleneck. A service does not load GPU guidance unless a GPU stage is actually in the scored path. HighLoad-specific advice belongs only to the service route.

## Contract

Before editing, establish the objective and authoritative metric, baseline, protected artifact, editable and immutable files, correctness gate, budget, target conditions, search-health thresholds, and multi-agent mode (`off` by default).

Use current workspace and user evidence by default. Mine sibling workspaces, old candidates, or prior submissions only for requested transfer or continuation.

Use `/goal` for substantial or long-running optimization. If asked for a goal "for later", return a copy-paste prompt beginning with `Use problem-agnostic-optimization.` and a filled `/goal` block; activate only when explicitly asked.

## Core Loop

1. Reproduce the baseline authoritatively.
2. Preserve the current best before risky edits.
3. Build the cheapest useful bottleneck model.
4. Choose one falsifiable mechanism and make the smallest candidate that faithfully tests it.
5. Prove the intended route executed.
6. Validate correctness before performance when possible.
7. Measure with the authoritative metric.
8. Decide `PROMOTE`, `KEEP VARIANT`, `REJECT`, `BUG`, or `BLOCKED`.
9. Update the model after a promotion or surprising result.
10. Count actual measured attempts and change hill when a search-health trigger fires.

For each candidate, retain only parent, mechanism family, hypothesis, expected signal, attempt budget, kill criterion, validation, measurement, and decision. Keep one compact active-state entry; no dossier by default.

One mechanism may require coordinated edits. Prefer the smallest faithful mechanism test, not the smallest textual diff. Ablate after a compound structural candidate shows authoritative signal.

## Gap And Promotion

Classify the gap as `proven floor`, `schedule`, `evidence`, or `statistical`. A plateau is not a floor proof. Use `proven lower bound` only when required-work counts, valid throughput assumptions, dependencies, and unavoidable costs establish it. Otherwise use `model floor` or `observed plateau` and keep structural alternatives open.

Only the authoritative metric promotes. Require valid output, the correctness gate, improvement outside noise, relevant target/shape/seed coverage, and contract validity. Reject wrong-answer speedups, leaked or hardcoded answers, stale-state wins, hidden-test detection, skipped required work, grader changes, and forbidden shortcuts.

## Search Health

Track the current mechanism family, actual measured attempts, same-family candidate misses, active contract budget since meaningful promotion, and whether the next candidate must be off-hill.

A measured attempt is each configuration, seed or draw, scheduler result, generated artifact, or authoritative evaluation used to choose or defend a family. A batch reports its total; wrapping thousands of evaluations in one candidate does not reset stagnation.

Same-artifact checkpoints, repeated verification, pings, token snapshots, and report refreshes are operational work, not optimization candidates or promotions. They do not reset the drought.

Unless the user sets different thresholds, trigger reassessment when any condition holds:

1. Three consecutive same-family measured candidates fail to improve the authoritative metric outside noise.
2. Ten percent of the active contract budget passes without a meaningful promotion.
3. A written sweep or family attempt budget is exhausted.

The user may override either direction when the contract justifies it. Set an attempt budget and stop rule before every sweep.

At the trigger, stop the sweep, mark the hill `CLOSED` or `NARROWED`, state the failed prediction in one sentence, name three different mechanism families, and spend the next measured candidate off-hill. Reopen the old family only with a new premise, not equivalent seeds or configurations. A meaningful promotion resets the drought.

## Optional Observability

Default behavior is no logging subsystem. Search-health accounting is active decision state, not a logging requirement. Keep it in the current plan or reasoning context.

When Scorebench is active, derive attempts, budget use, promotion history, and best state from Scorebench. Follow the `scorebench` skill for lifecycle, submissions, usage, history, logging, and reports. Do not create parallel PAO logs or dashboards, duplicate token accounting, or submit directly to the underlying venue.

If the user explicitly requests local persistence while Scorebench is inactive, use a separate sidecar module. Never run local and Scorebench logging in parallel.

## Multi-Agent And Finish

Enable multi-agent mode only when requested. Give each worker one isolated mechanism from a named parent; serialize promotion through correctness and the authoritative metric. After a plateau trigger, allocate at least one worker off-hill.

Report only the best artifact, authoritative result, validation status, and next blocker or direction by default. Produce a durable handoff, audit, dashboard, or detailed report only when requested or required by an external harness.
