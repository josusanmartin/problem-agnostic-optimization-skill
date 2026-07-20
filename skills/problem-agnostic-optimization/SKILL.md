---
name: problem-agnostic-optimization
description: "Use when improving a measured artifact under a correctness or scoring contract: performance, latency, throughput, leaderboard score, CPU/GPU kernel time, or stochastic policy quality. Runs a lean, throughput-aware evidence loop with a protected best, measured-attempt accounting, authoritative promotion, and forced off-hill escapes. Logging and reporting are optional external concerns; when Scorebench is active, Scorebench owns them."
---

# Problem-Agnostic Optimization

Optimize the artifact. Keep process machinery off the critical path.

```text
contract -> baseline -> bottleneck model -> candidate -> validate/measure -> decide -> iterate or escape
```

Only the authoritative metric promotes. Profiles, counters, local benchmarks, and models explain.

## Contract

Before editing, establish:

- Objective and authoritative metric, including direction and target.
- Current baseline, or `unknown, reproduce first`.
- Artifact to protect, editable files, and immutable files.
- Correctness and validation requirements.
- Budget or stopping rule.
- Target hardware, workload, seeds, shapes, or production conditions when relevant.
- Search-health thresholds, defaulting to the policy below.
- Multi-agent mode, defaulting to `off`.

Use `/goal` for substantial or long-running optimization. If asked for a goal "for later", return a copy-paste prompt beginning with `Use problem-agnostic-optimization.` and a filled `/goal` block; activate only when explicitly asked.

Use current workspace and user evidence by default. Mine sibling workspaces, old candidates, or prior submissions only for requested transfer or continuation.

## Core Loop

1. Reproduce the baseline with the authoritative command or service.
2. Preserve the current best artifact before risky edits.
3. Build the cheapest useful bottleneck model from measurements, profiles, counters, case splits, or resource floors.
4. Choose one falsifiable mechanism and make the smallest candidate that faithfully tests it.
5. Prove the intended candidate path executed before interpreting correctness or timing.
6. Validate correctness before performance when possible.
7. Measure with the authoritative metric.
8. Decide `PROMOTE`, `KEEP VARIANT`, `REJECT`, `BUG`, or `BLOCKED`.
9. Update the bottleneck model after a promotion or surprising regression.
10. Count actual measured attempts and change hill when the search-health trigger fires.

For each candidate, retain: parent, mechanism family, hypothesis, expected signal, attempt budget, kill criterion, validation, measurement, and decision. Keep one compact active-state entry; no dossier by default.

One mechanism may require coordinated edits. Prefer the smallest faithful mechanism test, not the smallest textual diff. Use follow-up ablations after a compound structural candidate shows an authoritative signal.

## Optional Observability

Optimization and observability are separate modules.

Default behavior is no logging subsystem. Do not initialize a local harness or create `progress.tsv`, `events.jsonl`, `log.md`, `state.json`, charts, dashboards, audits, token ledgers, or candidate JSON unless explicitly requested. Benchmark outputs, profiler captures, submissions, and contract-required files are not optional logging.

Search-health accounting is active decision state, not a logging requirement. In plain PAO, keep it in the current plan or reasoning context. When Scorebench is active - because the user invokes it, provides a scoped Scorebench run, or the task is assigned through Scorebench - derive attempts, budget use, promotion history, and best state from Scorebench. Do not mirror them into PAO files.

Follow the `scorebench` skill for run lifecycle, submissions, token accounting, history, best-state tracking, logging, and reports. Do not create parallel PAO logs or dashboards, do not duplicate token accounting, and do not submit directly to the underlying venue. PAO supplies only optimization strategy and candidate decisions.

If the user explicitly requests local persistent logging while Scorebench is inactive, use a separate logging skill or module selected for that task. Keep it sidecar to the candidate loop. A logger or renderer failure must not block optimization unless logging is part of the user's stated contract.

Never run local and Scorebench logging in parallel. If a run moves to Scorebench, stop local logging rather than backfilling or mirroring it.

## Gap And Candidate Choice

Classify the current gap before choosing a candidate:

- `floor gap`: a proven lower bound blocks the target for the current graph or family.
- `schedule gap`: the graph may reach the target, but packing, tail, dependencies, resource pressure, synchronization, allocation, or variance wastes capacity.
- `evidence gap`: the model or measurements are too weak to choose reliably.
- `statistical gap`: apparent movement may be noise.

A plateau is not a floor proof. Use `proven lower bound` only when required-work counts, throughput assumptions, dependencies, and unavoidable costs establish the bound. Otherwise call the result a `model floor` or `observed plateau` and keep structural alternatives open.

Do not micro-tune below a proven floor. Change work graph, representation, primitive, route, specialization, or a contract-valid approximation. Treat inherited gap classifications and closed hills as hypotheses unless backed by current evidence.

Separate contract semantics, enforcement behavior, and the rejected implementation form. A scanner, compiler, sandbox, or policy rejection closes only the observed syntax, API, tool, or execution form unless the contract forbids the broader mechanism. Never evade forbidden semantics. When the semantics are allowed but enforcement is broader than the written rule, seek a transparent contract-valid representation and validate it authoritatively.

Mechanism families include work deletion or fusion, resource transfer, tail or dependency change, scheduler or variance change, representation or primitive or route change, contract specialization, tolerance-gated approximation, and forbidden shortcut.

## Search Health

Track the current mechanism family, actual measured attempts in that family, consecutive same-family candidates without meaningful promotion, active contract budget since meaningful promotion, and whether the next candidate must be off-hill.

A measured attempt is each configuration, seed or draw, scheduler result, generated artifact, or authoritative evaluation consumed to choose or defend a search family. A batch or sweep reports its total attempts; wrapping thousands of evaluations in one candidate does not reset stagnation. Fixed correctness samples still consume contract budget, but do not create fake candidate promotions.

Same-artifact checkpoints, repeated verification, pings, token snapshots, and report refreshes are operational work, not optimization candidates or promotions. They do not reset the promotion drought.

Unless the user explicitly sets different thresholds, trigger reassessment when any condition holds:

1. Three consecutive same-family measured candidates fail to improve the authoritative metric outside noise.
2. Ten percent of the active contract budget passes without a meaningful promotion.
3. A written sweep or family attempt budget is exhausted.

The user may override either direction when the contract justifies it. Set an attempt budget and stop rule before every sweep.

At the trigger, stop the current sweep, mark the hill `CLOSED` or `NARROWED`, state the failed prediction or missing evidence in one sentence, name at least three genuinely different mechanism families, and spend the next measured candidate off-hill. Continue the old family only with an explicit new premise such as new evidence, a changed graph, a calibrated search tool, or a previously untested range justified by the model. More equivalent seeds or configurations are not a new premise.

## Promotion

Never promote from a screening metric. Promote only when the candidate:

- Computes the required output for valid inputs.
- Passes the required correctness scope or authoritative acceptance gate.
- Improves the authoritative metric outside known noise.
- Survives relevant shapes, seeds, hardware, hidden cases, or production guardrails.
- Remains valid under the stated contract.

After a meaningful promotion, update the protected best and reset the promotion-drought state. Near ties favor the simpler, smaller, less stateful artifact. Keep target-specific variants separate when one candidate wins only a lane, shape, seed regime, or hardware target.

Reject wrong-answer speedups, leaked or hardcoded answers, stale-state wins, hidden-test detection, skipped required work, grader or harness modifications, and any contract-invalid shortcut.

## Push, Reassess, Escape

Keep pushing a hill while the authoritative metric improves, a proven bottleneck signal moves as predicted, implementation bugs explain failures, or a justified bracket remains within its attempt budget. When the search-health trigger fires, obey the off-hill transition instead of documenting or relabeling the same family.

When a materially faster artifact or source becomes available, compare its algorithm, phase graph, representation, hardware mapping, precision, repair, routing, and lifecycle with the protected best. Audit prior negative verdicts against the new premises before choosing the next hill. See `references/frontier-introspection.md`.

If repeated wrapper, primitive, or isolated-phase substitutions fail to move the measured owner and the remaining gap exceeds their plausible gain, reserve a bounded branch for an integrated architecture. Define its phase contract, milestones, budget, route attestation, and kill criteria; diagnose components separately, but promote only end to end.

For detailed floor analysis and escape operators, read `references/resource-models.md`. For measurement quality, variance, profiling, search accounting, and external-technique intake, read `references/evidence-loop.md`.

## Multi-Agent Mode

Default is `off`. Enable only when the user asks or the `/goal` says `Multi-agent mode: on`.

Give each worker one isolated mechanism hypothesis from a named parent. The coordinator protects the canonical best, checks parent staleness, and serializes promotion through correctness and the authoritative metric. After a plateau trigger, allocate at least one worker off-hill. When Scorebench is active, it owns run coordination metadata and observability; do not add a second local ledger.

## Finish

Default reporting is concise: state the best artifact, authoritative result, validation status, and the next blocker or direction. If the run stops on a plateau, state the closed or narrowed hill and the next off-hill candidate. Produce a durable handoff, audit, dashboard, or detailed experiment report only when the user explicitly requests one or an active external harness requires it.

## References

| Need | Read |
|---|---|
| Measurement, profiling, variance, blockers | `references/evidence-loop.md` |
| Winning-source introspection and verdict audits | `references/frontier-introspection.md` |
| Floors, tails, primitive inversion, local optima | `references/resource-models.md` |
| Simulator, policy, hidden seeds | `references/stochastic-policy-search.md` |
| CPU optimization | `references/cpu-architecture.md` |
| GPU optimization | `references/gpu-architecture.md` |
| Common problem families | `references/problem-families.md` |
