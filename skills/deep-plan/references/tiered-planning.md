# Reference: Tiered Planning (Phase 3)

## Overview
Planning decomposes high-level user intent into a clean, 3-tier document hierarchy stored under `.deep-plan/<epic-slug>/`. Each tier serves a specific cognitive layer and consumer.

---

## 1. Directory Structure

```text
.deep-plan/<epic-slug>/
├── 00-tier1-epic.md              # High-Level: Scope, Invariants, NFRs
├── 01-architecture-overview.md   # Mid-Level: System Architecture & Data Flow
├── modules/                      # Mid-Level: Module/Component Specifications
│   ├── M01-[name].md
│   └── M02-[name].md
├── tasks/                        # Low-Level: Atomic Worker Cards (Execution Unit)
│   ├── T01-[name].md
│   ├── T02-[name].md
│   └── T03-[name].md
├── dependency-dag.json           # Machine-readable task execution graph
└── progress-ledger.md            # Swarm execution status and review log
```

---

## 2. Step 3.1: Generate Tier 1 Epic Document
- Template: `templates/tier1-epic-template.md`
- Written by PM directly using the user request and Grounding Dossier.
- Enforces:
  - Explicit Problem Statement (not literal prompt).
  - Numbered System Invariants (`INV-1`, `INV-2`).
  - Clear In-Scope modules vs. Out-of-Scope items.

---

## 3. Step 3.2: Generate Tier 2 Module Specs
- Template: `templates/tier2-module-template.md`
- PM dispatches the **System Architect Subagent** (`references/subagents/system-architect.md`).
- For each in-scope module:
  - Creates `modules/M{n}-[name].md`.
  - Defines exact interface contracts (TypeScript types, schema migrations, REST/gRPC signatures).
  - Maps sequence diagrams and data flow.
  - Specifies module-level sad paths and error handling contracts.

---

## 4. Step 3.3: Generate Tier 3 Atomic Tasks & DAG
- Template: `templates/tier3-task-template.md`
- PM dispatches the **Task Decomposition Specialist** (`references/subagents/task-decomposer.md`).
- Decomposes each Tier 2 module into atomic tasks stored in `tasks/T{n}-[name].md`.

### The Atomic Task Contract
Every Tier 3 task must meet the **Zero Ambiguity Standard**:
1. **Bounded Context:** Bounded to 1–2 files and achievable within a single worker context.
2. **Exact Targets:** Explicit file paths and target lines/functions.
3. **Traceability:** Links to parent Module (`M{m}`) and relevant Invariant (`INV-x`).
4. **Concrete Sad Path:** Explicit edge cases, timeouts, or error handling.
5. **Machine Verification & Non-Vacuity:** Test command must fail against pre-implementation code and pass cleanly post-implementation.

### Generating `dependency-dag.json`
The Task Decomposer generates the machine-readable DAG:
```json
{
  "epic": "epic-slug",
  "tasks": [
    { "id": "T01", "module": "M01", "complexity": "low", "dependencies": [] },
    { "id": "T02", "module": "M01", "complexity": "mid", "dependencies": ["T01"] },
    { "id": "T03", "module": "M02", "complexity": "low", "dependencies": ["T01"] },
    { "id": "T04", "module": "M02", "complexity": "mid", "dependencies": ["T02", "T03"] }
  ]
}
```

---

## 5. Planning Gate Check
- In **Autonomous Mode**: PM verifies all documents exist, validates the DAG for acyclicity, initializes `progress-ledger.md`, and transitions directly to execution (Phase 4).
- In **Collaborative Mode**: PM presents the Tier 1 summary and module map to the user for confirmation before launching Phase 4 execution.
