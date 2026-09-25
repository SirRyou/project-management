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

Use `templates/tier2-module-template.md`. The PM must give the System Architect the epic slug and exact paths to `00-intent.md`, `01-grounding.md`, `02-risk-register.md`, `03-tier1-epic.md`, the `modules/` output directory, and the template. Do not instruct a fresh subagent only to read a named tier or dossier. Dispatch the System Architect for each module — one agent per module, and **only after the §6 contract registry is frozen**. Parallel fan-out is permitted at that point; before it, each architect would freeze a different snapshot of a moving contract. Define ownership boundaries, interface contracts, schemas, sequence flows, error contracts, risk mitigations, and the contract that downstream tasks may rely on.

If a Security Architect or another specialist is activated, require the specialist output to link back to the same Tier 1 invariants and risk register. Do not silently replace the general architecture contract without recording the reason.

## Tier 3: Atomic Execution Tasks

Use `templates/tier3-task-template.md`. The PM must give the Task Decomposer the epic slug and exact paths to `00-intent.md`, `01-grounding.md`, `02-risk-register.md`, `03-tier1-epic.md`, every `modules/M*-*.md` input, the `tasks/` output directory, `dependency-dag.json`, and the template. Do not instruct a fresh subagent only to read a named tier or module. A single decomposer covering every module is the default; when the epic is large enough to justify parallel decomposition, follow **Fanning Out Multiple Decomposers** below first. Define one independently verifiable behavioral or contract change per task. Permit the task to span implementation, tests, migrations, generated artifacts, or cross-package contracts when they jointly realize one completion criterion.

### Fanning Out Multiple Decomposers

A single decomposer over a large module set is a long serial pass. When the epic is large enough to justify parallel decomposition, the PM must first:

1. **Partition the ID space.** Assign each decomposer a **disjoint task-ID range** plus, if needed, a separate overflow range. Publish the assignment before any decomposer starts writing. Two agents writing into the same `tasks/` directory will collide — cards have been deleted mid-edit and duplicated by concurrent writers.
2. **Freeze the ID ledger.** Author `tasks/ID-LEDGER.md` mapping `T-id → slug → module → assigned range`, and freeze it. It is PM-owned. Name it `ID-LEDGER.md`; do **not** name it `T00-*.md`, because the task-card glob would pick it up as a task and fail validation.
3. **Freeze the contract registry** (§6 of `03-tier1-epic.md`) before any decomposer reads a module specification.
4. **Forbid renumbering** within a range another agent may have referenced, and forbid globbing `tasks/T*.md` — each decomposer reads only its own range and the module specifications it was assigned.

If a renumber is genuinely unavoidable, the renumbering agent must emit an explicit old→new mapping for the PM to apply to **every other fragment**. Renumbering preserves referential integrity while destroying meaning: the DAG stays acyclic, resolvable, and wrong. `validate` cannot detect it.

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

**Cross-module citations carry the target's slug as well as its ID.** In a task card, write `T11-localvadport`, not `T11`; in the DAG, `dependencies` stays ID-only by schema. The slug is a semantic handle: it makes a renumber self-evidently wrong at the citation site (`T11` resolving to a card named `capabilities-card`) instead of silently plausible, and it turns detection into a string comparison rather than a prose re-read of every card. The validator's dependency extraction matches `T[0-9]{2,}` anywhere in the field, so the slugged form parses identically — no CLI change is needed.

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

Before execution, validate all artifact links, task IDs, dependency references, DAG acyclicity, and ledger initialization. `validate` is a shape check: run `deep_plan.py edges <epic-slug>` and read the edge list before Phase 4, because a renumbered ID leaves a DAG that is acyclic, resolvable, and wrong. In Collaborative Mode, require explicit user approval after the complete plan. In Autonomous Mode, proceed after validation unless a boundary-changing architecture fork requires user synchronization.
