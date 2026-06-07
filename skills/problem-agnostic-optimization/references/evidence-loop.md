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
- Scoreboard semantics and draw/noise model: is the recorded result single-shot, an aggregate, or `best-of-N` over submissions (the board keeps your best ever)? What varies between samples: rerun noise, seed/nonce/route selector, hidden queue state, or structurally distinct artifact? Record measured spread across draws or reruns. These decide whether a sweep can ever help; see Variance Handling.

If the score is aggregate, split it. A geomean hides shape-specific bottlenecks.

## Objective Evidence

Set the objective before candidate work:

- If the user provides a target, record it exactly.
- If no target is provided, search public leaderboards, papers, repos, docs, issue threads, production references, or prior local reports for the best known result on the same contract.
- If no public or local reference exists, compute a theoretical minimum from bytes moved, operation count, launch/setup latency, resource slots, or critical-path latency.
- For minimizing metrics, set the goal at the explicit target, best public result, or theoretical floor. For maximizing metrics, use the corresponding best known ceiling or theoretical maximum.
- Record the objective source and uncertainty. If the source may be stale and internet access is available, refresh it.
- Do not choose a soft "improve a bit" target unless the user asks for a small cleanup. Optimization needs a concrete ambitious threshold.

## External Technique Intake

Objective Evidence finds the best known *result*. Also seek the best known *method*: competitor writeups, public source, talks, issue threads, or papers for the same contract. Treat these as mechanisms to port, not just numbers to chase. Optimizing only within self-generated ideas (closed-world search) is a common reason a real win is missed; when the search has plateaued, importing a known-better mechanism is often higher leverage than another local sweep.

When porting an external mechanism:

- Decompose it into named sub-techniques and port them faithfully before tuning.
- Verify each sub-technique transferred with a counter, ablation, or microbenchmark, not just the end-to-end score.
- A faithful-looking reconstruction that regresses usually means one mis-transferred parameter (window size, stride, ordering, alignment, block count), not a refuted technique. Isolate the mis-transfer before discarding the mechanism.
- Re-derive and cite the mechanism; do not copy locked or proprietary source as your own, and never use leaked outputs or hidden-test constants.

## Breakthrough Mining

Use this when a run is plateaued, public-leaderboard driven, or expensive enough that another same-family sweep is unlikely to matter. A breakthrough is a mechanism that changes an active floor, exposes a new resource axis, imports a better route, or creates a cheaper way to search. It is not merely a large score delta.

Mine public history and local ledgers into a small durable table. In harnessed runs, keep it in `work/breakthroughs.md`; do not leave it only in chat.

```text
row | parent -> candidate | score/resources | active floor | delta | mechanism | proof or invariant | search tool | validation | slack/dependency
```

Prioritize rows that changed a tier, not only rows with the largest percent drop:

- first drop below a resource wall, latency tier, memory tier, or leaderboard frontier
- large product-metric movement on one axis even when another axis regressed
- repeated tags, constants, or comments that become a family of wins
- "reverted", "relaxed", "margin", "island", "reroll", or "fallback" notes that imply recoverable slack, when those mechanisms are contract-allowed
- failed or rejected submissions whose notes name a mechanism, blocker, or missing validator

For each major row, answer:

- What exactly was binding before: operation count, peak lifetime, tail phase, validation island, hidden distribution, or search throughput?
- What license made the change valid: algebraic identity, contract specialization, reachable-support invariant, temporarily clean storage, cheaper primitive, or external route?
- Which resource moved and which resource was spent back?
- What cheap screen or model made the candidate searchable, and what authoritative check still promoted it?
- What knobs were loosened to land the structural win, and which can be re-tightened afterward?
- Which prior clean island, cached route, tuned seed, or local conclusion became stale after the change?

Turn mined mechanisms into candidates by class:

- **Co-binder teardown**: if several phases tie the peak or tail within a small band, a single local cut may not move the metric. Instrument phase labels or resource owners, then sink all co-binders in one route or in a planned stack.
- **Invariant-based omission or hosting**: prove some work, state, lane, buffer, carry, branch bit, or history slot is zero, dead, redundant, or unobserved under the contract. Then remove it, host it on a temporarily clean lane, or recompute it around the peak.
- **Algebraic fusion**: look for adjacent operations with no intervening reader, inverse pairs, duplicated predicates, or equivalent branch decisions. Fuse only after proving the intermediate state is not required.
- **Paired-phase fusion**: when a forward phase and its reverse/apply mirror both pay a similar carry, cleanup, synchronization, or materialization cost, check whether the reverse controls can be recovered from the output state and both phases can share one primitive. This is higher risk than local fusion; prove phase cleanliness, not just value equality.
- **Primitive swap**: replace an expensive cleanup, branch, conversion, allocation, or synchronization primitive with a contract-valid cheaper primitive. Check that the new primitive preserves correctness state, not just counts.
- **Reachable-support truncation**: a worst-case width, bound, search space, or iteration count may be loose for the contract-declared scored distribution. Treat the truncated path as a hypothesis requiring full validation, not as a proof from sampled cleanliness or hidden-test leakage.
- **Search-tool breakthrough**: if the authoritative run is too slow for the needed sweep, build a cheaper bit-exact or conservative screen for the dirty condition. The screen proposes candidates; the authoritative metric still decides.
- **Post-breakthrough slack reclamation**: structural wins often relax guards, margins, windows, seeds, or conservative knobs to find a clean route quickly. After promotion, revisit those relaxed knobs on the new base before declaring the route exhausted.
- **Negative breakthrough**: an attractive route can be ruled out by measured resource tradeoff, not just correctness failure. Record why it looked promising, the blocker, and the condition that would reopen it.

Do not copy a winning artifact blindly. Extract the mechanism, parent assumptions, knobs, and validator, then rebuild the candidate against the current protected best.

### Screen Calibration

A cheap screen is a breakthrough only after calibration. Before it filters large search spaces:

- Reproduce known-clean and known-dirty cases from the same contract when they exist.
- Model every scored factor, shape, seed family, or hidden/public split that can cause a false clean.
- Record what the screen can reject, what it cannot prove, and whether false negatives are acceptable.
- Measure stacked knobs directly. Individual dirty counts, break sets, or error rates can cancel, compose, or become worse when combined; do not extrapolate from single-knob screens alone.
- Use the screen to propose candidates, not to promote them. The authoritative metric remains the promotion gate.
- When a screen repeatedly mispredicts the authoritative result, downgrade it and stop using it as a veto.

### Validation Islands

Some contracts allow neutral selectors, seeds, nonces, route choices, or rerolls that change the validation stream without changing the computed function or counted work. Treat these as first-class candidate state:

- Record why the selector is contract-allowed and what it changes.
- After any serialized work, route, or op-order change, assume the previous clean island is stale until full validation proves otherwise.
- Do not describe an island search as a correctness proof; it is a way to find a candidate that still must pass the full validator.
- Keep old and new selector values in the candidate artifact so a surprising result can be audited.

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

Fallback discipline:

- Promote only by the authoritative metric, even if a weak profiler says the candidate should win.
- Use weak evidence to choose the next candidate, not to claim the bottleneck is proven.
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

## Candidate Ledger

Every meaningful candidate gets:

```markdown
## vNN short-name

- Parent:
- Hypothesis:
- Mechanism:
- Expected signal:
- Profiling basis:
- Profiling availability:
- Resource floor delta:
- Profile/trace evidence:
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

Use variance or draw pushes only after structural improvement is exhausted or when the target gap is within normal noise or selector spread. The default is that aimless resubmission is churn, not optimization.

Rules:

- State that the run is a variance call.
- Keep the artifact unchanged (or, if the platform dedups submissions, the smallest distinct artifact per draw).
- Record sample count, min, median, max, and dispersion when possible.
- Do not describe same-file reruns as code improvement.
- Stop variance calls when the distribution shows the target is implausible or the budget is no longer justified.

### When A Sweep Is Warranted

A budgeted distribution/variance sweep is sometimes the correct tool, not a rules exception. It is the mechanism that reconciles "do not claim a floor from a plateau" with "stop variance pushes": a bounded sweep either banks a real gain or produces the measured distribution that closes the current draw family and forces a clean stop or hill change. Run one only when all hold:

- Structural levers are exhausted, or the open question is purely whether the target is reachable under a defined noisy or contract-allowed draw family.
- The measured draw-to-draw or run-to-run spread is comparable to or larger than the remaining gap, so single samples cannot decide.
- At least one of:
  - `best-of-N scoreboard`: the board records your min/max over submissions, so each genuinely-distinct draw can lower (raise) the recorded result even with no better artifact; or
  - `contract-allowed draw distribution`: seeds, nonces, route selectors, or structurally-distinct artifacts change the scored draw without changing the intended computation or violating the contract; or
  - `distribution-for-decision`: you need the reachable distribution to close the current draw family rigorously, and a sweep that places the target several dispersion units outside the measured distribution is the family-specific evidence the plateau rule otherwise lacks.

It is churn (the default-discouraged case) when the metric is deterministic and no distinct draw/selector exists, the board takes latest/mean (no best-of-N benefit), structural levers remain, or there is no plan and no stop.

Write the sweep plan before sampling:

- Pilot: >= 5 distinct samples -> min, median, spread.
- Per-sample cost (submissions, rate-limit time, eval budget) and the distinctness constraint: if the platform dedups, each draw needs the smallest contract-valid distinct artifact, which bounds the achievable sample count.
- Objective: lower the recorded best-of-N / characterize the current draw family / detect a sub-region effect above noise.
- Falsifiable stop, whichever fires first: recorded best stalls for `K` draws; the distribution places the target outside by the chosen margin (then close the current draw family and return to structural search); or the budget is spent.

Order statistics give the stop teeth: expected gain from the next draw shrinks toward the distribution's lower tail as samples accumulate, so stop when marginal expected gain is below the per-sample cost. A converged sweep is a result: it ends by banking a best-of-N gain or by supplying the distribution that closes the current draw family, not the whole problem.

## Platform Blockers

Classify as platform/tooling blocker when:

- Failure happens before user code runs.
- The reference/sample output is corrupt, null, NaN, or unavailable.
- The runner lacks required dtype/library support.
- The submit endpoint returns availability errors with no job/submission ID.
- External capacity or billing prevents execution.

Do not spend repeated submissions on a platform blocker. Preserve the state/log, write a short issue note, and continue only when the platform changes or a bypass is credible.

## Forbidden Shortcut Screen

Reject and do not run exploit-like shortcuts:

- Hardcoded outputs or shape/device constants learned from checker failures.
- Leaked validation answers used to skip computation.
- Reliance on uninitialized state, stale buffers, warmup count, or fixed hidden input order outside the contract.
- Stale-suite leaderboard rows used as proof of first place.
- Runtimes from wrong-answer or compile-failed states used as performance proof.
- Modifying the reference, harness, scorer, data generator, or submission protocol to make a candidate appear faster.

Clean optimization computes the intended result under the declared contract.
