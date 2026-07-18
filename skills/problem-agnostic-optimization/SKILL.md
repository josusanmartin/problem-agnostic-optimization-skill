---
name: problem-agnostic-optimization
description: "Use when improving a measured artifact under a correctness or scoring contract: performance, latency, throughput, leaderboard score, CPU/GPU kernel time, or stochastic policy quality. Protects the best result while prioritizing candidate throughput, authoritative measurement, explicit search-budget accounting, and enforced escapes from unproductive search families."
---

# Problem-Agnostic Optimization

```text
contract -> baseline -> model -> candidate -> validate/measure -> promote, learn, or escape
```

Only the authoritative metric promotes. Everything else explains. The process must cost less than the search capacity it saves.

## Always

1. Set the objective, authoritative metric, validation gate, edit surface, and budget before editing.
2. Reproduce or establish the baseline promptly; use `unknown, reproduce first` when needed.
3. Preserve the current best artifact outside risky candidate work.
4. Optimize candidate throughput as well as candidate quality. Defer bookkeeping that delays the next useful measurement.
5. Test one mechanism per candidate by default. A mechanism may require coordinated edits; do not split an interacting structural change into misleading micro-candidates.
6. Validate correctness before performance when practical.
7. Promote only by the authoritative metric.
8. Count actual measured attempts, including inner-loop configurations, seeds, and scheduler evaluations.
9. Force a different search family after the plateau trigger; do not document the same hill more thoroughly instead.
10. Reject wrong-answer, leaked-answer, stale-state, harness/grader, or invalid-contract wins.

## Contract

Record the objective, run state, authoritative metric, target, baseline, protected best, editable and immutable files, budget, validation, evidence availability, stop condition, progress ownership, and `Multi-agent mode: on|off`.

Run state is `prepare-only`, `active-run`, or `audit`. Create or update an active goal only when the user explicitly asks to start the optimization run now.

If asked to draft a goal for later, return a copy-paste prompt beginning with `Use problem-agnostic-optimization.` and a filled `/goal` block. Do not activate it.

If no target is given, use a comparable public best, prior local best, production SLO, or justified theoretical bound. Otherwise choose an ambitious measurable target and label its uncertainty.

## Persistence Modes

Use the lightest mode that preserves the run:

- `fast`: default, including long single-agent and leaderboard search. Keep the protected best and a compact score/decision/next-direction record. Progress charts are off unless requested. Do not read the full harness reference or initialize rich artifacts before the baseline unless the run cannot be resumed safely without them.
- `standard`: use for asynchronous or noisy remote work, explicit durable progress requests, handoffs, or runs likely to span sessions. Read `references/harness.md` and initialize the harness, but keep derived artifacts off the active-search path.
- `audit`: use when reviewing a run, investigating integrity, or preparing a high-stakes promotion. Rich evidence is allowed because the task is analysis rather than candidate throughput.

`minimal` is an alias for `fast`. A coordinator or sidecar should own token polling, heartbeat/checkpoint submissions, charts, dashboards, and report rendering whenever one exists. These activities must not consume the optimizer's search budget.

## Baseline And Model

Run the cheapest authoritative or contract-faithful baseline first. Then write a short bottleneck model that predicts what must change for the target to move.

Classify the current gap as:

- `floor gap`: a justified lower bound blocks the target for this graph or family.
- `schedule gap`: the graph may reach the target but packing, tail, dependencies, allocation, or variance wastes capacity.
- `evidence gap`: the model or measurements are too weak to choose reliably.
- `statistical gap`: apparent movement may be noise.

A plateau is not a floor proof. Treat resource floors as hypotheses unless their counts, throughput assumptions, dependencies, and unavoidable costs form a valid lower bound. If a better predicted floor fails to improve the authoritative metric twice, classify the model as incomplete and change the graph, route, or evidence source.

## Candidates

Before a meaningful candidate, state only what guides the experiment:

- parent and protected-best relationship
- mechanism family and hypothesis
- expected authoritative signal
- kill criterion
- correctness and measurement commands

Use an isolated branch or artifact for risky structural work. Prefer the smallest candidate that faithfully tests the mechanism, not the smallest textual diff. Compound changes are appropriate when an invariant, representation, schedule, or resource transfer works only as a coordinated unit; use follow-up ablations after it shows a signal.

Mechanism families include work deletion, resource transfer, tail/dependency change, scheduler/variance, representation/primitive/route change, contract specialization, approximation, and forbidden shortcut.

## Search Accounting

Track search health in attempts and budget, not ledger rows:

- One attempt is each measured configuration, seed, scheduler result, generated candidate, or authoritative evaluation used to support a search-family conclusion.
- A batch or sweep reports its total attempts; wrapping thousands of evaluations in one candidate does not reset stagnation.
- A same-artifact checkpoint, repeated verification, heartbeat, or token snapshot is operational work, not a candidate or promotion.
- A sub-noise score movement does not reset the promotion drought.

Default plateau trigger: force reassessment when either condition is met:

1. Three consecutive same-family measured candidates fail to improve outside noise.
2. Ten percent of the available active-time, evaluation, submission, token, or spend budget passes without a meaningful promotion.

Use the stricter user-supplied limit when present. A sweep must have a written attempt budget and stop rule before it starts.

At the trigger:

1. Stop the current sweep and mark the hill `CLOSED` or `NARROWED`.
2. Record the failed prediction or missing evidence in one sentence.
3. Name at least three genuinely different mechanism families.
4. Spend the next measured candidate off-hill. It may be a controlled regression or compound structural probe.

Continue the old hill only when a new premise is explicit: new evidence, a changed graph, a calibrated search tool, or a previously untested range justified by the model. More seeds or configurations alone are not a new premise.

For detailed resource, escape, and stochastic-search methods, read `references/resource-models.md`, `references/evidence-loop.md`, or `references/stochastic-policy-search.md` only when that issue is active.

## Progress

The active-search critical path is:

1. authoritative result or blocker
2. promotion decision
3. next direction, including whether the plateau trigger fired

Append one compact `<harness>/progress.tsv` row when persistence is requested and the writer is immediately available. Leave optional token, raw-evidence, and narrative fields blank instead of waiting. Refresh charts, dashboards, candidate dossiers, reviews, and usage summaries only at promotion, reassessment, handoff, user request, or in a sidecar.

Do not resubmit or reverify an identical artifact merely to create a candidate record. If an external service requires periodic checkpoints, label them `CHECKPOINT`, exclude them from search accounting, and let the coordinator perform them when possible.

## Promotion

Never promote from a screening metric. A meaningful promotion passes required correctness, the authoritative metric, applicable regression or adversarial checks, and a fresh verifier when the contract or risk requires it. Near ties favor the simpler and less stateful artifact.

After promotion, update the protected best and reset the promotion-drought counters. After a surprising regression, update or reject the bottleneck model before choosing another candidate.

## Multi-Agent Mode

Default is `off`. Enable only when requested. The coordinator owns canonical files and serial promotion; workers receive isolated mechanism families from a named parent. After a plateau, allocate at least one worker to a different representation, primitive, route, target split, or specialization rather than multiplying the same tuning sweep. Read `references/harness.md` for the worker protocol.

## Integrity And Handoff

Before promotion, confirm the candidate computes the required output for valid inputs, passes the required correctness scope, improves outside noise, uses current evidence, and remains valid across allowed input, seed, hardware, and hidden-case variation.

At handoff, report the protected best, authoritative metric, validation status, changed files, remaining gap, attempts and active budget since the last promotion, closed hills, live hypotheses, blockers, and next off-hill candidate. Distinguish `budget exhausted`, `blocked`, `plateau`, and `no valid target evidence`.

## References

| Need | Read |
|---|---|
| Durable, remote, resumable, or multi-agent harness | `references/harness.md` |
| Audit an active run | `references/auditor.md` |
| Floors, tails, primitive inversion, local optima | `references/resource-models.md` |
| Measurement, variance, frontier mining, blockers | `references/evidence-loop.md` |
| Simulator, policy, or hidden seeds | `references/stochastic-policy-search.md` |
| CPU/GPU/domain probes | `references/cpu-architecture.md`, `references/gpu-architecture.md`, `references/problem-families.md` |
| Optional durable templates | `references/templates.md` |
