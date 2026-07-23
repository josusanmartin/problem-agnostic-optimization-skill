# Stochastic Policy Search

Use this reference when a policy, controller, agent, scheduler, or other stateful action function is scored over stochastic, hidden, or adversarial scenarios.

## Establish Only The Decision Contract

Retain only facts that can change a candidate:

- Observable/action APIs, persistent state, reset behavior, and final-state semantics.
- Randomness controls, hidden regimes, public/private differences, and reproducibility.
- Objective, relevant tail or safety guardrails, invalid-action behavior, resource limits, and submission budget.
- Protected baseline artifact and score distribution.

Do not rebuild a supplied contract or create a table merely to restate it.

## Use A Layered Gate

Use the cheapest applicable levels; skip redundant ones:

1. `smoke`: compile/import, legal actions, and obvious edge cases.
2. `matched`: candidate versus parent on common seeds or scenarios.
3. `validation`: disjoint scenarios not used to choose the candidate.
4. `authority`: the official platform score.

Do not promote from one stochastic result unless its margin clearly dominates measured noise. Near ties favor the simpler, safer policy.

Track only decision-relevant statistics: objective estimate and uncertainty, paired delta or win rate when matched, the contractual tail/guardrail, invalid rate, and constraint margin. Add regime decomposition only when it changes the next experiment; do not compute a dashboard of unused metrics.

## Choose Search Scale

When logic is editable, high-value mechanism families include:

- Regime or hidden-state estimation.
- Adaptive margin, participation, exposure, inventory, queue, or budget control.
- Event or adversary classification.
- Competitor/outside-option tracking.
- Hysteresis, cooldown, decay, or tail-risk guards.

Test one mechanism before combining it. A hybrid earns budget only after its parts show isolated signal.

When numeric parameters are the only editable artifact, begin bounded broad discovery immediately. Use random or Latin-hypercube search, then local search around broad winners. Keep parameters in a compact configuration and ablate added constants.

For noisy or best-of-N sweeps, load the `variance` add-on through the router. Use matched training scenarios for screening, disjoint validation for promotion, and a holdout only when overfit risk justifies preserving one.

## Reject Overfit

Reject or verify when:

- A win appears on one seed set but not matched or disjoint scenarios.
- Mean improves while a contractual tail, safety guardrail, or invalid rate collapses.
- The winner is a sharp isolated parameter spike rather than a stable neighborhood.
- The policy depends on a visible-test quirk outside the declared contract.
- Added state or complexity cannot be explained or ablated.

The authority promotes; local distributions decide which candidates deserve that cost.
