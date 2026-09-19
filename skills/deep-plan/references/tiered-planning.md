# Reference: Tiered Planning (Phase 3)

Build a linked three-tier plan after the intent, grounding, and risk artifacts are complete.

## Directory Structure

```text
.deep-plan/<epic-slug>/
├── 00-intent.md
├── 01-grounding.md
├── 02-risk-register.md
├── 03-tier1-epic.md
├── modules/
│   ├── M01-[name].md
│   └── M02-[name].md
├── tasks/
│   ├── T01-[name].md
│   └── T02-[name].md
├── dependency-dag.json
└── progress-ledger.md
```

## Tier 1: Scope and Invariants

Use `templates/tier1-epic-template.md`. Record the problem, objective, use cases, in-scope and out-of-scope boundaries, numbered invariants, NFRs, risk references, and module map. Derive candidate invariants from the request, existing behavior, and repository conventions; label inferred assumptions.

## Tier 2: Architecture Contracts

Use `templates/tier2-module-template.md`. Dispatch the System Architect for each module. Define ownership boundaries, interface contracts, schemas, sequence flows, error contracts, risk mitigations, and the contract that downstream tasks may rely on.

If a Security Architect or another specialist is activated, require the specialist output to link back to the same Tier 1 invariants and risk register. Do not silently replace the general architecture contract without recording the reason.

## Tier 3: Atomic Execution Tasks

Use `templates/tier3-task-template.md`. Define one independently verifiable behavioral or contract change per task. Permit the task to span implementation, tests, migrations, generated artifacts, or cross-package contracts when they jointly realize one completion criterion.

Require every task to specify:

1. Exact target paths and symbols where applicable.
2. Ordered implementation steps.
3. Parent module and invariant traceability.
4. Artifact and contract dependencies.
5. Concrete failure defenses.
6. Verification mode and exact commands.
7. Expected outputs and completion evidence.

Treat file and function count as a decomposition heuristic, not a hard limit.

## Dependency DAG

Use stable task IDs and validate that every dependency refers to an existing task, no task depends on itself, and the graph is acyclic. A dependency means that the task needs another task's code, schema, generated artifact, interface contract, decision, or verified behavior. Unlock a task only after every dependency is completed and integrated.

Represent research spikes as normal DAG tasks with a stable `research_id` field or an equivalent explicit link. Do not use an undocumented special task number.

Example:

```json
{
  "epic": "epic-slug",
  "tasks": [
    { "id": "T01", "module": "M01", "kind": "research", "research_id": "R01", "dependencies": [] },
    { "id": "T02", "module": "M01", "kind": "implementation", "dependencies": ["T01"] }
  ]
}
```

## Planning Gate

Before execution, validate all artifact links, task IDs, dependency references, DAG acyclicity, and ledger initialization. In Collaborative Mode, require explicit user approval after the complete plan. In Autonomous Mode, proceed after validation unless a boundary-changing architecture fork requires user synchronization.
