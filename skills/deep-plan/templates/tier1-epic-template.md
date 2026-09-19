# Tier 1: Epic Overview & Invariants

> **Scope & Invariant Contract**
> Defines the business problem, objective, invariants, and scope boundaries.
> Written during Planning Phase 1 & 2. Ground truth for all downstream modules and tasks.

---

## 1. Problem & Business Objective
- **Problem Statement:** [One sentence: underlying problem being solved, not the literal prompt]
- **Target Persona & User Story:** [Who is this for, and what job does it accomplish?]
- **Business Impact / Objective:** [Measurable outcome or system capability unlocked]

---

## 2. System Invariants & Trust Boundaries
*Rules that must ALWAYS remain true across all modules and tasks.*

| ID | Invariant / Boundary | Area / Component | Enforcement Mechanism |
| :--- | :--- | :--- | :--- |
| **INV-1** | [e.g. Invariant statement] | [e.g. Auth / DB / State] | [e.g. DB transaction constraint, middleware check] |
| **INV-2** | [e.g. Invariant statement] | [e.g. Billing / API] | [e.g. Idempotency key, mutual exclusion lock] |

---

## 3. Scope Boundaries

### In-Scope (Deliverable Modules)
- **M01 — [Module Name]:** [High-level purpose and boundary]
- **M02 — [Module Name]:** [High-level purpose and boundary]

### Out-of-Scope (Deferred / Excluded)
- **[Feature / Edge Case]:** [Rationale for excluding]
- **[Future Enhancement]:** [Rationale for excluding]

---

## 4. Non-Functional Requirements (NFR)
- **Performance / Latency:** [Max latency, throughput, or memory budgets]
- **Backward Compatibility:** [Deprecation window, migration constraints, zero-downtime requirements]
- **Observability:** [Required logs, correlation IDs, telemetry metrics]

---

## 5. Module Map & Dependency Topology
```text
[M01: Name] ──► [M02: Name] ──► [M03: Name]
```
*(References Tier 2 specification documents in `modules/`)*
