# Frontier Introspection

Use this reference after a materially faster artifact, winning source, production rewrite, paper implementation, or postmortem becomes available. Convert the gap into candidates rather than a retrospective.

## Preserve Comparable Evidence

Retain only what makes the comparison reproducible: artifact/source identity, score, hardware and contract, build path, timed lifecycle, protected parent, and whether each claim is observed, authored, or inferred. Use the active external harness when present; do not initialize a local history system.

## Triangulate Multiple Frontiers

When multiple faster artifacts exist:

- Separate independent lineages from copied source or build artifacts.
- Compare each with the protected best and with the others under matching contracts.
- Identify shared algorithm, phase graph, representation, hardware mapping, precision/repair, routing, and lifecycle choices.
- Rank shared differences as hypotheses; keep source-unique details `unknown` until ablated.

Independent agreement raises priority, not certainty. Never combine incompatible hardware, timing boundaries, or correctness scopes into false consensus.

## Diff The Architecture

Compare only dimensions that can explain the gap:

```text
contract/enforcement | timed boundary | algorithm/DAG | mapping/resources
representation/precision | specialization | state/lifetime | toolchain/repair
```

Label each difference `causal`, `enabling`, `incidental`, or `unknown`. Port the cheapest difference capable of changing the current floor or bottleneck; do not copy the winner wholesale.

Prove the intended frontier route executed before interpreting it. Check the expected module or artifact, attest the route with a trace/marker/counter or fail-loud diagnostic, remove intrusive diagnostics, then measure normally. Broad fallbacks can silently measure the parent.

## Audit Negative Verdicts

Revisit only closures touched by the frontier mechanism. Use the narrowest valid label:

- `algorithm-negative`: a mature integrated route loses under the same contract.
- `implementation-negative`: the tested implementation was immature.
- `mapping-negative`: the tested mapping loses; another mapping remains open.
- `integration-negative`: precision, layout, order, or boundary transfer was wrong.
- `attachment-negative`: an unchanged parent bottleneck hid the mechanism.
- `availability-negative`: required hardware, tool, library, or build path was absent.
- `enforcement-negative`: one representation was rejected while allowed semantics remain open.
- `measurement-invalid`: fallback, stale code, wrong route, or lifecycle invalidated timing.

Never reopen forbidden semantics by disguising them. Never close an algorithm from an unavailable tool, fallback timing, or stage-only prototype.

## Co-Design Coupled Mechanisms

An algorithm may require a different schedule, storage layout, precision boundary, certificate/repair path, code-generation route, or adjacent phase before it can win. Use component ablations to understand the system, but budget one faithful integrated candidate when local pieces are expected to regress in isolation.

## Write The Phase Contract

For an integrated route, specify only boundaries that can fail:

- Representation, dtype, layout, ownership, normalization, and metadata.
- Buffer aliasing, workspace, synchronization, and lifetime.
- Critical scalars, certificate, repair/retry, fallback, and expected rates.

Evaluate the phase graph end to end; a losing component can enable a winning route by deleting conversion, materialization, traversal, synchronization, or a second solve.

## Keep A Precision Ledger

Use one compact row per distinct precision boundary:

```text
phase/state | storage | products/accumulation | critical scalar | certificate | repair
```

Scope failures to the tested boundary. Low-precision storage does not imply a low-precision output contract.

## Reserve An Architecture Budget

Open a bounded integrated branch when repeated local substitutions do not move the measured owner, their plausible gain is below the remaining gap, and the frontier points to a different phase graph.

Protect the best; set time/candidate/submission and kill budgets; exercise the complete phase contract on the cheapest representative case; require route attestation, correctness, integrated execution, and authority. Do not let cheap local candidates consume this branch budget.

## Diagnose With Stage Cuts

When full profiling is unavailable, use an attested prefix, controlled suffix replacement, or phase stop with comparable inputs, setup, warmup, and route markers. Stage cuts diagnose ownership only; never promote them, sum incompatible cuts, or infer an end-to-end win from one fast phase.

## Convert Hindsight Into Search

Retain three outputs:

1. Mechanism map: consensus and architecture differences with causal/enabling labels.
2. Verdict corrections: old closures narrowed, superseded, or retained with evidence.
3. Next probe: cheapest falsifiable transfer, integrated target, budget, and kill.

Ask when the clue first existed, what belief blocked it, and what affordable probe could have changed the decision. Add persistent fields only when an observability module is active.

Reject lessons that depend on leaked answers, hidden-test constants, falsified work, forbidden concurrency, disguised policy violations, or moving counted work outside the contract.
