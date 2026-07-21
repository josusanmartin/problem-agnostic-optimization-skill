---
name: problem-agnostic-optimization
description: "Use when improving a measured artifact under a correctness or scoring contract: performance, latency, throughput, leaderboard score, CPU/GPU kernel time, service load, fixed-resource schedules, or stochastic policy quality. Route by scored-artifact semantics, load only relevant modules, then run a lean evidence loop with protected-best promotion and bounded plateau escapes. Logging and reporting are optional; when Scorebench is active, Scorebench owns them."
---

# Problem-Agnostic Optimization

Optimize the artifact. Keep process machinery and irrelevant domain guidance off the critical path.

## Route First

Route before planning. The core always applies; references are opt-in.

1. Use the first matching primary row. Scored-artifact semantics outrank language, hardware, or venue branding.
2. Select one primary route. GPU adds one shape module; add a second only if the artifact spans both shapes.
3. Add modules only on a current trigger, then state `Route: <primary>; shape: <module or none>; add-ons: <modules or none>` once.
4. Do not read every reference, preload modules, or follow references recursively.

### Primary Route

| Route id | First matching scored-artifact semantics | Load exactly this primary module |
|---|---|---|
| `policy` | Policy/controller action quality over stochastic, hidden, or adversarial scenarios, even when implemented on CPU/GPU | `references/stochastic-policy-search.md` |
| `service` | Live request/response, network, or queue service under concurrent load | `references/service-throughput.md` |
| `fixed-resource` | Cycle count of a generated schedule, packet placement, or packing quality on fixed engines such as VLIW, DSP, or custom accelerators | `references/fixed-resource-scheduling.md` |
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
| `measurement` | Metric or profiling-protocol uncertainty, weak or unavailable profiling, or platform blocker | `references/evidence-loop.md` |
| `variance` | Noisy samples, stochastic comparison, selector/draw search, or planned best-of-N sweep | `references/variance-and-sweeps.md` |
| `technique` | Public-method intake, breakthrough mining, or cheap-screen calibration | `references/technique-intake.md` |
| `resource` | Resource floor, tail, transfer, primitive inversion, or co-binder analysis | `references/resource-models.md` |
| `plateau` | Search-health trigger, local-optimum audit, or off-hill escape design | `references/plateau-escape.md` |
| `frontier` | Faster external artifact, multiple frontiers, or stale negative verdict | `references/frontier-introspection.md` |
| `runtime` | Startup, allocation, JIT, dispatch, I/O, launch, or setup dominates | `references/runtime-overhead.md` |
| `portfolio` | Multi-agent mode with parallel mechanism families, independent/adversarial review, or worker reallocation | `references/multi-agent-portfolio.md` |

Replace stale modules when the bottleneck changes; do not accumulate routes. Keep services end-to-end; isolate CPU/GPU stages as child scopes.

## Contract

Before editing, establish objective and authority, baseline, protected artifact, editable scope, correctness gate, budget, targets, and multi-agent mode (`off` by default).

Use current evidence. Transfer sibling or prior candidates only when requested; revalidate inherited gap labels and closed hills.

Scope before floors: model the enforced contract and declared generalization, not an imagined superset or visible-test accident. A rejection closes only the observed form unless the contract forbids the mechanism. Never evade forbidden semantics; test only transparent contract-valid representations.

Use `/goal` when the user requests a substantial run. For a goal "for later", return a copy-paste prompt beginning with `Use problem-agnostic-optimization.` and a filled `/goal` block; activate only when explicitly asked.

## Core Loop

1. Reproduce the baseline authoritatively.
2. Preserve the current best before risky edits.
3. Build the cheapest useful bottleneck model for the enforced domain.
4. Choose one falsifiable mechanism; make the smallest faithful candidate.
5. Prove the intended path executed before interpreting correctness or timing.
6. Reject with the cheapest faithful screen available.
7. Run full correctness, then authoritative measurement, on survivors.
8. Decide `PROMOTE`, `KEEP VARIANT`, `REJECT`, `BUG`, or `BLOCKED`.
9. Update the model after a promotion or surprising result.
10. Count actual measured attempts and reassess when a search-health trigger fires.

Retain parent, mechanism, prediction, budget/kill, result, and decision in one active-state entry.

One mechanism may require coordinated edits. Prefer the smallest faithful test, not the smallest diff. Ablate compound candidates after authoritative signal.

Structure before local tuning: prefer changes to required work, representation, algorithm, dependencies, or policy logic until evidence says parameters or ordering own the gap.

Screen many, gate few: cheap faithful screens may reject; full correctness and authority gate every promotion.

## Gap And Promotion

Classify the gap as `proven floor`, `schedule`, `evidence`, or `statistical`. A plateau is not a floor proof. Say `proven lower bound` only when required work, throughput, dependencies, and unavoidable costs establish it; otherwise use `model floor` or `observed plateau`.

Only authority promotes. Require correctness, improvement outside noise, required coverage, and contract validity. Reject wrong answers, leaked or hardcoded answers, stale state, hidden-test detection, skipped work, grader changes, and forbidden shortcuts.

Near ties favor simpler, smaller, less stateful artifacts. Keep target-specific variants separate. A `meaningful authoritative promotion` is a contract-valid result outside noise that becomes a protected global or target-specific best.

## Search Health

Track only the active hill, attempts, comparable misses, budget use, and next decision.

A measured attempt is any configuration, draw, artifact, or evaluation used to choose a family. A batch reports its total once. A candidate miss is one valid, comparable authoritative decision that fails to improve outside noise. Screen rejections, `BUG`, `BLOCKED`, invalid measurements, and unresolved noise consume attempts and budget but do not increment or reset the miss streak.

A search epoch opens only after the authoritative baseline and the first valid comparable candidate or planned sweep draw. It resets only on a meaningful authoritative promotion or a genuine hill change that changes the mechanism, not on renaming, another batch, or equivalent draws.

Unless the user sets different thresholds, reassess when any condition holds:

1. Three consecutive comparable same-family candidate decisions miss.
2. At least three measured attempts have occurred and ten percent of the active contract budget has been consumed in the open epoch without a meaningful authoritative promotion.
3. A written sweep or family attempt budget is exhausted.

Set an attempt budget and stop rule before every sweep or screening round. Samples count as attempts, while the bounded sweep outcome is one candidate-family decision.

At a trigger, load the plateau add-on. Continue only when an explained implementation bug leaves a faithful test untried or a predeclared bracket remains valuable; narrow its budget. Otherwise mark the hill `CLOSED` or `NARROWED`, state the failed prediction, and spend the next measured candidate off-hill by default. Reopen only from a new evidence-backed premise.

## Optional Observability

Default behavior is no logging subsystem. Keep search health in active state. Normal benchmark output, profiler captures, submitted artifacts, and contract-required files are not optional logging.

Scorebench is active when the user invokes it, supplies a scoped run, or assigns the task through it. Derive attempts, budget use, promotions, and best state there; follow the `scorebench` skill for lifecycle and reporting. Do not mirror PAO logs, dashboards, or token accounting or submit directly to the venue.

If the user requests local persistence while Scorebench is inactive, use a separate sidecar. Never run it beside Scorebench. A logger failure must not block optimization unless logging is contractual.

## Multi-Agent And Finish

Enable multi-agent mode only when requested and load the `portfolio` add-on. The coordinator alone promotes; workers never replace the protected best directly.

Report only the best artifact, authoritative result, validation, and next blocker or direction. Produce a durable handoff or detailed report only when requested or harness-required.
