---
name: problem-agnostic-optimization
description: "Use when improving a measured artifact under a correctness or scoring contract: performance, latency, throughput, leaderboard score, CPU/GPU kernel time, service load, fixed-resource schedules, or stochastic policy quality. Route by scored-artifact semantics, load only relevant modules, then run a lean evidence loop with protected-best promotion and bounded plateau escapes. Logging and reporting are optional; when Scorebench is active, Scorebench owns them."
---

# Problem-Agnostic Optimization

Optimize the artifact. Keep process machinery and irrelevant domain guidance off the critical path.

## Route First

Route before planning candidates or opening references. This core always applies; references are opt-in modules, not a reading list.

1. Use the first matching primary row for what the scorer rewards. Scored-artifact semantics outrank language, hardware, or venue branding.
2. Select exactly one primary route. Only a GPU route gets a shape module: one initially, another only if the artifact spans both shapes.
3. Add a cross-cutting module only when current evidence matches its trigger.
4. State `Route: <primary>; shape: <module or none>; add-ons: <modules or none>` once in active context.
5. Do not read every reference, preload possible modules, or follow references recursively.

### Primary Route

| Route id | First matching scored-artifact semantics | Load exactly this primary module |
|---|---|---|
| `policy` | Policy/controller action quality over stochastic, hidden, or adversarial scenarios, even when implemented on CPU/GPU | `references/stochastic-policy-search.md` |
| `service` | Live request/response, network, or queue service under concurrent load | `references/service-throughput.md` |
| `fixed-resource` | Schedule, cycle count, packet placement, or packing quality on fixed execution engines | `references/fixed-resource-scheduling.md` |
| `gpu` | GPU kernel or GPU library route whose device work is the scored artifact | `references/gpu-architecture.md` |
| `cpu` | Offline executable, command benchmark, CPU kernel, SIMD path, or CPU hot loop | `references/cpu-architecture.md` |
| `other` | Other measured artifact | No primary module; use the core until evidence selects one |

### GPU Kernel Shape

Use this table only with the `gpu` primary route.

| Shape id | Operation shape | Optional module |
|---|---|---|
| `elementwise` | Elementwise or streaming transform | `references/kernel-elementwise.md` |
| `reduction-scan` | Reduction, norm, loss, scan, or prefix operation | `references/kernel-reductions-scans.md` |
| `stencil-convolution` | Pooling, stencil, or convolution | `references/kernel-stencils-convolution.md` |
| `matrix` | GEMM, GEMV, or batched matrix composition | `references/kernel-matrix.md` |
| `histogram` | Histogram, atomic aggregation, or sparse update | `references/kernel-histogram.md` |
| `quantized` | Quantized format, decode, or block scaling | `references/kernel-quantized.md` |
| `attention-moe` | Attention, MLA, MoE, paged KV, or expert routing | `references/kernel-attention-moe.md` |

### Evidence-Triggered Add-ons

| Add-on id | Current evidence trigger | Load only then |
|---|---|---|
| `measurement` | Metric uncertainty, profiling need, weak evidence, or platform blocker | `references/evidence-loop.md` |
| `variance` | Noisy samples, stochastic comparison, selector/draw search, or planned best-of-N sweep | `references/variance-and-sweeps.md` |
| `technique` | Public-method intake, breakthrough mining, or cheap-screen calibration | `references/technique-intake.md` |
| `resource` | Resource floor, tail, transfer, primitive inversion, or co-binder analysis | `references/resource-models.md` |
| `plateau` | Search-health trigger, local-optimum audit, or off-hill escape design | `references/plateau-escape.md` |
| `frontier` | Faster external artifact, multiple frontiers, or stale negative verdict | `references/frontier-introspection.md` |
| `runtime` | Startup, allocation, JIT, dispatch, I/O, launch, or setup dominates | `references/runtime-overhead.md` |
| `portfolio` | Multi-agent mode with parallel mechanism families, adversarial review, or worker reallocation | `references/multi-agent-portfolio.md` |

When the bottleneck changes, replace obsolete primary/shape modules and remove stale add-ons. Do not accumulate routes. Keep an end-to-end service on the service route; route an isolated GPU/CPU stage as a child scope.

## Contract

Before editing, establish objective and authority, baseline, protected artifact, editable/immutable files, correctness gate, budget, target conditions, search-health thresholds, and multi-agent mode (`off` by default).

Use current workspace and user evidence. Mine sibling workspaces or prior candidates only for requested transfer. Treat inherited gap labels and closed hills as hypotheses until current evidence supports them.

Separate contract semantics, observed enforcement, and the rejected representation. A scanner or sandbox rejection closes only the observed form unless the contract forbids the mechanism. Never evade forbidden semantics; when semantics are allowed, test only transparent contract-valid representations.

Use `/goal` for substantial or long-running work. If asked for a goal "for later", return a copy-paste prompt beginning with `Use problem-agnostic-optimization.` and a filled `/goal` block; activate only when explicitly asked.

## Core Loop

1. Reproduce the baseline authoritatively.
2. Preserve the current best before risky edits.
3. Build the cheapest useful bottleneck model.
4. Choose one falsifiable mechanism and make the smallest candidate that faithfully tests it.
5. Prove the intended candidate path executed before interpreting correctness or timing.
6. Validate correctness before performance when possible.
7. Measure with the authoritative metric.
8. Decide `PROMOTE`, `KEEP VARIANT`, `REJECT`, `BUG`, or `BLOCKED`.
9. Update the model after a promotion or surprising result.
10. Count actual measured attempts and reassess when a search-health trigger fires.

Retain only parent, mechanism family, hypothesis, expected signal, budget/kill, validation, measurement, and decision in one compact active-state entry.

One mechanism may require coordinated edits. Prefer the smallest faithful mechanism test, not the smallest textual diff. Ablate after a compound structural candidate shows authoritative signal.

## Gap And Promotion

Classify the gap as `proven floor`, `schedule`, `evidence`, or `statistical`. A plateau is not a floor proof. Use `proven lower bound` only when required-work counts, valid throughput, dependencies, and unavoidable costs establish it; otherwise use `model floor` or `observed plateau`.

Only the authoritative metric promotes. Require valid output, correctness, improvement outside noise, relevant target/shape/seed coverage, and contract validity. Reject wrong-answer speedups, leaked or hardcoded answers, stale-state wins, hidden-test detection, skipped required work, grader changes, and forbidden shortcuts.

Near ties favor the simpler, smaller, less stateful artifact. Keep target-specific variants separate when a candidate wins only one lane, shape, seed regime, or hardware target. A `meaningful authoritative promotion` is a contract-valid result outside noise that becomes the protected best or a separately retained target-specific best.

## Search Health

Track the active hill and mechanism family, measured attempts, consecutive comparable misses, epoch budget use, and whether the next candidate should be off-hill.

A measured attempt is each configuration, seed/draw, scheduler result, generated artifact, or authoritative evaluation used to choose or defend a family. A batch reports its total. A candidate miss is one valid, comparable authoritative decision that fails to improve outside noise. `BUG`, `BLOCKED`, invalid measurements, and unresolved in-noise results consume attempts and budget but do not increment or reset the miss streak.

A search epoch opens only after the authoritative baseline and the first valid comparable candidate or planned sweep draw on a hill. It resets on a meaningful authoritative promotion or an explicit hill change that changes the mechanism, not on renaming, another batch, or equivalent seeds/configurations.

Unless the user sets different thresholds, reassess when any condition holds:

1. Three consecutive comparable same-family candidate decisions miss.
2. Ten percent of the active contract budget is consumed in the open epoch without a meaningful authoritative promotion.
3. A written sweep or family attempt budget is exhausted.

Set an attempt budget and stop rule before every sweep. Samples count as attempts, while the bounded sweep outcome is one candidate-family decision.

At a trigger, stop and load the plateau add-on through the router. Continue the hill only when an explained implementation bug leaves a faithful test untried or a predeclared bracket remains plausibly valuable; state the reason and narrow its budget. Otherwise mark the hill `CLOSED` or `NARROWED`, state the failed prediction, name three different mechanism families, and spend the next measured candidate off-hill by default. Reopen only with a new premise supported by current evidence.

## Optional Observability

Default behavior is no logging subsystem. Search-health accounting is active decision state, not a logging requirement. Normal benchmark output, profiler captures, submitted artifacts, and files required by the target contract are not optional logging.

Scorebench is active when the user invokes it, supplies a scoped Scorebench run, or assigns the task through Scorebench. Then derive attempts, budget use, promotion history, and best state from Scorebench; follow the `scorebench` skill for lifecycle, submissions, usage, history, logging, and reports. Do not create parallel PAO logs or dashboards, duplicate token accounting, or submit directly to the underlying venue.

If the user explicitly requests local persistence while Scorebench is inactive, use a separate sidecar module. Never run local and Scorebench logging in parallel. A logger or renderer failure must not block optimization unless logging is part of the contract.

## Multi-Agent And Finish

Enable multi-agent mode only when requested; then load the `portfolio` add-on. The coordinator alone promotes through correctness and authority; workers never replace the protected best directly.

Report only the best artifact, authoritative result, validation status, and next blocker or direction by default. Produce a durable handoff, audit, dashboard, or detailed report only when requested or required by an external harness.
