# Problem-Agnostic Optimization Skill

A lean Codex skill for improving measured artifacts under a correctness or scoring contract: programs, CPU/GPU kernels, stochastic policies, production latency or throughput, and leaderboard submissions.

The skill owns optimization strategy. Logging, token accounting, dashboards, submission transport, and run reporting are optional integrations.

## Responsibilities

| Mode | Optimization | Logging and reporting |
|---|---|---|
| Plain `problem-agnostic-optimization` | PAO runs the evidence loop and search-health policy | None by default |
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

## Route First

The first skill action is routing, before candidate planning or reference loading. PAO chooses by scored-artifact semantics, not venue branding or implementation substrate. The first matching primary route wins: stochastic policy, live request service, fixed-resource schedule, GPU artifact, CPU/offline artifact, then the core-only fallback.

PAO selects exactly one primary module, initially at most one GPU-only kernel-shape module, and only evidence-triggered add-ons. A second shape module is allowed only when the scored GPU artifact genuinely spans both shapes. It never treats the references directory as a reading list.

Examples:

- A CUDA convolution loads `gpu-architecture.md` plus `kernel-stencils-convolution.md`. It does not load CPU, service, stochastic-policy, or VLIW guidance.
- A live request server loads `service-throughput.md`, whether or not a venue calls itself HighLoad. If one CPU/GPU stage needs isolated work, PAO creates a child scope and routes that scope separately.
- A simulator-scored controller loads `stochastic-policy-search.md` even when implemented with CPU or GPU code, because policy quality is the scored artifact.
- A VLIW cycle search loads `fixed-resource-scheduling.md`, which includes a rough per-engine floor. It adds `resource-models.md` only when deeper floor, tail, transfer, or co-binder analysis drives the next candidate.

The active context records one compact selection such as:

```text
Route: gpu; shape: kernel-stencils-convolution; add-ons: none
```

When evidence changes the bottleneck, PAO returns to the router, replaces obsolete primary/shape modules, and removes add-ons whose triggers no longer apply. It does not accumulate routes, and references do not recursively load other references.

Cross-cutting guidance is split by trigger: measurement/profiling, variance and bounded sweeps, public-technique intake, resource models, plateau escape, frontier introspection, and runtime overhead. A common profiling question no longer loads sweep, breakthrough-mining, and plateau machinery together.

### Draft A Goal Without Starting

```text
Use problem-agnostic-optimization.

Draft a /goal block for later. Do not start or activate the goal.
The task is <task>. The authoritative metric is <metric>.
Check the current repo for the baseline and remaining contract details.
```

The result should be a copy-paste prompt, not an activated goal.

## With Scorebench

Use both skills when the user invokes Scorebench, supplies a scoped Scorebench run, or the task is assigned through Scorebench:

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

The `scorebench` skill controls context, run lifecycle, pings, submissions, refresh, token accounting, and reports. PAO controls the bottleneck model, hypotheses, candidate edits, correctness gates, search-health decisions, and promotion decisions. PAO must not create `work/optimization_harness/` or parallel local progress files during a Scorebench run.

## Default Behavior

The skill keeps only enough active state to choose the next experiment:

- Contract and authoritative metric.
- Protected best artifact and result.
- Current bottleneck model.
- Current mechanism family, hypothesis, and kill criterion.
- Actual measured attempts and budget consumed in the current search epoch.
- Validation, measurement, and decision.
- Whether the next candidate must be off-hill.

It does not require a file-based ledger, progress chart, dashboard, audit session, token snapshots, or a formal handoff. Those are separate capabilities and should be enabled only when requested.

At completion, the default report is short: best artifact, authoritative result, validation status, and next blocker or direction.

## Search Health

PAO counts actual search work rather than candidate labels. A scheduler sweep containing 5,000 measured configurations consumes 5,000 attempts even if it produces one candidate artifact. Its bounded outcome is one candidate-family decision, so individual draws do not become thousands of same-family misses. Checkpoints, verifier reruns, pings, token snapshots, and report refreshes are operational work rather than candidates or promotions.

The search epoch opens only after an authoritative baseline and the first valid comparable candidate or planned sweep draw on a hill. Unless the user sets different thresholds, PAO reassesses after three comparable same-family misses, 10% of the contract budget consumed in the open epoch without meaningful authoritative promotion, or exhaustion of a written sweep/family budget. Bugs, blockers, invalid measurements, and unresolved noise consume budget but are not misses.

At the trigger, PAO stops and loads only the plateau-escape add-on. It may continue a narrowed hill when an explained implementation bug leaves a faithful test untried or a predeclared bracket remains plausibly valuable. Otherwise it closes or narrows the hill and spends the next measured candidate off-hill by default. A meaningful authoritative promotion or a genuine hill change resets the epoch; equivalent seeds, batches, or renamed families do not.

A plateau is not a resource floor. Reserve `proven lower bound` for models whose required-work counts, throughput assumptions, dependencies, and unavoidable costs establish the bound. Otherwise use `model floor` or `observed plateau` and keep structural alternatives open.

Search-health accounting is decision state, not a local logging requirement. During Scorebench runs, derive it from Scorebench history and do not mirror it into PAO files.

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

The entrypoint is intentionally small, and the reference payload is split into narrow modules that load only when routed:

```text
problem-agnostic-optimization/
  SKILL.md
  agents/openai.yaml
  references/
    cpu-architecture.md
    evidence-loop.md
    fixed-resource-scheduling.md
    frontier-introspection.md
    gpu-architecture.md
    kernel-attention-moe.md
    kernel-elementwise.md
    kernel-histogram.md
    kernel-matrix.md
    kernel-quantized.md
    kernel-reductions-scans.md
    kernel-stencils-convolution.md
    plateau-escape.md
    resource-models.md
    runtime-overhead.md
    service-throughput.md
    stochastic-policy-search.md
    technique-intake.md
    variance-and-sweeps.md
```

## Validate

```bash
python3 -m pip install -r requirements-dev.txt
./scripts/validate.sh
python3 -m pytest -q
```

The validator parses exact router headings and tables, requires every semantic route id, resolves every module path, rejects orphaned or recursive modules, enforces word budgets, checks skill metadata, and rejects non-ASCII content. The tests mutate every current route/module pair and cover malformed paths, anchors, demoted headings, and false-positive `.md` prose.

## Acknowledgements

This skill incorporates general operating ideas inspired by:

- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills): simplicity-first edits, surgical changes, explicit assumptions, and goal-driven execution.
- [karpathy/autoresearch](https://github.com/karpathy/autoresearch): autonomous fixed-budget experiment loops, keep/discard discipline, and evidence-managed search.

This project is not affiliated with either repository and does not copy their code.
