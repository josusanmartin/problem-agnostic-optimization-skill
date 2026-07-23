# Variance And Bounded Sweeps

Use this reference when noise, stochastic evaluations, contract-allowed selectors, or a best-of-N scoreboard makes repeated draws potentially informative.

## Variance Calls

Use variance pushes only when the target gap is within measured noise or selector spread, or after structural levers are exhausted. Aimless resubmission is churn.

- State that the run is a variance call.
- Keep the artifact unchanged, or use the smallest contract-valid distinct artifact only when the platform deduplicates submissions.
- Record sample count, min, median, max, and dispersion when possible.
- Count every draw as a measured attempt and charge it to the active hill's epoch budget.
- Treat the bounded sweep outcome as one candidate-family decision; do not turn every draw into a same-family miss.
- Never describe same-artifact reruns as code improvement.
- Stop when the distribution makes the target implausible or marginal expected gain no longer justifies cost.

## When A Sweep Is Warranted

Run a bounded distribution sweep only when structural work is exhausted or the open question is explicitly about a noisy draw family, the measured spread is comparable to the remaining gap, and at least one condition holds:

- `best-of-N scoreboard`: each genuinely distinct draw can improve the recorded best.
- `contract-allowed draw distribution`: seeds, nonces, selectors, or distinct artifacts change the draw without changing required semantics.
- `distribution-for-decision`: enough samples can place the target outside a declared uncertainty margin and close only this draw family.

Do not sweep when the metric is deterministic with no distinct selector, the board records latest or mean with no distribution question, structural levers remain, or no written stop exists.

## Sweep Contract

Write before sampling:

- Pilot: at least five distinct samples, with min, median, and spread.
- Per-sample cost and distinctness rule.
- Objective: improve recorded best-of-N, characterize the draw family, or detect a subregion effect outside noise.
- Attempt budget and falsifiable stop: best stalls for `K` draws, target lies outside the selected margin, or budget is spent.
- Optional escape bracket: one budgeted larger-radius probe after a dry local sweep; omit it when a radius change cannot test the same family faithfully.
- Epoch rule: another seed batch does not reset the search epoch; only a meaningful authoritative promotion or a genuine hill change does.

Order statistics make the stop useful: expected gain from the next draw shrinks toward the distribution tail as samples accumulate. End by banking an authoritative gain or using the measured distribution to close the draw family, never the whole problem.
