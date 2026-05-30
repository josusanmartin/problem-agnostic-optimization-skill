# Stateful Stochastic Policy Search

Use this reference when the submitted artifact is a policy, controller, strategy, agent, scheduler, game bot, online decision rule, or other stateful action function evaluated by a stochastic simulator or hidden distribution.

This is a target family, not a domain-specific playbook. Only add a specific strategy when it maps to a reusable mechanism such as regime estimation, adaptive margins, flow/event classification, exposure control, participation control, competitor tracking, cooldown/decay, or tail-risk guarding.

## First Checks

Build the contract table:

- Action API: what the policy can observe, store, output, cancel, route, schedule, allocate, update, or abstain from.
- State API: visible state, hidden state, persistent memory, reset behavior, time index, and final-state semantics.
- Randomness: seeds, scenario generation, hidden parameters, stochastic actors, public/private differences, and reproducibility controls.
- Objective: mean score, edge, utility, profit, loss, win rate, p95, drawdown, constraint-adjusted score, or leaderboard-specific metric.
- Constraints: runtime, gas, compute units, storage, memory, language, sandbox, rate limits, invalid-action behavior, and submission budget.
- Baseline: current best artifact, current leaderboard or public reference score, local score distribution, and known variance.

## Evaluation Protocol

Do not promote from a single stochastic score unless the improvement is much larger than measured noise.

Use levels:

- `L0`: compiles, imports, validates, and obeys action constraints.
- `L1`: beats baseline on a cheap smoke scenario set.
- `L2`: beats baseline on matched scenarios using common random inputs when possible.
- `L3`: beats baseline on validation scenarios not used for tuning.
- `L4`: survives larger randomized evaluation with mean, standard error, and tail metrics.
- `L5`: improves the authoritative platform score.

Near-ties favor the simpler, safer policy.

## Scenario Sets

Maintain named scenario sets:

- `smoke`: tiny, fast, catches crashes and invalid actions.
- `train`: used for parameter search.
- `validation`: used for promotion.
- `holdout`: used rarely, only to detect overfit.
- `adversarial`: edge cases, extreme hidden parameters, budget exhaustion, empty flow, large shocks, high contention, or constraint-boundary cases.

When possible, compare candidate and parent on the same scenarios.

## Required Metrics

Record:

- Mean score.
- Median score.
- Standard deviation.
- Standard error.
- Min and max.
- `p05` and `p95`, or worst decile.
- Win rate versus parent on matched scenarios.
- Score by regime bucket.
- Crash or invalid-action rate.
- Constraint margin: runtime, gas, compute units, memory, storage, order/action count, or budget.

## Decomposition

Break the score into generic components when possible:

- Reward from benign or opportunistic events.
- Loss to informed, adversarial, or worst-case events.
- Opportunity cost from being too conservative.
- Tail loss or catastrophic paths.
- Resource or constraint cost.
- Inventory, exposure, backlog, queue, budget, or state risk.
- Competitor, baseline, outside-option, or reference-policy interaction.

If total score improves but decomposition worsens, mark as `VERIFY` rather than promote.

## Candidate Types

Classify every candidate as one of:

- `mechanism`: changes the policy logic.
- `parameter mutation`: same policy, different constants.
- `estimator`: changes hidden-state or regime inference.
- `risk control`: reduces tail loss or constraint failure.
- `participation control`: changes when or how much to act.
- `ablation`: removes one mechanism to test whether it matters.
- `robustness probe`: tests generalization across regimes.
- `constraint recovery`: fixes runtime, gas, storage, memory, or invalid-action risk.
- `variance call`: same artifact rerun, no code change.

## General Strategy Families

These are abstract mechanism families, not domain-specific strategies:

1. Static baseline.
   - Fixed action rule.
   - Useful as a control and fallback.
2. Regime estimator.
   - Infer hidden environment parameters from observations.
   - Examples: volatility, demand, jumpiness, congestion, toxicity, competitor strength, load, or scarcity.
3. Adaptive margin or safety buffer.
   - Widen or narrow the policy's safety margin based on inferred risk.
   - Generalizes across spreads, fees, quotes, risk thresholds, and scheduling slack.
4. Flow or event classifier.
   - Separate benign/opportunistic events from informed/adversarial events.
   - Adapt differently after each class.
5. Inventory, exposure, or budget controller.
   - Manage accumulated state: inventory, cash, backlog, queue position, reserves, risk, compute budget, or memory.
6. Participation controller.
   - Decide when to engage, how aggressively, and when to abstain.
   - Optimize volume or opportunity capture versus adverse selection and cost.
7. Competitor or outside-option tracker.
   - Adapt to static or dynamic competitors, alternative routes, queues, normalizers, fallback services, or reference policies.
8. Hysteresis, decay, or cooldown.
   - Avoid overreacting to noise.
   - Use bounded memory, decays, cooldowns, and state smoothing.
9. Tail-risk guard.
   - Sacrifice small mean score when necessary to avoid catastrophic paths or invalid actions.
10. Hybrid controller.
   - Combine estimator, margin, participation, and exposure control only after each part has isolated evidence.

## Parameter Search

Use generated candidates when many constants exist.

Recommended loop:

1. Start with a small hand-written mechanism.
2. Expose parameters in a compact config.
3. Run random or Latin-hypercube search for broad discovery.
4. Use coordinate descent or local search around winners.
5. Run ablations to verify which parameters and mechanisms actually matter.
6. Validate on disjoint scenarios.
7. Promote only if the win survives noise and regime splits.

Do not keep adding constants without ablation evidence.

## Overfit Rules

Reject or verify carefully when:

- Improvement appears only on one seed set.
- Mean improves but worst-decile score collapses.
- Leaderboard improves once but local matched validation does not.
- Candidate depends on quirks not stated in the contract.
- Policy becomes too complex to explain or ablate.
- Parameter sweep finds a sharp spike rather than a broad plateau.
- Win disappears under renamed, reordered, or independent scenarios.

## Handoff

Record:

- Best artifact.
- Parent artifact.
- Scenario sets used.
- Mean, SEM, `p05`, and `p95`.
- Per-regime table.
- Decomposition table.
- Open hypotheses.
- Closed branches.
- Parameters searched.
- Next cheapest falsifiable probe.
