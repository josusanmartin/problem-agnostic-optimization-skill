# Multi-Agent Portfolio

Use this reference only when multi-agent mode is explicitly enabled and parallel workers will explore, compare, or audit more than one mechanism family. Keep it unloaded for single-agent work or one delegated implementation task.

## Contents

- Portfolio contract and independent seeding
- Family registry and dynamic allocation
- Progress, blocking, and cross-pollination
- Adversarial review and coordinator rounds
- Worker return packets and observability

## Set The Portfolio Contract

Before dispatch, state the shared objective, authoritative metric, protected best, correctness gate, editable scope, budget, target, and stopping rule. Set no fixed worker quota by strategy. Size and reallocate the portfolio from expected information or gain per cost.

Give every worker:

- The same contract and current authoritative baseline.
- One named parent artifact or commit.
- One distinct mechanism family, falsifiable premise, expected signal, budget, and kill criterion.
- The exact artifact or evidence packet it must return.

Do not assign several workers to superficial variants of one idea while major families remain untested. Duplicate a family only for explicit replication, independent derivation, adversarial review, or a clearly separable implementation branch.

## Preserve An Early Independent Round

Seed genuinely different mechanism families before sharing a favored strategy. During each worker's first round, disclose the contract, parent, validated facts, and assigned family, but not other workers' proposed mechanisms or the coordinator's preferred answer.

Require one concrete packet from each family before synthesis. Early independence is complete when a worker returns a candidate, proof, counterexample, discriminating measurement, or scoped blocker. Time alone or a status update does not complete the round.

Keep materially incompatible routes alive when the remaining budget can still discriminate them. Do not let an elegant reduction, an early noisy win, or several similarly worded reports collapse the portfolio without authoritative evidence.

## Maintain A Mechanism Registry

Keep one compact active registry, grouped by underlying mechanism rather than wording:

```text
family | premise | parent | occupancy | status | concrete evidence | blocker | reopen condition | next decision
```

Use `OPEN`, `PROMISING`, `AUDIT`, `BLOCKED`, `CLOSED`, or `PROMOTED`. Treat renamed constants, seeds, prompts, schedules, or selectors inside the same causal mechanism as one family.

After each return:

1. Merge duplicate families and keep the strongest packet.
2. Check whether any family is crowded relative to its evidence.
3. Redirect redundant workers toward untested families, independent audit, or the weakest bottleneck assumption.
4. Allocate follow-up capacity by expected information or gain per cost, not by initial assignments or worker enthusiasm.
5. Preserve at least one incompatible route while it remains plausible and affordable.

When several workers independently converge on one family, retain the best-positioned owner and redirect the rest unless replication itself is the test. A family earns more capacity only through concrete signal, not elegance or repetition.

## Count Progress Honestly

A reformulation or reduction counts as progress only when it supplies at least one of:

- A strictly smaller or cheaper subproblem with a validated bridge back to the target.
- An executable candidate or construction that can face the correctness and authority gates.
- A proof, bound, invariant, or counterexample that closes measurable search space.
- A new diagnostic that changes the next decision.

If the route stops at an unresolved lemma, compatibility condition, optimizer, or construction equivalent in strength to the original target, mark it `BLOCKED`, not nearly complete. Reopen it only with a materially new mechanism, invariant, construction, proof tool, or changed authoritative evidence.

Do not count summaries, reductions without leverage, unverified claims, or duplicate local variants as independent progress.

## Cross-Pollinate After Evidence

Cross-pollinate only after the independent round exposes each family's actual signal and gap. The coordinator may then share validated transferable facts, counterexamples to subclaims, resource limits, and interface constraints.

Launch a hybrid family only when the transfer names a new causal mechanism or removes a specific blocker. Do not broadcast one favored solution and relabel dependent variations as portfolio diversity.

## Assign Adversarial Review

For any candidate that could replace the protected best, relax a contract assumption, or claim a proof or counterexample, assign an independent reviewer when capacity permits. The author must not be the sole verifier.

Derive a challenge-specific failure checklist from the contract. At minimum, challenge:

- Whether the intended path executed from the named parent.
- Correctness, hidden assumptions, stale state, and target coverage.
- Authority, variance, comparability, and claimed causal mechanism.
- Forbidden shortcuts, leaked information, skipped work, or representation tricks.
- Confusion between surrogate and authority, local and global behavior, or formal and executable results.
- Exactness and nontriviality of any claimed proof, bound, or counterexample.

Return `CONFIRMED`, `PLAUSIBLE`, or `REFUTED` with the concrete trigger and evidence. Only the coordinator may move an audited candidate through the normal promotion gate.

## Run Coordinator Rounds

Repeat a bounded round until the target, contract budget, or stopping rule ends the run:

1. Snapshot the protected best and invalidate stale parents.
2. Audit registry occupancy, missing families, and blocked routes.
3. Dispatch independent mechanism or adversarial packets.
4. Collect only concrete returns and merge duplicate evidence.
5. Validate, measure, promote, close, or narrow through the core rules.
6. Reallocate the next round dynamically.

After a plateau trigger, assign new capacity off-hill before adding another same-family worker unless an explained bug or predeclared bracket justifies the exception. Serialize promotion so parallel workers cannot overwrite the canonical best or each other.

## Require A Concrete Worker Packet

Require this compact return shape:

```text
family | parent | artifact/patch/proof | hypothesis | validation | authoritative result or blocker | decision | reopen condition
```

Reject vague optimism and status-only reports. A blocker packet must name the failed premise, evidence, and what materially new fact would reopen it.

## Keep Observability External

The registry is active coordination state, not a logging subsystem. When Scorebench is active, derive worker history, attempts, budgets, and promotions from Scorebench and do not mirror them locally. Otherwise keep the registry in compact active context unless the user explicitly requests a persistence sidecar.
