# Resource Models

Use this reference when total runtime alone is not enough to decide what to try next. The goal is to distinguish "the schedule is bad" from "the operation graph cannot reach the target."

## Resource Floors

Convert the workload into constrained-resource lower bounds:

- Count work units by resource: ALU slots, vector slots, scalar slots, load/store ports, memory bytes, gathers, shuffles, barriers, kernel launches, scratch usage, or queue operations.
- Divide each count by plausible throughput.
- Add unavoidable latency or launch/setup costs.
- The maximum lower bound is the best possible runtime without deleting work, moving work, or changing the representation.

If the target is below the current lower bound, do not spend time on schedule-only changes. Move up a level:

- Delete work using contract or algebra.
- Fuse stages to remove materialization or launch overhead.
- Specialize valid shapes/routes.
- Move work to a resource with measured slack.
- Change data representation or primitive family.

## Schedule Gap Versus Op-Graph Gap

A better theoretical floor can still run slower. Track both:

- `floor`: best possible if resources were perfectly packed.
- `scheduled/runtime`: actual cycles or wall time.
- `gap`: runtime minus floor.

Interpretation:

- Large gap, same op graph: scheduler, packing, dependency, lifetime, or tail issue may be worth tuning.
- Small gap, target still missed: schedule is near frontier; delete or rebalance work.
- Lower floor, worse runtime: the new graph added dependencies, scratch lifetimes, waits, barriers, aliases, or tail work.
- Same floor, better runtime: likely packing/tail/scheduler improvement.

## Tail Audit

Total counts hide late critical paths. Audit the final part of the schedule or runtime trace:

- Which resource is full near the end?
- Which block, group, warp, lane, item, or row finishes last?
- Are stores blocked by final compute or reductions?
- Are waits, barriers, atomics, or scratch reuse semantically required?
- Did a memory-saving alias create write-after-read or read-after-write chains?
- Does compaction leave a long tail on one engine while others idle?

If the tail dominates, optimize the tail even if total counts look balanced.

## Engine Balance

Moving work only helps when the destination has slack.

Before a rebalance candidate, state:

- Resource saved:
- Replacement resource:
- Current floor for both resources:
- Expected new floor:
- New dependency or tail risk:

Reject "frees resource A" arguments unless the replacement work on resource B stays below the target floor.

## Contract-Aware Omission

Skipping work is valid only when the contract proves the skipped state is unobserved or redundant.

Safe examples:

- A final state is not part of the output.
- A value is algebraically redundant under exact input constraints.
- A warmup/setup path is outside the measured region by contract.
- A shape-specialized path is valid because the benchmark contract fixes that shape set.

Unsafe examples:

- Skipping because current hidden tests do not inspect a value.
- Reusing stale state without contract proof.
- Hardcoding values learned from checker failures.
- Omitting values-plus-indices when the contract requires both.

## Cheap Models Before Expensive Edits

Use a model when an implementation is expensive or likely to perturb many paths:

- Throughput lower-bound spreadsheet or script.
- LP/randomized floor search for schedule feasibility.
- Distribution simulator for collision, dedup, sparsity, or route balance.
- Microbenchmark for one primitive or resource.
- Tail audit on a reduced schedule.
- Correctness identity proof before fusing or omitting work.

A model does not need to be perfect. It only needs to answer whether the best case can matter.

## Composing Mechanisms

Compose only after individual mechanisms are characterized.

Good composition:

- Mechanism A saves saturated resource X but increases resource Y.
- Mechanism B reduces Y or shortens the new tail.
- A scheduler/compactor retune is run after the graph changes.
- The composed default is validated, not just component toggles.

Bad composition:

- Bundling knobs before knowing their effects.
- Combining two changes that both overload the same destination resource.
- Trusting a lower floor without checking dependencies and tail.

## Plateau Rules

Stop broad local search when:

- Best variants repeatedly tie the baseline.
- Lower bounds already exceed the target.
- Exhaustive or randomized masks find only parity.
- Count reductions repeatedly worsen scheduled runtime.
- The same family fails under multiple independent formulations.

Then change representation, primitive, route, or contract specialization level.

## Local-Optimum Audit

Run this audit when the search keeps improving local details but not the authoritative target.

Triggers:

- Three or more variants in the same family tie, regress, or move less than noise.
- A sweep curve is flat or has already found the local sweet spot.
- The current lower bound is above the target.
- A lower floor repeatedly fails to become a runtime win.
- The same mechanism loses across different implementations or targets.
- Same-artifact variance samples show the target is outside the plausible distribution.

Audit:

```markdown
## Local Optimum Audit

- Current hill:
- Why it looked promising:
- Best verified result on this hill:
- Plateau evidence:
- Resource floor or tail blocker:
- What this hill can still plausibly gain:
- Why that is insufficient:

Different hills:
- Hill 1:
- Hill 2:
- Hill 3:

Next off-hill probe:
- Cheapest falsifiable test:
- Expected signal:
- Kill criterion:
```

Different-hill examples:

- Change primitive family: direct kernel to library/FFT/GEMM, cooperative scan to two-pass scan, atomics to sort/reduce, scalar loop to vectorized representation.
- Change representation: packed data, transposed layout, precomputed metadata, page grouping, block ordering, scratch layout, compressed state.
- Change route/config: persistent to non-persistent, CPU to GPU path, one library heuristic to another, exact path to residual approximate path.
- Delete/fuse work: remove materialization, combine stages, omit contract-unobserved state, skip setup only when the contract proves it safe.
- Split target: per-shape, per-GPU, per-seed, per-mode, or per-size policy instead of one global implementation.

Rule:

- After the audit, the next candidate should be off-hill by default. Return to micro-tuning only if the off-hill probe fails or the user explicitly asks to keep grinding.
