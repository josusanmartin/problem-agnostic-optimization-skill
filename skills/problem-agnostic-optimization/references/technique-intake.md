# Technique Intake And Breakthrough Mining

Use this reference when public methods, competitor artifacts, prior history, or a cheaper search tool could expose a mechanism outside the current closed-world search.

## Contents

- Objective and method intake
- Breakthrough-history mining
- Mechanism extraction
- Screen calibration and validation islands

## Objective Evidence

Set a concrete objective before candidate work:

- Record a user-supplied target exactly.
- Otherwise find the best known result under the same contract from current leaderboards, papers, repositories, documentation, issue threads, production references, or requested prior evidence.
- If no reference exists, estimate a theoretical minimum or maximum from bytes, operations, latency, resource slots, or critical path.
- Record the source, date, contract match, and uncertainty. Refresh drift-prone public evidence when possible.
- Avoid a soft "improve a bit" target unless the user asks for a small cleanup.

The best known result is not necessarily the best known method. Seek public source, writeups, talks, issues, or papers for mechanisms that can be tested under the active contract.

## External Method Intake

Treat an external method as a mechanism to port, not a result to copy:

- Snapshot its source, provenance, build path, runtime lifecycle, contract, hardware, and authoritative result before interpreting it.
- Establish common ancestry among sources. Independent architectural agreement ranks hypotheses more strongly than copied implementations.
- If a materially faster artifact exists, return to the core router for the deeper frontier comparison instead of duplicating it here.
- Decompose the method into named sub-techniques and transfer each faithfully before tuning.
- Verify transfer with an ablation, counter, microbenchmark, or route attestation as well as end-to-end measurement.
- Treat a faithful-looking regression as a possible transfer error in window, stride, ordering, alignment, block count, precision, or lifecycle before rejecting the mechanism.
- Recheck old `CLOSED` verdicts under the new premises. Separate algorithm, implementation, mapping, integration, attachment, availability, enforcement, and measurement failures.
- Re-derive and cite the mechanism. Never use locked source, leaked outputs, or hidden-test constants as if they were clean optimization evidence.

## Breakthrough Mining

Use a compact history map when it can prevent duplicate work or reveal a new hill. A breakthrough changes an active floor, exposes a new resource axis, imports a better route, or creates a cheaper search tool; it is not merely a large score delta.

Keep the map in the active plan or active external harness. Do not initialize a logging system solely for mining.

```text
parent -> candidate | result/resources | active floor | mechanism | proof | search tool | validation | slack/dependency
```

Prioritize rows that changed a tier:

- First crossing of a resource wall, latency tier, memory tier, or leaderboard frontier.
- Large movement on one product-metric axis even when another axis regressed.
- Repeated tags or constants that form a family of wins.
- Notes such as `reverted`, `relaxed`, `margin`, `island`, `reroll`, or `fallback` that imply reclaimable contract-valid slack.
- Failed or rejected attempts whose notes identify a mechanism, blocker, or missing validator.

For each major row, identify:

- The binding operation count, peak lifetime, tail phase, validation island, hidden distribution, or search-throughput limit.
- The license for the change: algebraic identity, contract specialization, reachable-support invariant, clean storage, cheaper primitive, or external route.
- The resource saved, resource spent, and remaining co-binders.
- The cheap screen or model that made it searchable and the authoritative gate that promoted it.
- Knobs loosened to land the structural win and candidates for later reclamation.
- Prior clean islands, cached routes, tuned seeds, or conclusions invalidated by the graph change.

## Mechanism Classes

Turn mined evidence into one-hypothesis candidates:

- **Co-binder teardown**: identify all phases near the same peak or tail and sink them below the next tier together when one local cut cannot move the metric.
- **Invariant-based omission or hosting**: prove state is zero, dead, redundant, or unobserved, then delete, relocate, or recompute it around the peak.
- **Algebraic or paired-phase fusion**: remove redundant intermediates, inverse pairs, duplicated predicates, or mirrored carry/cleanup work only after proving phase cleanliness.
- **Primitive swap**: replace expensive cleanup, branch, conversion, allocation, synchronization, or math with a contract-valid cheaper primitive.
- **Completion by construction**: use a factorization, traversal, or transform that already produces a required complement, ordering, certificate, or second output.
- **Certificate and selective repair**: run a cheaper route, certify independent work units, and repair only failures; price certificate, synchronization, compaction, and worst-case fallback.
- **Reachable-support specialization**: narrow width, bound, search space, or iteration count only when the declared scored distribution supports it and full validation remains clean.
- **Search-tool breakthrough**: build a bit-exact or conservative screen when authoritative evaluation is too slow for the needed search. The screen proposes; authority promotes.
- **Post-breakthrough reclamation**: retighten guards, margins, windows, selectors, or conservative knobs after the structural route is protected.
- **Negative breakthrough**: close a route with a measured tradeoff or counterexample, scoped to the tested mechanism and accompanied by a reopen condition.

Rebuild each candidate against the current protected best. Do not copy a winning artifact blindly.

## Screen Calibration

Before a cheap screen filters a large search space:

- Reproduce known-clean and known-dirty cases under the same contract.
- Model every scored factor, shape, seed family, and public/hidden split that can create a false clean.
- State what the screen can reject, what it cannot prove, and whether false negatives are acceptable.
- Measure stacked knobs directly; component error rates can cancel or compound.
- Use the screen to propose candidates, never to promote them.
- Downgrade a screen that repeatedly mispredicts authority, and stop allowing it to veto candidates.

## Validation Islands

Some contracts allow neutral seeds, nonces, selectors, route choices, or rerolls that change the validation stream without changing intended computation or counted work.

- State why the selector is contract-allowed and what it changes.
- Treat a prior clean island as stale after work serialization, route, or operation-order changes until full validation passes.
- Never call island search a correctness proof; every selected artifact still needs the full gate.
- Retain old and new selector values in the candidate artifact so surprising results remain auditable.
