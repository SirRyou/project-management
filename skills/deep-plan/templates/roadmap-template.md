# <Roadmap Name>

> **This is the append-order skeleton, not a strict final layout.** The roadmap is written
> incrementally (progressive write). Each phase appends its section to `.deep-plan/<name>.md` in
> place. A section that doesn't exist yet simply hasn't been reached. The *required-section checklist*
> in [quality-gates.md](../references/quality-gates.md) verifies each **heading exists** by the end of
> Phase 4 — it does NOT require the file to physically match this order in a single final pass.
>
> Sections below are tagged **(Phase N)** = which phase writes them. Read-only consumers (execution
> handoff, retro) locate content by heading, not by position.

---

## PROBLEM (Phase 1)

One sentence: the underlying problem being solved, **not** the literal prompt.
If literal ask == underlying problem, say so explicitly.

## OBJECTIVE (Phase 1)

One paragraph: what this epic accomplishes.

## IN-SCOPE (Phase 1)

- [ ] [item] — rationale. Each item = atomic sub-feature, the sequential unit of Phase 2 analysis.

## OUT-OF-SCOPE (Phase 1)

- [item] — rationale (deferred, out of bounds).

## BLOCKERS (Phase 1, optional)

- [item] — must resolve before execution. Omit section entirely if none.

## SYSTEM INVARIANTS & TRUST BOUNDARIES (Phase 1)

Rules that must always remain true regardless of implementation. Fill in project-specific ones.

- [ ] [invariant / boundary] — area of concern (e.g. database transactions, auth rules)

## ASSUMPTIONS (Phase 1, optional)

- [assumption] — project risk if wrong. Omit section entirely if none.

## Codebase Context (Phase 1)

- Relevant files (paths + one-line purpose)
- Schemas / constraints
- Patterns new code must follow
- Tests that could break
- Unverified unknowns

## Research Backlog (Phase 1 placeholder, Phase 2+ logs)

| ID | Question | Priority | Status |
| -- | -------- | -------- | ------ |
| R1 | ...      | High     | Open   |

---

## Phase 2: Gap Analysis (Phase 2)

Enumerate gaps adversarially, **per IN-SCOPE item**. Failure Modes / Security Risks **live here** in
2A-2D; Phase 3 Work Streams reference them by F-id / S-id rather than duplicating. Ends with the
consolidation (E) and review gate (F).

### Problem-Fit & Status: [Item] (2A)

- **Literal ask:** [what was requested]
- **Underlying goal:** [what actually needs to be true]
- **Gap:** [does the literal ask fully close it? what's missing?]
- **Verdict:** FIT | PARTIAL_FIT (missing: ...) | MISFIT
- **Invariant Impact:** [Preserved | Threatened]
- **Blocker Status:** [NONE | BLOCKER - Reason]

_(Repeat 2A-2D per item.)_

#### Failure Modes (2B)

| # | Failure Mode | Trigger | Impact | Machine Exit Verification |
| - | ------------ | ------- | ------ | ------------------------- |
| F1 | [..] | [..] | [..] | [command / test] |

#### Security Risks (2C)

| # | Risk | Trust Boundary Crossed | Adversarial Trigger | Impact | Defense Contract |
| - | ---- | ---------------------- | ------------------- | ------ | ---------------- |
| S1 | [..] | [..] | [..] | [..] | [..] |

_(If no security surface: `No security surface — reason: [why]`.)_

#### Invariant & Boundary Violation Check (2D)

- [silent-violation notes] -> mark CRITICAL, require automated assertion.

#### Work Stream Consolidation (2E)

Cluster gaps/FMs/risks into deliverable work streams.

#### Review Gate (2F)

Collection of BLOCKER / MISFIT / PARTIAL_FIT items. Present and get answer before Phase 3.

#### Research Addendum (2G)

Resolved unknowns + industry alignment that validates (or adjusts) the design.

---

## Phase 3: Roadmap (Phase 3)

### Architecture Decisions

Decisions affecting multiple work streams.

| ID | Decision | Rationale | Affects | Status |
| -- | -------- | -------- | ------  | ------ |
| D1 | [..] | [..] | T1, T2 | Accepted |

> Superseded decision -> mark `Superseded by Dxx`, never delete.

### Work Streams

#### WS1 — <Name>

##### Objective

Why this work stream exists and what invariants it protects.

##### Tasks

| ID | Task | Depends On | Mitigates (F-/S-id) | Risk | Status |
| -- | ---- | ---------- | ------------------- | ---- | ------ |
| T1 | [..] | None | F1, S1 | Low | TODO  |

> Every failure mode and security risk from 2A-2D must trace to >=1 task via Mitigates;
> unmitigated F-/S-id = failed Phase 3 checklist.

##### Sad Paths

- **T1:** What can go wrong. **Mitigation:** How it's handled.

##### Exit Criteria

- [ ] [Machine Verification Command: `npm test` / `pytest` / `git diff`] — must pass cleanly

##### Unit Tests (per-WS, required)

- [ ] Minimal unit test(s) for THIS work stream's own logic. Each WS must own its unit tests
      locally — cross-WS / integration / e2e coverage goes in `Cross-Cutting Work`, not here.

---

### Cross-Cutting Work (required)

Tasks that bridge multiple work streams or sprints: **integration / e2e tests**, shared
refactoring, type-safety wiring, migration glue. Owned here, not parked inside a WS.

| ID | Task | Work Stream | Depends On | Status |
| -- | ---- | ----------- | ---------- | ------ |
| X1 | [e2e/integration harness] | WS1, WS3 | WS1-T1 | TODO  |

---

### Dependency Graph (Phase 3)

```text
WS1
 ├── T1 (independent)
 ├── T2 <- T1
 │
 ▼
WS2 ...

Cross-Cutting:
  X1 (e2e) — after WS1 + WS4
```

### Implementation Order (Phase 3)

- **Sprint 1** — Tasks: ... / Expected Outcome: ...

### Risks (Phase 3)

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| ...  | Low | High | ... |

### Completion Checklist (Phase 5)

### Review Log (Phase 4)

| Review | Engine | Mode | Findings | Status |
| ------ | ------ | ---- | -------- | ------ |
| CTO / Eng / UI | ... | external | N findings, M incorporated | Cleared |

---

## Phase 4: Findings & Amendments (Phase 4)

Trail of CTO / Eng / UI passes + judge decisions + amendments applied as edits to the
relevant Phase 2/3 sections.

- **CTO Pass:** [finding -> amendment -> decided]
- **Eng/Security Pass:** ...
- **Judge's Decisions & Amendments:** compiled, with why.
