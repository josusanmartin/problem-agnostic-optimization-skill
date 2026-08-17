# Measurement And Evidence

Use this reference when the metric or profiling protocol is uncertain, profiling is weak or unavailable, or a platform blocker may invalidate measurements.

## Resolve The Next Uncertainty

Clarify only what can change the next experiment:

- Authoritative metric, aggregation, target scope, noise semantics, and timed lifecycle.
- Comparable artifact, inputs/seeds, build mode, hardware, warmup, and route.
- Whether a profile observes the same path and workload as the scorer.
- Platform limits that can fail before candidate code runs.

Split aggregate scores only when a case or lane can choose a different candidate. If draws or selectors matter, load the `variance` add-on through the router.

When production generalization is contractual, keep robustness guardrails untimed and pass/fail. Before promotion, run one representative downstream workload covering route preconditions, non-finite inputs, data-derived index bounds, repeated/interleaved calls, and memory sanitization when relevant.

## Use Evidence By Role

The authority promotes; profiles, counters, models, and local benchmarks diagnose.

- `strong`: target-system profile, trace, counters, or per-case timing on the scored path.
- `medium`: similar-system or component evidence with a known transfer gap.
- `weak`: static floors, synthetic microbenchmarks, surrogate workloads, or another architecture.
- `none`: controlled candidate comparisons and case decomposition only.

Use the strongest honest source. Keep the artifact, workload, hardware, warmup, and lifecycle comparable. Record a profiler command or output path only when it is needed to reproduce the next decision or an external harness requires it.

Profile when the bottleneck is unknown, evidence contradicts the result, a lower-floor candidate regresses, or a promotion moves the bottleneck. Start with low-overhead counters; escalate to traces only for path, tail, launch, lock, allocation, or stall questions. Stop profiling when it yields no falsifiable candidate.

## Work Without A Profiler

Choose the cheapest discriminating fallback:

- Required work, bytes, launches, syscalls, allocations, critical path, or resource floor.
- Per-shape, size, scenario, warm/cold, or tail split.
- One controlled ablation.
- Compiler output, occupancy estimate, query plan, or other static model.
- Differential timing under identical conditions.
- Attested prefix, suffix, or stage cut for diagnosis only.

Never promote a stage cut or sum incompatible cuts into an end-to-end claim.

## Downgrade Bad Screens

Weak evidence chooses candidates; it does not prove a bottleneck or floor. If a screen repeatedly mispredicts authority, downgrade it. A downgraded screen cannot veto a candidate because false negatives can hide real wins. When no local screen predicts authority, spend a bounded authoritative-evaluation budget directly.

Only a valid lower-bound proof establishes a `proven lower bound`. Otherwise retain `model floor` or `best known so far`.

## Stop On Platform Blockers

Treat a failure as platform/tooling when it occurs before user code, the reference result is corrupt or unavailable, required support is absent, the endpoint returns no job ID, or external capacity prevents execution.

Do not repeat unchanged submissions. Retain the exact error in active context or the external harness and resume only after the platform changes or a credible recovery appears.
