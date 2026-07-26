---
name: problem-agnostic-optimization
description: "Use when optimizing a measured artifact under a correctness/scoring contract: latency, throughput, leaderboard score, CPU/GPU kernels, services, fixed-resource schedules, or stochastic policies. Route by scored-artifact semantics, load only triggered modules, protect authoritative bests, and escape plateaus. Logging is optional; active Scorebench owns it."
---

# Problem-Agnostic Optimization

Optimize the artifact; keep process machinery off the critical path.

## Route First

Use the first matching primary by scored-artifact semantics, not language, hardware, or venue. Select one primary; GPU adds one shape, or two only when the artifact spans both. Load only modules needed for the next decision and replace them when evidence changes. Do not read every reference, preload anticipated modules, or follow references recursively. Routing is internal unless ambiguity affects the work.

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

Do not accumulate routes. Keep services end-to-end; isolate CPU/GPU stages as child scopes.

## Contract

Fill only missing contract facts: objective/authority, baseline, protected artifact, editable scope, correctness gate, budget/targets, and multi-agent mode (`off` by default). Do not restate supplied facts or narrate setup. Transfer prior candidates only when requested; revalidate inherited conclusions.

Scope before floors: model the enforced contract and declared generalization, not an imagined superset or visible-test accident. A rejection closes only the observed form unless the contract forbids the mechanism. Never evade forbidden semantics; test only transparent contract-valid representations.

## Core Loop

1. Reproduce the authoritative baseline and protect the best.
2. Build the cheapest bottleneck model that can choose a candidate.
3. Test one falsifiable mechanism with the smallest faithful change.
4. Prove its path ran; reject through cheap faithful screens.
5. Run full correctness, then authority, on survivors and decide `PROMOTE`, `KEEP VARIANT`, `REJECT`, `BUG`, or `BLOCKED`.
6. Update the model after surprising evidence; count attempts and honor search-health triggers.

Retain parent, mechanism, prediction, budget/kill, result, and decision in one active-state entry.

One mechanism may span coordinated edits. Prefer the smallest faithful test, not the smallest diff; ablate compound candidates after authoritative signal. When only parameters or ordering are editable, begin bounded discovery. Otherwise start with structural changes until evidence assigns the gap to local tuning.

## Gap And Promotion

Classify the gap as `proven floor`, `schedule`, `evidence`, or `statistical`. A plateau is not a floor proof. Use `proven lower bound` only when required work, throughput, dependencies, and unavoidable costs establish it; otherwise use `model floor` or `observed plateau`.

Only authority promotes. Require correctness, improvement outside noise, coverage, and contract validity. Reject wrong or hardcoded answers, stale state, hidden-test detection, skipped work, grader changes, and forbidden shortcuts. Near ties favor simpler artifacts; keep target-specific variants separate. A `meaningful authoritative promotion` is a valid result outside noise that becomes a protected best.

## Search Health

Keep only the active hill, attempts, comparable-miss streak, budget, and next decision. A measured attempt is any configuration, draw, artifact, or evaluation used to choose a family; report a batch total once. A candidate miss is one valid comparable authoritative decision without improvement outside noise. Screen rejections, `BUG`, `BLOCKED`, invalid measurements, and unresolved noise consume budget but do not change the miss streak.

A search epoch opens only after the authoritative baseline and the first valid comparable candidate or planned sweep draw. It resets only on a meaningful authoritative promotion or a genuine hill change that changes the mechanism, not on renaming, another batch, or equivalent draws.

Unless the user sets different thresholds, reassess when any condition holds:

1. Three consecutive comparable same-family candidate decisions miss.
2. At least three measured attempts have occurred and ten percent of the active contract budget has been consumed in the open epoch without a meaningful authoritative promotion.
3. A written sweep or family attempt budget is exhausted.

Set an attempt budget and stop rule before a sweep or screening round. Samples count as attempts; the bounded outcome is one candidate-family decision.

At a trigger, load the plateau add-on. Continue the hill only for an explained bug with a faithful test left or a valuable predeclared bracket, under a narrower budget. Otherwise mark it `CLOSED` or `NARROWED` and spend the next measured candidate off-hill. Reopen only from a new evidence-backed premise.

## Optional Observability

Default behavior is no logging subsystem. Keep search health in active state; benchmark output, profiler captures, submitted artifacts, and required files are not optional logging.

Scorebench is active when the user invokes it, supplies a scoped run, or assigns the task through it. Derive attempts, budget use, promotions, and best state there; follow the `scorebench` skill for lifecycle and reporting. Do not mirror PAO logs, dashboards, or token accounting or submit directly to the venue.

If local persistence is requested without Scorebench, use a separate sidecar. Never run both. Logger failure is non-blocking unless logging is contractual.

## Multi-Agent And Finish

Enable multi-agent mode only when requested and load the `portfolio` add-on. The coordinator alone promotes; workers never replace the protected best directly.

When the user requests a substantial `/goal`, fill only missing fields. For a goal "for later", return a copy-paste prompt beginning with `Use problem-agnostic-optimization.` and do not activate it.

Report only the best artifact, authoritative result, validation, and next blocker or direction. Produce a durable handoff or detailed report only when requested or harness-required.
