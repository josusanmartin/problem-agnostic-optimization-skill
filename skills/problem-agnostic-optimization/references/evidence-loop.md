# Evidence Loop

Use this reference when deciding what to measure, what to trust, and how to promote or reject candidates.

## Contract First

Build this before coding:

- Interface and exact artifact to submit or deploy.
- Input shapes, sizes, dtypes, layouts, distributions, seeds, and hidden/public differences.
- Correctness tolerance and reference behavior.
- Target metric: remote wall time, geomean, p95, throughput, score, counters, memory, or cost.
- Target hardware, compiler/runtime, flags, source limits, language limits, and sandbox constraints.
- Budget: submissions, API calls, GPU minutes, wall-clock, or production risk.
- Editable files and immutable reference, harness, evaluation, data, or scoring files.

If the score is aggregate, split it. A geomean hides shape-specific bottlenecks.

## Objective Evidence

Set the objective before candidate work:

- If the user provides a target, record it exactly.
- If no target is provided, search public leaderboards, papers, repos, docs, issue threads, production references, or prior local reports for the best known result on the same contract.
- If no public or local reference exists, compute a theoretical minimum from bytes moved, operation count, launch/setup latency, resource slots, or critical-path latency.
- For minimizing metrics, set the goal at the explicit target, best public result, or theoretical floor. For maximizing metrics, use the corresponding best known ceiling or theoretical maximum.
- Record the objective source and uncertainty. If the source may be stale and internet access is available, refresh it.
- Do not choose a soft "improve a bit" target unless the user asks for a small cleanup. Optimization needs a concrete ambitious threshold.

## Measurement Hierarchy

Promotion uses the authoritative metric:

- Leaderboard/ranked submit beats local benchmark.
- Production p95 beats synthetic microbench.
- End-to-end model score beats isolated component timing.
- Public accepted/benchmarked state beats failed-state runtime fields.

Use counters and profiles for diagnosis:

- Counters explain why wall time moved.
- Counters do not override wall time.
- If counters improve and time worsens, the wrong resource was optimized or a new pressure was introduced.
- Distinguish a real graph improvement from a placement improvement: slot counts, bytes, launches, or branch counts changing means a different operation graph; identical counts with better time is scheduler, packing, or tail behavior.

## Candidate Ledger

Every meaningful candidate gets:

```markdown
## vNN short-name

- Parent:
- Hypothesis:
- Mechanism:
- Expected signal:
- Resource floor delta:
- Tail/dependency risk:
- Artifact:
- Correctness:
- Measurement:
- Per-shape/counter delta:
- Decision: promote / keep variant / reject / bug / blocked
- Next:
```

For longer runs, add theme summaries:

```markdown
## vNN-vMM theme

- Starting model:
- Variants tried:
- Best result:
- What improved:
- What regressed:
- What this ruled out:
- Updated model:
- Next experiments:
```

## Promotion Gates

Promote only when:

- Correctness is clean or the authoritative platform has accepted it.
- The target metric improves outside known noise, or the scoreboard has accepted the row.
- The win survives the required scope: full test set, hidden/ranked route, multi-seed sweep, cross-shape sweep, or rerun stability when applicable.
- The winning artifact is saved under a durable name.
- The result includes command, run ID, submission ID, job ID, or report path.
- The improvement source is understood well enough to guide the next iteration.
- The added complexity is justified by the measured gain. Near-ties should favor simpler code.

Keep separate artifacts when a candidate wins on one target but regresses another.

## Simplicity And Scope

Optimization work should be narrow even when the search is aggressive:

- Every changed line should trace to the candidate hypothesis.
- Do not add speculative abstractions, configurability, dependencies, or error handling that is not required by the target contract.
- Match the existing project style and harness conventions.
- If equal or near-equal scores are available, prefer deletion, simplification, or smaller diffs over clever machinery.
- Surface assumptions and tradeoffs before coding when multiple interpretations would change the experiment.

## Failed-Idea Interpretation

Convert each failure into a search rule:

- `work deleted, target still impossible by floors`: the deletion is too small or hits the wrong resource; compose only with a mechanism that attacks the remaining floor.
- `lower floor, slower runtime`: dependency chain, scratch lifetime, barrier, aliasing, or tail got worse.
- `one resource saved, another overloaded`: resource rebalance was not conservative.
- `same counts, time changes`: schedule/tail sensitivity exists; tune only if the target gap is plausibly within the variance or packing gap.
- `single-shape win, geomean loss`: keep as a route candidate, not a global promotion.
- `benchmark win, ranked loss`: stability, hidden distribution, warmup, or state contract differs.
- `schedule-only plateau`: move to work deletion, fusion, specialization, representation change, or primitive change.
- `repeated near-ties`: run a local-optimum audit before the next same-family candidate.
- `counterexample found for an algebraic shortcut`: close the shortcut family unless a stronger precondition is proven by the contract.

## Variance Handling

Use variance pushes only after structural improvement is exhausted or when the target gap is within normal noise.

Rules:

- State that the run is a variance call.
- Keep the artifact unchanged.
- Record sample count, min, median, max, and dispersion when possible.
- Do not describe same-file reruns as code improvement.
- Stop variance calls when the distribution shows the target is implausible or the budget is no longer justified.

## Platform Blockers

Classify as platform/tooling blocker when:

- Failure happens before user code runs.
- The reference/sample output is corrupt, null, NaN, or unavailable.
- The runner lacks required dtype/library support.
- The submit endpoint returns availability errors with no job/submission ID.
- External capacity or billing prevents execution.

Do not spend repeated submissions on a platform blocker. Preserve the state/log, write a short issue note, and continue only when the platform changes or a bypass is credible.

## Shortcut Screen

Reject as exploit-like unless explicitly requested:

- Hardcoded outputs or shape/device constants learned from checker failures.
- Leaked validation answers used to skip computation.
- Reliance on uninitialized state, stale buffers, warmup count, or fixed hidden input order outside the contract.
- Stale-suite leaderboard rows used as proof of first place.
- Runtimes from wrong-answer or compile-failed states used as performance proof.

Clean optimization computes the intended result under the declared contract.
