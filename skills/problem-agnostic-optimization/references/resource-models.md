# Resource Models

Use this reference when total runtime alone is not enough to decide what to try next. The goal is to distinguish "the schedule is bad" from "the operation graph cannot reach the target."

## Contents

- Resource floors and schedule gaps
- Tail, engine-balance, and co-binder audits
- Primitive inversion and contract-aware omission
- Cheap models and mechanism composition

## Resource Floors

Convert the workload into constrained-resource lower bounds:

- Count work units by resource: ALU slots, vector slots, scalar slots, load/store ports, memory bytes, gathers, shuffles, barriers, kernel launches, scratch usage, or queue operations.
- Divide each count by plausible throughput.
- Add unavoidable latency or launch/setup costs.
- The maximum lower bound is the best possible runtime without deleting work, moving work, or changing the representation.

Label the result correctly:

- `proven lower bound`: counts cover all required work, throughput assumptions are valid, and unavoidable dependencies and setup are included.
- `model floor`: useful estimate with incomplete packing, dependency, lifetime, or route assumptions.
- `observed plateau`: failed search history only; never call this a floor.

A large configuration sweep proves only that the sampled search procedure did not find a better result. It does not prove the graph, scheduler family, or target is resource-pinned. If a later structural candidate could invalidate an assumption, keep that assumption explicit and the floor revisable.

Use the gap to estimate minimum useful change. If the target is below several resource floors, a candidate must reduce all blocking floors enough to matter; deleting a few operations on one resource is not a breakthrough if another floor remains above target.

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

Classify each candidate before spending a large budget:

- `work deletion`: fewer required operations, bytes, launches, branches, reductions, or synchronization points.
- `resource transfer`: work moves from one constrained resource to another; useful only if the destination has slack.
- `tail reshaping`: total work is similar, but the last critical chain shortens.
- `scheduler/variance`: same graph, different packing or tie-breaking.
- `representation/primitive change`: a different data layout, algorithm, or hardware primitive changes the floor model.

When the target is below the current floors, prioritize work deletion, representation, primitive, or contract-valid omission over scheduler-only search.

If a candidate lowers a model floor but the authoritative result fails to improve twice, stop optimizing that floor. Audit dependencies, tails, and omitted resource owners, then use an off-hill graph, representation, route, or evidence probe.

## Tail Audit

Total counts hide late critical paths. Audit the final part of the schedule or runtime trace:

- Which resource is full near the end?
- Which block, group, warp, lane, item, or row finishes last?
- Are stores blocked by final compute or reductions?
- Are waits, barriers, atomics, or scratch reuse semantically required?
- Did a memory-saving alias create write-after-read or read-after-write chains?
- Does compaction leave a long tail on one engine while others idle?

If the tail dominates, optimize the tail even if total counts look balanced.

Tail audits should name the last useful work, not just the last store or return. A final store blocked by compute points back to the compute chain; a final compute op blocked by a load points back to the load/address route. Use this to decide whether a final-stage tweak is worth testing.

## Engine Balance

Moving work only helps when the destination has slack.

Before a rebalance candidate, state:

- Resource saved:
- Replacement resource:
- Current floor for both resources:
- Expected new floor:
- New dependency or tail risk:

Reject "frees resource A" arguments unless the replacement work on resource B stays below the target floor.

For near-frontier systems, write the expected floor delta before coding. A useful rebalance needs both:

- The saved resource was actually limiting.
- The replacement resource stays below the target after the move.

If either is false, the candidate is a pressure transfer, not a likely breakthrough.

## Product Metrics And Co-Binders

For product metrics such as `resource_a * resource_b`, a candidate can win while spending one resource back to reduce the other. Compute the break-even before rejecting it:

```text
new_a * new_b < old_a * old_b
```

For a minimizing `count * peak` metric, spending `delta_count` is worthwhile when the peak drop is large enough:

```text
(count + delta_count) * (peak - delta_peak) < count * peak
```

This matters near peak or memory walls: a higher operation count can be a real breakthrough if it crosses a resource tier.

Co-binder rule:

- List the top resource owners at the current peak, tail, memory high-water mark, or latency endpoint.
- If several owners are within a small band, the first fix may appear to do nothing because another owner immediately rebinds the metric.
- Plan a stack that sinks all co-binders below the next floor, then validate the composed route.
- After the tier drop, spend the new slack carefully: re-tighten knobs that were relaxed to find the structural route.

Use a phase-owner table when the metric is blocked by peak, tail, memory, or live-state width:

```text
phase/resource owner | height/cost | next floor | evidence | proposed stack
```

The table should name the useful work that owns the floor, not just the final store, free, or return. If the next floor is close, the winning candidate may need to spend extra work to cross the peak tier and then reclaim operation count afterward.

Negative resource trades are also useful. If a deeper route saves operation count but grows transcript, memory, live width, latency tail, or synchronization enough to lose the product metric, retain the counterexample and state what would make it worth reopening.

## Primitive Inversion Audit

When local tuning repeatedly improves counts but not time, audit whether the chosen primitive family is itself the bottleneck. A "better" operation graph can be worse on a specific target if it uses a microcoded, narrow, serialized, or frontend-heavy primitive.

Run this audit before another sweep of unrolls, masks, or alignments:

- Suspect primitive:
- Evidence: counter, profile, throughput table, microbenchmark, or repeated plateau.
- Compact graph resource floor:
- Decomposed graph resource floor:
- Resource moved from:
- Resource moved to:
- Why the destination has slack:
- Expected wall-time/counter signal:
- Kill criterion:

Valid outcomes:

- A higher-instruction decomposition wins because it removes the hidden bottleneck.
- The decomposition loses but explains that the compact primitive is not the limiting floor.
- The decomposition wins on only one target; preserve target-specific variants instead of forcing one global path.

## Negative Proof Audits

Some high-leverage ideas are best tested by proof or counterexample before implementation:

- Algebraic deletion: does omitting or fusing a stage produce a constant delta, equivalent predicate, or contract-proven redundant value?
- Predicate substitution: can an already-live value's zero/nonzero status replace an explicit boolean or branch bit for all valid inputs?
- Shape specialization: do fixed sizes, seeds, layouts, or unobserved outputs prove a path can be skipped?
- Collision/dedup model: does the best-case distribution save enough work after gather/scatter/compact overhead?

A negative audit is a result. Retain the counterexample or failed proof obligation, then close that shortcut family until a new precondition appears.

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
- Resource-floor screen before implementing a broad mask/config search.
- Critical-tail trace before final-stage micro-tuning.

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
