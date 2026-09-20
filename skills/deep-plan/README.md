# Deep Plan: Evidence-Driven Planning and Swarm Execution

Structured planning and gated multi-agent execution for complex features, migrations, refactors, and architectural changes.

Deep Plan keeps the same planning rigor for every user while adapting visible detail and terminology to the inferred audience. Detailed evidence remains available in the planning artifacts.

## What It Does

1. **Intent and entry preflight** — Extracts goals, behaviors, invariants, outputs, constraints, assumptions, autonomy mode, and unresolved decisions.
2. **Grounding, gaps, and risks** — Maps repository architecture and dependencies, records file-and-line evidence, and creates a risk register.
3. **Three-tier planning** — Produces Tier 1 scope and invariants, Tier 2 architecture contracts, Tier 3 atomic tasks, and a dependency DAG.
4. **Adversarial plan review** — Challenges assumptions, risks, architecture, dependencies, acceptance criteria, and verification before implementation.
5. **Gated execution** — Uses isolated worktrees, dependency readiness, declared verification modes, Code Auditor review, adversarial review, explicit integration, and integrated-tree verification.

## Roles

| Role | Responsibility | Reference |
| :--- | :--- | :--- |
| **PM / Orchestrator** | Owns planning artifacts, DAG, ledger, integration, and user interaction | `SKILL.md` |
| **Codebase Explorer** | Maps architecture, dependencies, conventions, and blast radius | [codebase-explorer.md](references/subagents/codebase-explorer.md) |
| **System Architect** | Defines Tier 2 boundaries, contracts, data flow, and schemas | [system-architect.md](references/subagents/system-architect.md) |
| **Task Decomposer** | Creates Tier 3 tasks and the dependency DAG | [task-decomposer.md](references/subagents/task-decomposer.md) |
| **Plan Challenger** | Challenges the plan before execution | [plan-challenger.md](references/subagents/plan-challenger.md) |
| **Worker Implementer** | Executes one ready task in an isolated worktree | [worker-implementer.md](references/subagents/worker-implementer.md) |
| **Code Auditor** | Runs Standards and Spec review axes for code changes | [spec-reviewer.md](references/subagents/spec-reviewer.md) |
| **Adversarial Challenger** | Stress-tests implementation invariants and sad paths | [adversarial-challenger.md](references/subagents/adversarial-challenger.md) |

Security, performance, research, and documentation roles activate from the risk-and-task routing matrix.

## Artifact Layout

```text
.deep-plan/<epic-slug>/
├── 00-intent.md
├── 01-grounding.md
├── 02-risk-register.md
├── 03-tier1-epic.md
├── modules/
├── tasks/
├── dependency-dag.json
├── execution-state.json
└── progress-ledger.md              # Generated projection of execution-state.json
```

`execution-state.json` is the PM-owned canonical execution state. Workers and reviewers return evidence; they do not edit it directly.

See [the Codex multi-agent reference](references/codex-multi-agent.md) for runtime capability checks.

## Triggers

- "plan this feature"
- "deep plan"
- "design an epic"
- complex multi-file refactor, migration, security, or performance work
