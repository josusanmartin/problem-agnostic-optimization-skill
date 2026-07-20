# Problem-Agnostic Optimization Skill

A lean Codex skill for improving measured artifacts under a correctness or scoring contract: programs, CPU/GPU kernels, stochastic policies, production latency or throughput, and leaderboard submissions.

The skill owns optimization strategy. Logging, token accounting, dashboards, submission transport, and run reporting are optional integrations.

## Responsibilities

| Mode | Optimization | Logging and reporting |
|---|---|---|
| Plain `problem-agnostic-optimization` | PAO runs the evidence loop | None by default |
| PAO with [Scorebench](https://github.com/josusanmartin/scorebench-skill) | PAO chooses and evaluates candidates | Scorebench exclusively owns runs, submissions, tokens, history, best state, dashboards, and reports |
| Explicit local persistence | PAO runs the evidence loop | A separate user-selected logging module runs as an optional sidecar |

PAO does not bundle a local logging harness. It does not create progress ledgers, token logs, charts, dashboards, audits, or candidate dossiers unless the user explicitly selects a separate local logging module. When Scorebench is active, do not duplicate any of its records locally.

## Quick Start

Use a concrete `/goal` for a substantial run:

```text
Use problem-agnostic-optimization.

/goal
Objective:
Authoritative metric:
Current baseline: unknown, reproduce first
Editable files:
Immutable files:
Budget / stopping rule:
Validation:
Multi-agent mode: off
```

The core loop is:

```text
contract -> baseline -> bottleneck model -> candidate -> validate/measure -> decide -> iterate or escape
```

Only the authoritative metric promotes. Profiles, counters, local benchmarks, and static models explain.

For a tiny one-shot task, a `/goal` is optional. State the metric and constraints directly and let the skill run the same loop without creating process artifacts.

### Draft A Goal Without Starting

```text
Use problem-agnostic-optimization.

Draft a /goal block for later. Do not start or activate the goal.
The task is <task>. The authoritative metric is <metric>.
Check the current repo for the baseline and remaining contract details.
```

The result should be a copy-paste prompt, not an activated goal.

## With Scorebench

Use both skills when Scorebench provides the exercise or submission path:

```text
Use scorebench.
Use problem-agnostic-optimization.

/goal
Objective: <measurable target>
Authoritative metric: Scorebench result for the assigned exercise
Current baseline: reproduce through Scorebench
Editable files: <candidate files>
Immutable files: problem statement, checker, scorer, and submission protocol
Budget / stopping rule: <budget>
Validation: <local correctness checks plus Scorebench acceptance>
Multi-agent mode: off
Notes: no exploits; Scorebench exclusively owns submissions, token accounting, history, logging, and reporting.
```

The `scorebench` skill controls context, run lifecycle, pings, submissions, refresh, token accounting, and reports. PAO controls the bottleneck model, hypotheses, candidate edits, correctness gates, and promotion decisions. PAO must not create `work/optimization_harness/` or parallel local progress files during a Scorebench run.

## Default Behavior

The skill keeps only enough active state to choose the next experiment:

- Contract and authoritative metric.
- Protected best artifact and result.
- Current bottleneck model.
- Current candidate hypothesis and kill criterion.
- Validation, measurement, and decision.
- Next direction or stopping reason.

It does not require a file-based ledger, progress chart, dashboard, audit session, token snapshots, or a formal handoff. Those are separate capabilities and should be enabled only when requested.

At completion, the default report is short: best artifact, authoritative result, validation status, and next blocker or direction.

## Prompt Templates

### Leaderboard Or Challenge

```text
/goal
Objective: Reach first place or beat the current public best on <problem>.
Authoritative metric: accepted public submission result; local runs are screening only.
Current baseline: <result>, or unknown, reproduce first.
Editable files: <candidate files only>.
Immutable files: problem statement, checker, benchmark, reference, scoring code.
Budget / stopping rule: <submissions, time, or target>.
Validation: correctness first; compare relevant shapes or cases; account for variance.
Multi-agent mode: off.
Notes: no exploits, wrong-answer speedups, grader edits, or hidden-test tricks.
```

### Production Optimization

```text
/goal
Objective: Reduce <p95/latency/cost/memory> from <baseline> to <target>.
Authoritative metric: <benchmark, dashboard, or load test>.
Current baseline: <number, commit, command>.
Editable files: <implementation or configuration files>.
Immutable files: public API, correctness tests, datasets, benchmark contract.
Budget / stopping rule: <risk window, time, or target>.
Validation: tests, load test, p95/p99, error rate, and rollback safety.
Multi-agent mode: off.
```

### Stochastic Policy Or Simulator

```text
/goal
Objective: Improve expected score from <baseline> to <target>.
Authoritative metric: <official evaluation or server score>.
Current baseline: mean <x>, SEM <y>, seed set <name>.
Editable files: <policy or controller files>.
Immutable files: simulator, scorer, seed generator, submission protocol.
Budget / stopping rule: <simulations, submissions, time, or target>.
Validation: matched train, validation, holdout, and adversarial scenarios.
Multi-agent mode: off.
```

## Install

```bash
git clone https://github.com/josusanmartin/problem-agnostic-optimization-skill.git
cd problem-agnostic-optimization-skill

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
rm -rf "$CODEX_HOME/skills/problem-agnostic-optimization"
cp -R skills/problem-agnostic-optimization "$CODEX_HOME/skills/"
```

Restart Codex or start a new session after installing or updating the skill.

The installed payload is intentionally small:

```text
problem-agnostic-optimization/
  SKILL.md
  agents/openai.yaml
  references/
    cpu-architecture.md
    evidence-loop.md
    frontier-introspection.md
    gpu-architecture.md
    problem-families.md
    resource-models.md
    stochastic-policy-search.md
```

## Validate

```bash
python3 -m pip install -r requirements-dev.txt
./scripts/validate.sh
python3 -m pytest -q
```

The validator parses skill metadata, checks the lean required payload, and rejects non-ASCII skill content.

## Acknowledgements

This skill incorporates general operating ideas inspired by:

- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills): simplicity-first edits, surgical changes, explicit assumptions, and goal-driven execution.
- [karpathy/autoresearch](https://github.com/karpathy/autoresearch): autonomous fixed-budget experiment loops, keep/discard discipline, and evidence-managed search.

This project is not affiliated with either repository and does not copy their code.
