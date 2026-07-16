---
name: problem-agnostic-optimization
description: "Use when improving a measured artifact under a correctness or scoring contract: performance, latency, throughput, leaderboard score, CPU/GPU kernel time, or stochastic policy quality. Runs a lean evidence loop: objective, baseline, protected best, bottleneck model, one-hypothesis candidates, authoritative promotion, and plateau escapes. Logging and reporting are optional external concerns; when Scorebench is active, Scorebench owns them."
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
- Multi-agent mode, defaulting to `off`.

Use `/goal` for a substantial or long-running optimization. If the user asks for a goal "for later", return a copy-paste prompt beginning with `Use problem-agnostic-optimization.` and a filled `/goal` block; do not activate a goal unless explicitly asked.

Use the current workspace and user-provided evidence by default. Do not mine sibling workspaces, old candidates, or prior submissions unless the user asks for transfer or continuation.

## Core Loop

1. Reproduce the baseline with the authoritative command or service.
2. Preserve the current best artifact before risky edits.
3. Build the cheapest useful bottleneck model from measurements, profiles, counters, case splits, or resource floors.
4. Choose one falsifiable hypothesis and make the smallest edit that tests it.
5. Validate correctness before performance when possible.
6. Measure with the authoritative metric.
7. Decide `PROMOTE`, `KEEP VARIANT`, `REJECT`, `BUG`, or `BLOCKED`.
8. Update the bottleneck model after a promotion or surprising regression.
9. Continue while the hill has signal; change hill when same-family candidates tie or regress.

For a candidate, keep only the information needed to make the next decision: parent, hypothesis, expected signal, kill criterion, validation, measurement, and decision. A compact line or active plan is enough. Do not create per-candidate dossiers by default.

## Optional Observability

Optimization and observability are separate modules.

Default behavior is no logging subsystem. Do not initialize a local optimization harness or create `progress.tsv`, `events.jsonl`, `log.md`, `state.json`, charts, dashboards, audit reports, token ledgers, or candidate JSON files unless the user explicitly requests local persistence. Normal benchmark outputs, profiler captures, submitted artifacts, and files required by the target contract are not optional logging.

When Scorebench is active - because the user invokes it, provides a scoped Scorebench run, or the task is assigned through Scorebench - follow the `scorebench` skill for run lifecycle, submissions, token accounting, history, best-state tracking, logging, and reports. Do not create parallel PAO logs or dashboards, do not duplicate token accounting, and do not submit directly to the underlying venue. PAO supplies only the optimization strategy and candidate decisions.

If the user explicitly requests local persistent logging while Scorebench is inactive, use a separate logging skill or module selected for that task. Keep it sidecar to the candidate loop. A logger or renderer failure must not block optimization unless logging is part of the user's stated contract.

Never run local and Scorebench logging in parallel. If a run moves to Scorebench, stop local logging rather than backfilling or mirroring it.

## Gap And Candidate Choice

Classify the current gap before choosing a candidate:

- `floor gap`: the current graph or family cannot reach the target under the current resource model.
- `schedule gap`: the graph can reach the target, but runtime is lost to packing, tail, dependencies, resource pressure, synchronization, allocation, or variance.
- `evidence gap`: measurements are too weak to select a mechanism confidently.
- `statistical gap`: the apparent movement may be noise.

Do not micro-tune below a proven floor. Change work graph, representation, primitive, route, specialization, or a contract-valid approximation. Treat inherited gap classifications and closed hills as hypotheses unless backed by current evidence.

Mechanism classes:

- Work deletion or fusion.
- Resource transfer.
- Tail or dependency reduction.
- Scheduler or variance change.
- Representation, primitive, or route change.
- Contract specialization.
- Tolerance-gated approximation.
- Forbidden shortcut.

## Promotion

Never promote from a screening metric. Promote only when the candidate:

- Computes the required output for valid inputs.
- Passes the required correctness scope or authoritative acceptance gate.
- Improves the authoritative metric outside known noise.
- Survives relevant shapes, seeds, hardware, hidden cases, or production guardrails.
- Remains valid under the stated contract.

Near ties favor the simpler, smaller, less stateful artifact. Keep target-specific variants separate when one candidate wins only a lane, shape, seed regime, or hardware target.

Reject wrong-answer speedups, leaked or hardcoded answers, stale-state wins, hidden-test detection, skipped required work, grader or harness modifications, and any contract-invalid shortcut.

## Push, Reassess, Escape

Keep pushing a hill when the authoritative metric improves, a proven bottleneck signal moves in the predicted direction, implementation bugs explain failures, or an untested bracket remains.

Reassess when three same-family candidates tie or regress, resource improvements repeatedly fail to move the target, reruns put the target outside plausible variance, or the bottleneck model stops predicting results.

After reassessment, spend the next candidate off-hill by default. Try a different representation, primitive, route, target split, specialization, search tool, or external mechanism. A plateau closes a hill, not the problem; only a lower-bound proof can establish that the target is unreachable.

For detailed floor analysis and escape operators, read `references/resource-models.md`. For measurement quality, variance, profiling, and external-technique intake, read `references/evidence-loop.md`.

## Multi-Agent Mode

Default is `off`. Enable only when the user asks or the `/goal` says `Multi-agent mode: on`.

Give each worker one isolated hypothesis from a named parent. The coordinator protects the canonical best, checks parent staleness, and serializes promotion through correctness and the authoritative metric. Workers return only the candidate artifact or patch plus compact evidence. When Scorebench is active, it owns run coordination metadata and observability; do not add a second local ledger.

## Finish

Default reporting is concise: state the best artifact, authoritative result, validation status, and the next blocker or direction. Produce a durable handoff, audit, dashboard, or detailed experiment report only when the user explicitly requests one or an active external harness requires it.

## References

| Need | Read |
|---|---|
| Measurement, profiling, variance, blockers | `references/evidence-loop.md` |
| Floors, tails, primitive inversion, local optima | `references/resource-models.md` |
| Simulator, policy, hidden seeds | `references/stochastic-policy-search.md` |
| CPU optimization | `references/cpu-architecture.md` |
| GPU optimization | `references/gpu-architecture.md` |
| Common problem families | `references/problem-families.md` |
