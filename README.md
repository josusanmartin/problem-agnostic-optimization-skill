# Problem-Agnostic Optimization Skill

Codex skill for evidence-driven optimization across measured programs, CPU/GPU kernels, stochastic policy challenges, production latency/throughput targets, and leaderboard submissions.

The skill works best when the task starts with a clear `/goal`. Optimization is a long-running search problem; the agent needs an explicit objective, context, constraints, and stopping rule before it starts changing code.

## Use It With `/goal`

For any substantial optimization run, start with `/goal`.

Minimal form:

```text
/goal
Objective:
Authoritative metric:
Baseline:
Editable files:
Immutable files:
Budget / stopping rule:
Validation:
```

Use the extended form when the run is noisy, remote, budget-limited, hardware-specific, or stochastic:

```text
/goal
Objective:
Context:
Target mode:
Authoritative metric:
Current baseline:
Editable files:
Immutable files:
Budget:
Validation:
Stopping rule:
Notes:
```

Use concrete values. Avoid prompts like "make this faster" or "optimize this." The core loop is:

```text
contract -> baseline -> bottleneck model -> candidate -> validate/measure -> decide -> iterate or escape
```

Only the authoritative metric promotes; profiles, counters, local benchmarks, and static models explain.

### Field Guide

- `Objective`: the measurable target. Example: "get p95 under 1 ms", "reach first place", "beat public best by 1%", or "maximize validation score under 1000 simulations".
- `Context`: the repo, problem, benchmark, hardware, service, leaderboard, or paper/reference that defines the task.
- `Target mode`: `production`, `clean leaderboard`, or another explicitly stated mode. Clean leaderboard still forbids exploit-like shortcuts.
- `Authoritative metric`: the command, submit path, dashboard, leaderboard, p95, score, or public evaluator that decides promotion.
- `Baseline` / `Current baseline`: current best artifact, score, command, commit, submission ID, or "unknown, reproduce first".
- `Editable files`: what Codex may change.
- `Immutable files`: reference implementations, graders, harnesses, datasets, scoring code, and anything else that must not be changed.
- `Budget` / `Budget / stopping rule`: submissions, GPU minutes, wall time, simulation count, API spend, max candidates, or target exit condition.
- `Validation`: correctness checks, seed protocol, shape sweep, test command, profiler/counter expectations, or production guardrails.
- `Stopping rule`: target reached, budget exhausted, blocker, plateau audit, or handoff after N candidates.
- `Notes`: known failed attempts, public clues, constraints, tolerances, hidden-test risk, and anything that would make an optimization invalid.

## Operating Model

The skill keeps four artifacts current:

1. `Contract`: what counts as correct, what metric promotes, what files are editable, and what system, shape, seed, or scorer is authoritative.
2. `Best`: the current best artifact, score, command, result ID, and promotion rationale.
3. `Bottleneck model`: the current explanation of the gap, including resource floors, profile confidence, tails, case splits, and statistical uncertainty.
4. `Candidate ledger`: one hypothesis, one diff, expected signal, result, decision, and learning.

Candidate decisions are `PROMOTE`, `KEEP VARIANT`, `REJECT`, `BUG`, or `BLOCKED`. After repeated same-family ties or regressions, the skill should stop tuning and change representation, primitive, route, or specialization level.

## Prompt Templates

### Leaderboard Or Challenge

```text
/goal
Objective: Reach first place or beat the current public best on <leaderboard/problem>.
Context: <link>, repo path <path>, current candidate <file>.
Target mode: clean leaderboard.
Authoritative metric: public submit result from <command/service>; local runs are screening only.
Current baseline: <score/time/submission>, or reproduce first if unknown.
Editable files: <candidate files only>.
Immutable files: problem statement, checker, benchmark, reference, scoring code.
Budget: <N submissions or time limit>.
Validation: run correctness first when available; compare per-shape/per-case results; record variance.
Stopping rule: stop when first place is verified, budget is exhausted, or plateau audit says change hill.
Notes: no exploits, no wrong-answer speed, no harness edits.
```

### Production Optimization

```text
/goal
Objective: Reduce <p95/latency/cost/memory> from <baseline> to <target>.
Context: service/module <path>, workload <description>, production constraints <links>.
Target mode: production.
Authoritative metric: <benchmark/dashboard/load test command>.
Current baseline: <number, commit, command>.
Editable files: <implementation/config files>.
Immutable files: public API, correctness tests, datasets, benchmark contract.
Budget: <wall time, candidate count, risk window>.
Validation: tests, load test, profiling artifacts, p95/p99, error rate, rollback safety.
Stopping rule: target reached with stable validation, or handoff with bottleneck map.
Notes: maintainability and correctness beat benchmark-only tricks.
```

### Stochastic Policy Or Simulator

```text
/goal
Objective: Improve expected score from <baseline> to <target> under hidden/randomized scenarios.
Context: simulator/challenge <link or path>, submitted policy <file>.
Target mode: clean leaderboard or production.
Authoritative metric: <server score/public submit/official evaluation>.
Current baseline: mean <x>, SEM <y>, seed set <name>.
Editable files: policy/controller/config files.
Immutable files: simulator, scorer, seed generator, reference policies, submission protocol.
Budget: <simulations, submissions, wall time>.
Validation: smoke/train/validation/holdout/adversarial scenario sets; report mean, SEM, p05/p95, invalid rate, win rate vs parent.
Stopping rule: public score improves, holdout rejects candidate, budget exhausted, or overfit audit triggers.
Notes: compare parent and candidate on matched scenarios when possible.
```

## Install

Clone the repository and copy the skill directory into your Codex skills folder:

```bash
git clone https://github.com/josusanmartin/problem-agnostic-optimization-skill.git
mkdir -p "$HOME/.codex/skills"
cp -R problem-agnostic-optimization-skill/skills/problem-agnostic-optimization "$HOME/.codex/skills/"
```

The installed layout should be:

```text
$HOME/.codex/skills/problem-agnostic-optimization/
  SKILL.md
  agents/
    openai.yaml
  references/
    cpu-architecture.md
    evidence-loop.md
    gpu-architecture.md
    harness.md
    problem-families.md
    resource-models.md
    stochastic-policy-search.md
    templates.md
```

## Validate

From the repository root:

```bash
./scripts/validate.sh
```

If Codex's `skill-creator` validator is installed locally, the script uses it. It also checks the skill files for non-ASCII characters.

## Repository Layout

```text
skills/problem-agnostic-optimization/   # Codex skill payload
scripts/validate.sh                     # local validation helper
README.md                               # repo documentation
LICENSE                                 # MIT license
```

## Acknowledgements

This skill is original work, but it incorporates general operating ideas inspired by:

- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills): simplicity-first edits, surgical changes, explicit assumptions, and goal-driven execution.
- [karpathy/autoresearch](https://github.com/karpathy/autoresearch): autonomous fixed-budget experiment loops, keep/discard discipline, compact result tracking, and evidence-managed search.

This project is not affiliated with either repository and does not copy their code.
