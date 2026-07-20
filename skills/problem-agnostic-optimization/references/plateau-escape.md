# Plateau Reassessment And Escape

Use this reference when a core search-health trigger fires or current evidence says the active hill no longer predicts authoritative improvement.

## Contents

- Reassessment and closure rules
- Local-optimum audit
- Off-hill mechanism families and escape operators
- Divergence and new-hill commitment

## Reassess Before Closing

A trigger pauses the current sweep; it does not prove a floor or automatically close a useful written experiment.

Check first:

- Did the intended candidate path execute?
- Were the results valid, comparable, authoritative, and outside known noise?
- Does a specific implementation bug explain the misses, with a faithful test still untried?
- Does a predeclared bracket remain, and is its expected information or gain still worth the narrowed budget?
- Did the bottleneck prediction move, even if the authoritative result did not?
- Did current evidence invalidate an inherited closure or premise?

`BUG`, `BLOCKED`, invalid measurement, and unresolved noise consume attempt and contract budget but are not same-family misses. Continue only for an explained bug or a still-valuable written bracket; state the reason, next discriminating test, and narrower budget. Otherwise close or narrow the hill.

## Local-Optimum Audit

Record only what is needed to choose the next hill:

```text
hill | best authoritative result | failed prediction | remaining plausible gain | why insufficient | reopen premise
```

Mark `CLOSED` when equivalent local work is no longer justified. Mark `NARROWED` when one specific bracket or premise remains. A plateau closes a hill, not the problem; only a valid lower-bound proof can close the target as unreachable.

After closure, the next measured candidate is off-hill by default. Continuing locally requires an explicit current-evidence reason, not more equivalent seeds, constants, or configurations.

## Name Different Mechanism Families

Choose at least three genuinely different families before selecting the cheapest probe:

- **Work graph**: delete, fuse, split, recompute, delay materialization, or share paired phases.
- **Representation**: pack, transpose, compress, precompute metadata, or change state/scratch layout.
- **Primitive or algorithm**: library route, hardware primitive, decomposition, direct versus transform method, or exact versus repaired route.
- **Resource or tail**: transfer work to measured slack, remove a co-binder, or shorten a dependency chain.
- **Schedule or execution route**: persistence, placement, batching, compiler/codegen, or concurrency form.
- **Target split**: per-shape, per-device, per-seed, per-mode, or per-size specialization.
- **Evidence or search tool**: calibrated screen, simulator, lower-bound model, microbenchmark, or phase-owner instrumentation.
- **Contract-valid precision or specialization**: tolerance-gated approximation, fixed shape, declared distribution support, or unobserved output.
- **External method**: public source, paper, competitor mechanism, or production architecture.
- **Negative proof**: counterexample or resource tradeoff that cheaply closes a tempting basin.

Changing a constant, tile, seed, ordering, or selector inside the same mechanism is not a new hill.

## Escape Operators

Assign one operator to each off-hill probe:

- `neighborhood_shift`: change representation, primitive, route, target split, or edit region.
- `perturb_reoptimize`: make one disruptive contract-valid change, then locally repair it before judging the hill.
- `destroy_repair`: remove a binding structure, then repair correctness or resource damage inside a fixed budget.
- `surrogate_uncertainty`: probe where the bottleneck model is weakest, then verify authoritatively.
- `tabu_anti_revisit`: forbid a closed basin unless its written aspiration rule fires.
- `diversity_archive`: preserve the best artifact per distinct feature cell rather than collapsing every probe into one incumbent.
- `external_intake`: transfer a known-better method before inventing more local variants.
- `negative_proof`: close a family by proof or counterexample before implementation.

Allow a temporary authoritative regression only when it opens a named new hill, has a strict repair/stop budget, and never replaces the protected best.

## Bounded Divergence

Spend a small novelty budget across different mechanism families, not many variants of one family. The contract controls size; three to six cheap probes or isolated worker packets is usually enough.

Each probe states:

```text
new hill | family/operator | why distinct | expected signal | validation/measurement | budget | kill | reopen rule
```

Every configuration, draw, generated artifact, or authoritative evaluation still counts as a measured attempt. Diversity means hypothesis diversity; it does not excuse an unbounded draw or parameter sweep.

Use Scorebench or another active external harness for persistent state when present. Otherwise keep only compact active context; do not create a local logging subsystem for the escape.

## Commit To A New Hill

When a probe opens a credible hill, stop scattering and allocate a short commitment budget, normally two to four follow-up candidates. An explicit hill change starts a new search epoch; renaming the old family does not.

Commit when at least one is true:

- A meaningful authoritative promotion occurs.
- The probe changes an active floor, peak/tail owner, validation island, or searchable region.
- A diagnostic signal moves a well-supported bottleneck and the remaining loss is plausibly repairable.
- The probe wins one separable lane, shape, seed regime, target, or product-metric axis.
- A faithfully transferred external mechanism has one identifiable integration defect.

Do not abandon a new hill after one rough result when its mechanism signal is real and the kill criterion has not fired. Close it when correctness fails intrinsically, its resource trade cannot cross the next floor, or authority and diagnostics both refute it after the commitment budget.

A genuine hill change resets the search epoch because the mechanism changed. Only a meaningful authoritative promotion updates the protected best, and the global contract budget remains consumed.
