---
name: problem-agnostic-optimization
description: "Use when improving a measured artifact under a correctness or scoring contract: performance, latency, throughput, leaderboard score, CPU/GPU kernel time, or stochastic policy quality. Runs an evidence loop: objective, baseline, protected best, bottleneck model, one-hypothesis candidates, authoritative promotion, plateau escapes, and optional coordinator-led multi-agent exploration."
---

# Problem-Agnostic Optimization

Loop:

```text
contract -> baseline -> bottleneck model -> candidate -> validate/measure -> decide -> iterate or escape
```

Only the authoritative metric promotes. Everything else explains.

## Always

1. Set the objective and authoritative metric before editing.
2. Reproduce or establish the baseline; if unknown, mark it `unknown, reproduce first`.
3. Preserve the current best artifact.
4. Define editable and immutable files.
5. Test one hypothesis per candidate.
6. Validate correctness before performance when possible.
7. Promote only by the authoritative metric.
8. If same-family candidates tie or regress, change hill.
9. Reject wrong-answer, leaked-answer, stale-state, harness/grader, or invalid-contract wins.

## Contract

Record objective, mode, authoritative metric, baseline, edit surface, budget, validation, evidence availability, and `Multi-agent mode: on|off`.

If the user asks to prepare, draft, write, fill, or format a goal "for later", return a copy-paste prompt that starts with `Use problem-agnostic-optimization.` and then includes the filled `/goal` block. Do not create, activate, start, or persist an active goal unless the user explicitly asks to start the optimization run now.

If no target is given, find a public best, prior local best, paper result, production SLO, or theoretical/resource floor. If none is available, set an ambitious measurable floor and label the uncertainty.

Use minimal notes only for tiny one-shot tasks that do not use `/goal` and do not need persistence.

## Harness Trigger

Harness deployment is default-on for every substantial `/goal` run, leaderboard/challenge run, production optimization, open-ended run, remote/noisy/rate-limited run, auditor-reviewed run, multi-agent run, or run with `Progress chart: on`.

Before baseline or candidate work, read `references/harness.md` and initialize the harness. Fast path: run the bundled `scripts/init_harness.py` if available; otherwise create the same files manually:

```text
work/audit.md
work/best.md
work/breakthroughs.md
work/checkpoints/progress.json
work/candidates/_template.result.json
work/dashboard.html
work/events.jsonl
work/log.md
work/plan.md
work/promotion_ladder.md
work/progress.tsv
work/progress.svg
work/review.md
work/schemas/candidate_result.schema.json
work/state.json
work/verifier.md
```

Only skip harness deployment when the task is explicitly tiny or the user disables persistence. If you skip it, record the skip reason in your response or notes.

## Progress

For substantial runs, progress artifacts are default-on unless the `/goal` says `Progress chart: off`.

Before the first candidate, initialize `work/progress.tsv`, `work/log.md`, and the `progress` fields in `work/state.json`. After every measured candidate, try to capture current usage, append one candidate row to `work/progress.tsv`, regenerate `work/progress.svg` and `work/dashboard.html`, and refresh `work/review.md`. Use the bundled `scripts/record_progress.py` when available; hand-write TSV rows only when the script is missing. If the chart/dashboard scripts are unavailable or a result cannot be charted yet, write the blocker into `work/log.md` or `work/review.md`; do not silently skip progress artifacts.

`work/progress.tsv` is the score ledger. New runs must include these columns in every row: `timestamp`, `candidate`, `score` or another authoritative metric column, `decision`, `tokens_total`, `tokens_delta`, `wall_seconds`, and `label`. Timestamps must be UTC snapshots in `YYYY-MM-DDTHH:MM:SSZ` form. Token/time values may be blank when unavailable, but do not omit the columns. Do not use candidate count as a proxy for resource burn.

Token history comes from explicit `get_goal` usage snapshots recorded in `work/log.md`, not from interpolation across candidates. In Codex, always try to call `get_goal` after each measured candidate and append the raw or structured snapshot to `work/log.md` with UTC timestamp, elapsed wall time, total tokens, token delta since the previous snapshot when known, and all available token fields: input, cached input, output, reasoning output, cache creation, and cache read. Copy the latest snapshot into `work/state.json` under `progress.latest_usage_snapshot`. If early token history is missing, mark it as unknown; do not backfill or invent per-candidate token deltas.

The SVG chart has two panels: the top plots authoritative score by candidate number with a protected-best curve and optional target line; the bottom plots recorded token snapshots by elapsed wall time. Candidate count is the right x-axis for score progress. Elapsed wall time is the right x-axis for token burn.

## Gap

Classify the gap before choosing a candidate:

- `floor gap`: the current graph or family cannot reach target.
- `schedule gap`: the graph can reach target, but runtime is lost to packing, tail, dependencies, resource pressure, synchronization, allocation, or variance.
- `evidence gap`: measurement, profiling, counters, logs, traces, or static models are too weak.
- `statistical gap`: the apparent improvement may be noise.

Do not micro-tune below the current floor. Move to work deletion, fusion, specialization, representation change, primitive change, route change, or valid approximation inside tolerance.

A gap classification is a revisable hypothesis, not a fact, especially when inherited from a prior session, handoff, or ledger. `floor gap` means "no known path reaches target," not "the target is unreachable": that verdict needs a lower-bound proof (a resource floor at or above target), never a plateau of failed candidates. Re-test an inherited negative conclusion when a new premise appears: a user hint, an external writeup, a new tool, compiler, or hardware.

## Candidate

For each candidate, state: parent, parent hash when available, hypothesis, mechanism, duplicate check, expected signal, kill criterion, smallest edit, validation, measurement, and decision. For substantial runs, save a typed candidate result under `work/candidates/`. For tiny/minimal runs, a compact log entry is enough unless the candidate is promoted or risky.

Mechanism class: work deletion | resource transfer | tail/dependency | scheduler/variance | representation/primitive/route change | contract specialization | approximation | forbidden shortcut.

Decision: `PROMOTE` | `KEEP VARIANT` | `REJECT` | `BUG` | `BLOCKED`.

Never promote from a screening metric. Promotion should pass the ladder in `work/promotion_ladder.md`; meaningful promotions should also run or explicitly limit the fresh verifier gate in `work/verifier.md`. Near ties favor the simpler, smaller, less stateful artifact. After a promotion or surprising regression, update the bottleneck model before choosing the next candidate.

## Multi-Agent Mode

Default is `Multi-agent mode: off`. Enable only when the `/goal` says `Multi-agent mode: on` or the user explicitly asks for parallel workers. Use it only after the contract, protected best, and durable ledger exist. Workers run isolated one-hypothesis candidates from a named parent. The coordinator owns canonical files and promotion. Promotion remains serial and authoritative. For the worker packet and batch protocol, read `references/harness.md`.

## Push Or Reassess

Keep pushing the current hill when at least one is true:

- The last candidate improved the authoritative metric.
- The candidate improved a proven bottleneck signal and the target gap is still plausibly reachable.
- Failures are implementation bugs, not evidence against the mechanism.
- A proven knob has not yet been bracketed.
- A kept variant wins a lane, shape, seed regime, or hardware target that can be composed or routed.

Reassess before the next candidate when any is true:

- Three same-family candidates tie, regress, or move less than noise.
- Better floors, counts, or counters repeatedly fail to improve the authoritative metric.
- The target is below the current resource or statistical floor.
- The same mechanism fails across independent formulations or target cases.
- Same-artifact reruns show the target is outside plausible variance.
- The bottleneck model cannot predict candidate results.

After reassessment, either continue with a narrower hypothesis and kill criterion, or mark the hill `CLOSED` and spend the next candidate off-hill.

For plateaued, high-stakes, public-leaderboard, or multi-agent runs, mine the frontier for breakthrough patterns before another local sweep and preserve the map in `work/breakthroughs.md`. Read "Breakthrough Mining" in `references/evidence-loop.md`.

Exception: when a `best-of-N` scoreboard or contract-allowed draw distribution can vary the recorded result, a *budgeted* distribution sweep (written plan + falsifiable stop, see `references/evidence-loop.md`) is sanctioned rather than churn. It either banks a best-of-N gain or supplies family-specific distribution evidence to close that draw family. It must self-terminate by its stop rule, not run open-ended.

## Escape

After repeated ties, regressions, same-knob failures, or a lower-bound proof against the current family, run a local-optimum audit:

- Current hill.
- Plateau evidence.
- Floor, tail, dependency, or statistical blocker.
- Three different hills.
- Cheapest off-hill probe.

After reassessment, mark exhausted hills `CLOSED` until a new premise appears. Spend the next candidate off-hill by default: representation, primitive, route/library/config, target split, or contract specialization.

If the audit says the run is stuck, use the escape ladder in `references/resource-models.md`: recognize the stuck signal, run a bounded divergence burst across genuinely different hills, then commit a short budget to any hill with a real mechanism signal before abandoning it.

Invert the primitive when compact work counts hide a target-specific bottleneck. Use negative audits to kill seductive shortcuts before implementing them.

A `CLOSED` hill is a local verdict, not a global one: closing every known hill does not prove the target unreachable. When the search has exhausted self-generated ideas, intake an external mechanism (a competitor writeup, public source, or paper) and port it before concluding a floor. See "External Technique Intake" in `references/evidence-loop.md`.

## Integrity

Before promotion, confirm the candidate computes the required output for all valid inputs, passes the required correctness scope, improves outside noise, uses current evidence, and remains valid under allowed input, seed, hardware, and hidden-case variation.

When uncertain, keep the candidate separate and report the risk.

## References

| Need | Read |
|---|---|
| Long/noisy/remote or multi-agent run | `references/harness.md` |
| Audit an active run from a second session | `references/auditor.md` |
| Floors, tails, primitive inversion, local optima | `references/resource-models.md` |
| Measurement, profiling, variance, blockers | `references/evidence-loop.md` |
| Simulator/policy/hidden seeds | `references/stochastic-policy-search.md` |
| CPU/GPU/domain probes | `references/cpu-architecture.md`, `references/gpu-architecture.md`, `references/problem-families.md` |
| Logs/handoffs | `references/templates.md` |
