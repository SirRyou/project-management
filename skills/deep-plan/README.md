# Deep Plan: Swarm Orchestration & 3-Tier Planning

Structured pre-code planning and multi-agent swarm orchestration for complex features, migrations, and architectural refactoring.

## What It Does

Deep Plan orchestrates an engineering swarm (PM, System Architect, Task Decomposer, Worker Implementers, and Reviewers) to break down complex epics and execute them reliably:

1. **Intake & Grounding** — Captures user intent and autonomy preferences in a single upfront interaction; maps repository context and invariants using an isolated Codebase Explorer subagent.
2. **3-Tier Hierarchical Planning** — Eliminates ambiguous task decomposition by generating a clear hierarchy:
   - **Tier 1 (High-Level):** Scope, Business Objectives, System Invariants, NFRs.
   - **Tier 2 (Mid-Level):** Architecture Contracts, Component Boundaries, Sequence Diagrams, Schemas.
   - **Tier 3 (Low-Level):** Atomic Worker Cards with exact target files/lines, sad paths, and test commands.
3. **Swarm Execution & Dual-Review** — Executes against a dependency DAG. Upon task completion by a Worker Implementer, the PM fans out **two parallel reviewer subagents** (Spec Compliance & Adversarial Challenger) to verify correctness and protect invariants before unlocking dependent tasks.

---

## The Swarm Roles

| Role | Lifecycle | Responsibility | Reference |
| :--- | :--- | :--- | :--- |
| **PM / Orchestrator** | Persistent (Main Thread) | Manages DAG state, progress ledger, task dispatch, and user interaction. | `SKILL.md` |
| **Codebase Explorer** | Ephemeral (Phase 2) | Maps AST, schemas, dependencies, conventions, and blast radius. | [codebase-explorer.md](references/subagents/codebase-explorer.md) |
| **System Architect** | Ephemeral (Phase 3) | Slices Tier 1 scope into modular Tier 2 specifications and interface contracts. | [system-architect.md](references/subagents/system-architect.md) |
| **Task Decomposer** | Ephemeral (Phase 3) | Decomposes Tier 2 modules into atomic Tier 3 tasks and `dependency-dag.json`. | [task-decomposer.md](references/subagents/task-decomposer.md) |
| **Worker Implementer** | Ephemeral (Phase 4) | Implements one Tier 3 task following strict TDD (Red $\rightarrow$ Green $\rightarrow$ Refactor). | [worker-implementer.md](references/subagents/worker-implementer.md) |
| **Spec Reviewer** | Ephemeral (Phase 4) | Checks diff against Tier 3 acceptance criteria and verifies zero scope creep. | [spec-reviewer.md](references/subagents/spec-reviewer.md) |
| **Adversarial Challenger** | Ephemeral (Phase 4) | Stress-tests code for invariant breaks, silent failures, race conditions, and edge cases. | [adversarial-challenger.md](references/subagents/adversarial-challenger.md) |

---

## Artifact Layout

Planning produces a structured directory under `.deep-plan/<epic-slug>/`:

```text
.deep-plan/<epic-slug>/
├── 00-tier1-epic.md              # Tier 1: Scope, Invariants, NFRs
├── 01-architecture-overview.md   # Tier 2: System Topology & Cross-Cutting Architecture
├── modules/                      # Tier 2: Module/Component Specifications
│   ├── M01-[name].md
│   └── M02-[name].md
├── tasks/                        # Tier 3: Atomic Worker Execution Cards
│   ├── T01-[name].md
│   ├── T02-[name].md
│   └── T03-[name].md
├── dependency-dag.json           # Machine-readable task execution graph
└── progress-ledger.md            # Swarm execution status, commits, and review verdicts
```

---

## The 4 Phases

1. **Phase 1: User Intake** — Runs single `ask_question` call to establish Autonomy Mode (`Autonomous` vs `Collaborative`) and Epic nature.
2. **Phase 2: Codebase Grounding** — Dispatches Codebase Explorer to compile the Grounding Dossier and resolve unknowns.
3. **Phase 3: Tiered Planning** — Generates Tier 1, dispatches System Architect for Tier 2 modules, and dispatches Task Decomposer for Tier 3 atomic tasks and `dependency-dag.json`.
4. **Phase 4: Swarm Execution** — Iterates over the DAG:
   - Dispatches Worker Implementers for ready tasks.
   - Fans out dual reviews in parallel (**Spec Compliance** + **Adversarial Challenger**).
   - Updates `progress-ledger.md` and unlocks dependent tasks.
   - Runs global test suite upon completion.

---

## Triggers

- "plan this feature"
- "deep plan"
- "design an epic"
- "architectural planning"
- "break down this work"

## License

MIT
