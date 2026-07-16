# Phase X — <Roadmap Name>

## Context

## Objective

Describe what this phase is trying to accomplish.

### Underlying Problem

One sentence: what problem is actually being solved (not what was literally asked)?
If the literal request and the underlying problem are the same, state that explicitly.

## Current State

- Existing capabilities
- Known limitations
- Technical debt
- Previous phase summary

## Scope

### In Scope

- ...

### Out of Scope

- ...

### Trust Boundaries This Phase Touches

- [ ] [boundary] — which tasks cross it

---

## System Invariants

Rules that must always remain true regardless of implementation. Fill in project-specific invariants — the list below is a starting point, not a prescription.

- [ ] ...
- [ ] ...

---

## Architecture Decisions

Record decisions that affect multiple work streams.

| ID | Decision | Rationale | Affects | Status |
|----|----------|-----------|---------|--------|
| D1 | ... | ... | T1, T2 | Accepted |

> When a decision is superseded, mark it `Superseded by Dxx` rather than deleting it.

---

## Work Streams

### WS1 — <Name>

#### Objective

Why this work stream exists and what invariants it protects.

#### Problem-Fit

- **Literal ask:** What was requested.
- **Underlying goal:** What actually needs to be true for the user.
- **Gap:** Does the literal ask fully close that gap?
- **Verdict:** FIT / PARTIAL FIT (missing: ...) / MISFIT

#### Failure Modes

- ...

#### Security Risks

| # | Risk | Trust Boundary Crossed | Adversarial Trigger | Impact |
|---|------|------------------------|----------------------|--------|
| S1 | ... | ... | ... | ... |

_(If no security surface: `No security surface — reason: [why]`)_

#### Tasks

| ID | Task | Depends On | Risk | Status |
|----|------|------------|------|--------|
| T1 | ... | None | Low | TODO |

#### Sad Paths

- **T1:** What can go wrong. **Mitigation:** How it's handled.

#### Exit Criteria

- [ ] ...

---

### WS2 — <Name>

_(repeat WS1 structure)_

---

## Cross-Cutting Work

| ID | Task | Work Stream | Depends On | Status |
|----|------|-------------|------------|--------|
| T17 | ... | Testing | WS1-T1 | TODO |
| T22 | ... | Refactoring | None | TODO |

---

## Dependency Graph

```text
WS1
 ├── T1  (independent)
 ├── T2  (independent)
 ├── T3  ← T1
 │
 ▼
WS2
 ├── T4  (independent)
 ├── T5  ← T3
 │
 ▼
WS3

Cross-Cutting:
  T17-T21 (tests) — run parallel with each WS
  T22-T25 (type safety) — independent, run anytime
```

---

## Implementation Order

- **Sprint 1**
  - Goals: What this sprint achieves.
  - Tasks: T1, T2, T3
  - Expected Outcome: System state at end of sprint.

- **Sprint 2**
  - Goals: ...
  - Tasks: ...
  - Expected Outcome: ...

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ... | Low | High | ... |

---

## Research Backlog

Open technical questions. When resolved, move findings into Architecture Decisions or Implementation Notes.

| ID | Question | Priority | Status |
|----|----------|----------|--------|
| R1 | ... | High | Open |

---

## Review Log

| Review | Model | Mode | Findings | Status |
|--------|-------|------|----------|--------|
| Scope/Problem-Fit | ... | external / internal | N findings, M incorporated | Cleared |
| Eng/Security | ... | external / delegate / subagent | N findings, M incorporated | Cleared |

---

## Completion Checklist

### Problem-Fit

- [ ] Every PARTIAL FIT / MISFIT resolved or accepted as debt.

### Resilience

- [ ] All critical/high failure modes have mitigation tasks.

### Security

- [ ] All trust boundary crossings have corresponding S-id tasks.
- [ ] No WS with input/auth/third-party surface has empty Security Risks.

### Testing

- [ ] Every task has a concrete, testable exit criterion.

### User Confirmation

- [ ] All adversarial review findings resolved and confirmed by user.
