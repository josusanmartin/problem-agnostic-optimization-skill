# Resource Models

Use this reference when total runtime cannot distinguish a bad schedule from an operation graph that cannot reach the target.

## Build The Cheapest Floor

For each plausible binder, estimate:

```text
resource | required work | valid throughput | floor | dependency/tail cost | evidence
```

The maximum credible floor bounds the current graph. Label it honestly:

- `proven lower bound`: all required work, valid throughput, dependencies, and unavoidable setup are covered.
- `model floor`: useful but incomplete assumptions remain.
- `observed plateau`: search history only.

A large sweep never proves a floor. If the target lies below one or more credible floors, stop schedule-only work and delete work, fuse stages, specialize a contract-valid route, transfer work to measured slack, or change representation/primitive.

## Distinguish Graph From Schedule

Compare floor, measured runtime, and their gap:

- Large gap on the same graph: packing, dependency, lifetime, or tail work may matter.
- Small gap but target missed: change required work or its resource assignment.
- Lower floor but worse runtime: inspect new dependencies, aliases, barriers, scratch lifetimes, and tail work.
- Same floor but better runtime: packing or tail placement improved.

Classify a large-budget candidate as work deletion, resource transfer, tail reshaping, scheduler/variance, or representation/primitive change. If a modeled floor falls twice without authority improving, stop optimizing that floor and audit omitted owners.

## Trace The Last Useful Work

Walk backward from the last useful operation, not merely the final store or return:

- Name the dependency chain and resource that stays busy.
- Check waits, barriers, atomics, aliases, scratch reuse, and stragglers.
- Distinguish a throughput-saturated resource from serial latency.

Optimize the tail when it owns runtime even if total counts look balanced.

## Price Transfers And Co-Binders

Before moving work, retain:

```text
resource saved | replacement resource | old/new floors | dependency risk | kill
```

A transfer is promising only when the source binds and the destination remains below the target. For product metrics, compute the break-even directly; a higher count can win when it crosses a peak or memory tier.

If several phase owners sit near the same peak or tail, one fix may expose the next immediately. Name the co-binders and test the smallest stack that can sink all of them below the next tier. Validate the integrated route, then reclaim temporary slack.

## Invert A Toxic Primitive

When compact code or lower operation counts do not improve time, test whether a gather, shuffle, masked operation, conversion, atomic, library call, or other primitive is microcoded, narrow, or serialized on the target.

Build one A/B that replaces that primitive family and predicts the resource transfer. More instructions may win if pressure leaves the true binder. Preserve target-specific variants when the inversion does not transfer.

## Prove Work Deletion

Use proof or counterexample before implementing expensive omission, fusion, predicate substitution, deduplication, or specialization. Skipping work is valid only when the written contract proves the state redundant or unobserved.

Never infer permission from current hidden tests, stale state, checker feedback, or a missing assertion. Retain a counterexample as a scoped closure with a reopen premise.

## Model Before Expensive Edits

Use a throughput calculation, microbenchmark, simulator, critical-tail trace, or correctness identity only when it can cheaply decide whether the best case matters. Prefer a model that first reproduces an observed counter or bottleneck magnitude; sweep only after mismatch is explained. Compose mechanisms after their resource trades are understood; a lower floor without dependency and tail checks is not an integrated candidate.
