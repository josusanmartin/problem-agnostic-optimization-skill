# Frontier Introspection

Use this reference after a materially faster artifact, winning source, production rewrite, paper implementation, or postmortem becomes available. Convert hindsight into new search behavior instead of merely explaining the result.

## Contents

- Evidence preservation and multi-frontier triangulation
- Architecture diff, verdict audit, and execution attestation
- Co-designed phases, precision, and architecture budgets
- Counterfactual lessons and integrity gate

## Preserve The Evidence

Establish before analysis, using the active plan or the active external harness when one exists:

- Exact artifact, source snapshot, commit or submission ID, score, hardware, and contract.
- Build and generation path, including downloaded or prelinked components.
- Timed lifecycle boundary: import, compile, JIT, warmup, precompute, capture, replay, and teardown.
- Which claims are observed in source or traces, which are author comments, and which are inference.
- Current protected best and the compact active state or external-harness record being compared.

If persistent history is active, append a superseding interpretation rather than rewriting old entries. Otherwise retain the original evidence and corrected interpretation together in the active context.

## Triangulate Multiple Frontiers

When two or more materially faster artifacts are available, compare them with each other before treating either one as the blueprint:

- Check provenance, common ancestry, copied modules, shared authorship, and shared build artifacts. Two submissions with the same underlying source are one evidence lineage, not independent confirmation.
- Quantify both the protected-best gap and the frontier-to-frontier spread under the same contract. A small spread between independent architectures is stronger evidence about the reachable tier than one isolated score.
- Build a consensus matrix of shared algorithm, phase graph, representation, hardware mapping, precision, repair, routing, and lifecycle choices.
- Promote shared differences to high-priority hypotheses, not facts. They still need an ablation or faithful port.
- Keep source-unique details labeled `unknown` until measured. A winner comment, import, constant, or large source file is a clue, not causal evidence.

Use independent agreement to rank probes. Do not average incompatible contracts, hardware, timed boundaries, or correctness scopes into false consensus.

## Run The Architecture Diff

Compare the frontier artifact with the protected best across every dimension. Do not stop at imports or the headline algorithm.

| dimension | questions |
|---|---|
| Contract and enforcement | What does the rule forbid semantically? What did the scanner, checker, sandbox, or compiler reject syntactically? |
| Timed boundary | Which expensive work moved to import, generation, warmup, capture, caching, or offline build? Is that movement contract-valid? |
| Algorithm | What decomposition changes asymptotic work, conditioning, or available parallelism? |
| Dependency DAG | Which phases are serial, sibling, pipelined, overlapped, fused, or recomputed? What is the true critical path? |
| Hardware mapping | How are work units mapped to lanes, blocks, clusters, cores, memory engines, or devices? |
| Representation | Which data changes dtype, layout, compression, sparsity, ownership, or storage location? |
| Precision and repair | Which state is approximate, which scalars remain precise, what certificate detects failure, and what repairs it? |
| Specialization and routing | Which shapes, distributions, regimes, or contracts get independent routes? |
| State and lifetime | Which buffers, descriptors, graphs, handles, workspaces, or outputs are reused, aliased, or kept alive? |
| Toolchain and generation | Is the frontier hand-written, generated, template-instantiated, prelinked, autotuned, or assembled from libraries? |
| Correctness recovery | Where are residual checks, purification, fallback, retries, or accurate subroutes placed? |

For each difference, label it:

- `causal`: evidence shows it moves the authoritative metric.
- `enabling`: it makes another causal mechanism viable.
- `incidental`: present but not plausibly important.
- `unknown`: needs an ablation or probe.

## Audit Negative Verdicts

Revisit prior rejections that touch the frontier mechanism. Assign the narrowest valid verdict:

- `algorithm-negative`: a mature, integrated, co-designed implementation proves the decomposition itself loses under the same contract.
- `implementation-negative`: the tested implementation is immature, underparallelized, unstable, or otherwise unrepresentative.
- `mapping-negative`: the tested thread, block, tile, layout, schedule, or device mapping loses; the algorithm remains open under another mapping.
- `integration-negative`: the mechanism is sound but its precision, layout, ordering, or API boundary was transferred incorrectly.
- `attachment-negative`: the candidate replaced one phase while an unchanged parent bottleneck dominated end to end.
- `availability-negative`: the required library, compiler, profiler, device feature, build path, or runtime was unavailable; performance remains undecided.
- `enforcement-negative`: one syntax, API, tool, or execution form was rejected; broader semantics remain undecided.
- `measurement-invalid`: fallback, stale code, failed build, wrong route, warmup, or harness behavior means the mechanism was not measured.

Never close an algorithm from a fallback timing, an unavailable tool, a stage-only prototype, or a mapping whose own bottleneck is unrelated to the intended steady-state design. Never reopen a genuinely forbidden mechanism by disguising it.

## Require Execution Attestation

Before interpreting correctness or timing, prove the intended path ran:

1. Make optional compilation and route selection fail loud for one diagnostic candidate.
2. Confirm the expected module, symbol, generated artifact, or cached object exists.
3. Confirm the expected route with a trace, profile kernel name, route marker, counter, or deliberate diagnostic perturbation.
4. Remove intrusive diagnostics, then rerun the authoritative candidate.

Treat swallowed exceptions and broad fallbacks as measurement hazards. A passing result can still measure the parent.

## Separate Semantics From Representation

Model three layers:

1. Written contract and policy intent.
2. Enforcement behavior observed from scanners, checkers, sandboxes, compilers, or runtime guards.
3. The specific implementation representation that triggered enforcement.

A rejection at layer 3 does not prove the broader mechanism impossible. Enumerate transparent contract-valid representations before closing the class. For concurrency, these may include dependency-graph scheduling, batch chunking, cooperative groups, hardware clusters, producer-consumer pipelining, or fusion rather than an explicitly forbidden execution API.

Do not bypass actual policy. If the semantics are forbidden, close the mechanism. If semantics are allowed but enforcement is overbroad, document the mismatch and use only an accepted representation that preserves the rule's intent.

## Look For Co-Designed Mechanisms

Do not evaluate an algorithm independently of the substrate that makes it useful. Ask:

- Does the algorithm expose parallel work that the current runtime leaves serial?
- Does a new schedule require different storage, precision, or buffer lifetime?
- Does low precision become valid only with scaling, a certificate, and terminal repair?
- Does a factorization produce a complementary output that deletes a second solve or traversal?
- Does fixed-shape code generation remove dynamic dispatch, setup, or generic tails?
- Does a phase replacement matter only after its parent or child phases are rebuilt too?

When mechanisms are coupled, use staged ablations for understanding, but budget one integrated candidate. Local pieces may regress while the complete architecture wins.

## Write The Phase Contract

For an integrated route, specify every boundary between adjacent phases:

- Input and output representation, dtype, layout, ownership, and normalization.
- Metadata and complementary outputs produced once and consumed later.
- Buffer aliasing, workspace, synchronization, and lifetime across capture or replay.
- Critical scalars that require higher precision than the bulk carrier.
- Certificate, repair, retry, and fallback behavior, including their expected rates and costs.

Evaluate the phase graph as a system. A component that loses in isolation can still enable a faster end-to-end route by deleting conversion, materialization, traversal, synchronization, or a second solve.

## Keep A Precision Ledger

Record precision by phase and state rather than assigning one dtype to the whole algorithm:

| phase or state | carrier/storage | products/accumulation | critical scalars | certificate | repair/fallback |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

Low-precision storage or transport does not imply a low-precision output contract. Scope failures to the tested boundary: unscaled carrier, weak accumulation, missing certificate, expensive repair, or inaccurate terminal solve.

## Reserve An Architecture Budget

A practical trigger for a bounded end-to-end architecture branch is:

- About three independent wrapper, primitive, or local phase substitutions failed to move the measured owner; and
- The remaining gap is larger than the plausible gain from another wrapper-level change; and
- A frontier artifact or resource model points to a different integrated phase graph.

When triggered:

1. Protect the current best and assign explicit candidate, time, submission, and implementation budgets to the branch.
2. Start with the cheapest representative case that exercises the complete phase contract, not a microbenchmark that omits the hard boundaries.
3. Define milestones for build, route attestation, correctness, stage ownership, integrated execution, and authoritative measurement.
4. Define kill criteria for impossible resource use, failed invariants, unrepairable correctness, or a measured integrated floor above target.
5. Allow diagnostic components to regress while the architecture is incomplete; only the integrated route can promote.

Do not let a stream of cheap local candidates consume the architecture budget. A much larger or generated frontier implementation is a planning signal that the route may require real systems work; it is not evidence that source volume itself causes speed.

## Diagnose With Stage Cuts

When a full profiler is unavailable, create diagnostic variants that stop after an attested phase boundary, replace a suffix with a controlled sink, or run a representative prefix. Keep inputs, warmup, setup boundary, and route markers comparable.

Use stage cuts to estimate ownership and critical-path changes. Never promote a stage-cut result, infer end-to-end speedup by summing incompatible cuts, or treat a fast isolated phase as an algorithm-level win.

## Run The Counterfactual Timeline

For each enabling idea, identify:

- First date or candidate when the clue existed.
- Belief or anti-revisit rule that blocked it.
- Evidence strength behind that belief at the time.
- Cheapest probe that could have falsified the belief.
- Whether the probe was affordable before the deadline or budget limit.
- Process change that would trigger the probe earlier next time.

Judge the process using evidence available then, not only the final answer. Preserve correct decisions and change only rules that were overbroad, weakly supported, or missing an aspiration condition.

## Convert Hindsight Into Candidates

Carry three results into the next search decision:

1. **Mechanism map**: cross-frontier consensus and architecture differences with causal/enabling labels.
2. **Verdict corrections**: old closures narrowed, superseded, or retained with explicit evidence.
3. **Next-run rules**: concrete trigger, architecture budget, probe, and kill criterion; add a persistent field only when an observability module is active.

For every transferable mechanism, define the cheapest falsifiable probe and an integrated target candidate. Do not reduce the lesson to "write more custom code" or "use the winner's library."

## Integrity Gate

Reject any generalization that depends on leaked answers, hidden-test constants, falsified work, forbidden concurrency, disguised policy violations, or moving counted work outside the timed region contrary to the contract. Preserve useful architectural lessons only when they remain valid under the written objective and enforcement intent.
