# Problem-Agnostic Optimization Skill

Codex skill for evidence-driven optimization across measured programs, CPU/GPU kernels, stochastic policy challenges, production latency/throughput targets, and leaderboard submissions.

The skill is designed to make optimization runs behave like controlled experiments:

- Set an ambitious objective before optimizing.
- Preserve the current best artifact.
- Use the authoritative measurement as the promotion gate.
- Run the code before making performance claims.
- Keep candidate changes narrow and attributable.
- Escape local optima with explicit off-hill probes.
- Handle noisy, stochastic, and hidden-seed evaluations with scenario sets and statistical gates.

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
