# Measurement And Evidence

Use this reference when the metric or profiling protocol is uncertain, profiling evidence is weak or unavailable, or a platform blocker may invalidate measurements.

## Contents

- Measurement boundaries and evidence hierarchy
- Profiling workflow and evidence strength
- Weak-evidence fallbacks and floor discipline
- Platform blockers

## Clarify The Measurement

Resolve only uncertainties that change the next experiment:

- Exact authoritative metric, aggregation, target scope, and noise or draw semantics.
- Comparable artifact, inputs, seeds, build mode, hardware, warmup, and timed lifecycle boundary.
- Whether profiles and counters observe the same route and workload as the scorer.
- Platform limits that can invalidate the measurement before candidate code runs.

If the score is aggregate, split it. A geomean hides shape-specific bottlenecks.
If repeated draws or selectors might help, load the `variance` add-on through the router.

## Measurement Hierarchy

The authoritative metric promotes; profiles and counters diagnose:

- Leaderboard/ranked submit beats local benchmark.
- Production p95 beats synthetic microbench.
- End-to-end model score beats isolated component timing.
- Public accepted/benchmarked state beats failed-state runtime fields.

- If counters improve and time worsens, the wrong resource was optimized or a new pressure was introduced.
- Distinguish a real graph improvement from a placement improvement: slot counts, bytes, launches, or branch counts changing means a different operation graph; identical counts with better time is scheduler, packing, or tail behavior.

## Profiling Workflow

Profile when:

- The baseline bottleneck is unknown.
- Runtime disagrees with static floors, operation counts, or expected counter movement.
- A lower-floor candidate runs slower.
- A tail, memory, allocation, synchronization, compile/codegen, launch, lock, or scheduler issue is suspected.
- A promoted win changes the bottleneck map.

Profile with integrity:

- Use the same artifact, inputs, seeds, build mode, hardware, warmup, and budget as the comparable benchmark.
- Prefer low-overhead counters first; use traces, flamegraphs, or timelines when the question is call path, tail, launch, lock, allocation, or stall source.
- Record profiler command, tool version when relevant, run ID or output path, and the specific interpretation.
- Treat profiler overhead, missing symbols, sampling bias, JIT/warmup, and client-side bottlenecks as possible artifacts.
- Do not promote from profiler data alone; the authoritative metric still decides.

Turn profiles into candidate hypotheses:

- Name the suspected bottleneck and evidence.
- Predict which counter, frame, kernel, block, engine, or tail should move.
- If the profile does not identify an actionable limiter, stop profiling and change the model or question.

## Profiling Ladder

Profiling is how the search chooses better hypotheses. It is not required for every platform, and it should be used at the strongest level the environment honestly provides.

Evidence strength:

- `strong`: authoritative target-system profile, hardware counters, trace, per-case timing, or flamegraph for the same artifact and workload being scored.
- `medium`: local profile on similar hardware, public competitor counters, component-level profiler output, sampled production trace, or target-system aggregate counters without source visibility.
- `weak`: static throughput model, instruction/resource count, synthetic microbenchmark, local surrogate workload, or profiler from a different architecture.
- `none`: no profiler or counter data; rely on controlled experiments, resource floors, and case decomposition.

Use the strongest available layer:

1. Profile the baseline or current best before broad tuning when profiler access is available.
2. Compare profiles between baseline, current best, near misses, and public/production references when available.
3. Identify what improved, what regressed, and what did not matter. A profile is often most valuable when it rules out a tempting knob.
4. Translate profiler observations into falsifiable candidate hypotheses: "reduce backend load pressure", "lower branch misses", "shorten tail dependency", "shift port pressure", "remove allocation churn".
5. Re-profile after a promotion or surprising regression, because the bottleneck can move.

Record unavailable profiling explicitly. "No target profiler", "private profile", "no GPU trace access", or "local CPU differs from target" is useful state, not a footnote.

## When Profiling Is Weak Or Unavailable

Do not stop optimizing just because a profiler is missing. Replace it with lower-confidence evidence and label it as such.

Fallback tools:

- Resource floors: bytes moved, operations, launches, syscalls, allocations, critical path, memory footprint, network round trips, or scheduler slots.
- Case splits: per-shape, per-input-size, per-scenario, per-token, per-request, warm/cold, and tail-percentile timing.
- Controlled ablations: remove one feature, disable one branch, change one tile, one prefetch distance, one batch size, one cache, or one route.
- Static models: compiler output, instruction mix, occupancy estimates, `llvm-mca`, roofline-style math, kernel launch count, or query plans.
- Surrogate profiles: local `perf`, language profilers, flamegraphs, tracing logs, simulator output, or a smaller reproducible workload.
- Differential timing: compare parent and candidate under identical commands, seeds, input order, and warmup protocol.
- Stage-cut diagnostics: run an attested prefix, controlled suffix replacement, or phase-only route to estimate ownership when the full profiler is unavailable.

Fallback discipline:

- Promote only by the authoritative metric, even if a weak profiler says the candidate should win.
- Use weak evidence to choose the next candidate, not to claim the bottleneck is proven.
- Treat stage cuts as diagnosis only. Do not promote them, add timings from incompatible cuts, or infer an end-to-end win from an isolated phase.
- If weak evidence repeatedly mispredicts the authoritative score, downgrade or discard that screening model.
- A weak screen produces false negatives, not just false positives: it can veto a real win. Once you have downgraded a screen, do not let it reject a candidate; let the authoritative metric decide that candidate.
- When local screening is non-predictive, the authoritative metric becomes the screen. Budget exploratory authoritative evaluations for screening instead of throttling exploration to conserve them; an unspent submission or eval budget is worth less than a discovered improvement.
- If no profiler exists and candidates keep tying, run a local-optimum audit sooner than usual and switch to structural probes.

## Weak Evidence Cannot Prove A Floor

Weak evidence may justify "I have not found a faster path." It can never justify "no faster path exists." Keep optimizing under weak evidence, but do not record a floor, impossibility, or "unreachable" verdict from it.

If you are about to declare a target unreachable and your evidence is weak, that is the signal to *acquire* target-class measurement, not to conclude:

- Get representative hardware, hardware counters, or a target-system trace.
- Spend oracle or submission budget to measure directly.
- Ask the user for access, a hint, or the known method.

A floor claim is valid only from a lower-bound proof or strong target-class evidence. Until then the correct recorded state is "best known so far," and the search stays open.

## Platform Blockers

Classify as platform/tooling blocker when:

- Failure happens before user code runs.
- The reference/sample output is corrupt, null, NaN, or unavailable.
- The runner lacks required dtype/library support.
- The submit endpoint returns availability errors with no job/submission ID.
- External capacity or billing prevents execution.

Do not spend repeated submissions on a platform blocker. Retain the exact error in the current context or active external harness, and continue only when the platform changes or a credible recovery path appears.
