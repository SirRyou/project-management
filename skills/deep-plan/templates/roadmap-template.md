# Phase X — <Roadmap Name>

> Resilience-first. Design the failure paths before extending the happy path.

---

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

- [ ] [boundary, e.g. "user input → command/query", "agent → shell exec"] — which tasks cross it
- [ ] ...

---

## System Invariants

These rules must always remain true regardless of implementation.

- [ ] Only one active runtime/session.
- [ ] No leaked resources.
- [ ] Persistent state is always valid.
- [ ] Abort always cleans up.
- [ ] Context never exceeds configured limits.
- [ ] Tool execution cannot corrupt runtime state.

_(Add project-specific invariants here.)_

---

## Guiding Methodology

For every feature:

1. Define the invariant(s) it must preserve.
2. Verify it solves the underlying problem (not just the literal ask).
3. Enumerate failure modes.
4. Identify security risks and trust boundaries.
5. Write failing tests.
6. Implement the smallest safe solution.
7. Verify exit criteria.

**Never implement the happy path alone.**

---

## Architecture Decisions

Record decisions that affect multiple work streams.

| ID  | Decision | Rationale | Affects       | Status   |
| --- | -------- | --------- | ------------- | -------- |
| D1  | ...      | ...       | T1, T2        | Accepted |
| D2  | ...      | ...       | WS3           | Accepted |

> When a decision is superseded, mark it `Superseded by Dxx` rather than deleting it.

---

## Work Streams

---

### WS1 — <Name>

#### Objective

Why this work stream exists and what invariants it protects.

#### Problem-Fit

- **Literal ask:** What was requested.
- **Underlying goal:** What actually needs to be true for the user.
- **Gap:** Does the literal ask fully close that gap?
- **Verdict:** FIT / PARTIAL FIT (missing: ...) / MISFIT

#### Invariants

- ...
- ...

#### Failure Modes

- ...
- ...
- ...

#### Security Risks

| # | Risk | Trust Boundary Crossed | Adversarial Trigger | Impact |
| --- | --- | --- | --- | --- |
| S1 | ... | ... | ... | ... |

_(If no security surface: `No security surface — reason: [why]`)_

#### Tasks

| ID  | Task | Depends On | Risk   | Status |
| --- | ---- | ---------- | ------ | ------ |
| T1  | ...  | None       | Low    | TODO   |
| T2  | ...  | T1         | Medium | TODO   |

#### Implementation Notes

- **Approach:** High-level design choice and why.
- **Tradeoffs:** What was considered and rejected.
- **References:** Relevant docs, SDK sections, prior decisions.

#### Sad Paths

- **T1:** What can go wrong. **Mitigation:** How it's handled.
- **T2:** What can go wrong. **Mitigation:** How it's handled.

#### Exit Criteria

- [ ] ...
- [ ] ...

---

### WS2 — <Name>

_(repeat WS1 structure)_

---

## Cross-Cutting Work

### Testing

| ID  | Task | Depends On | Status |
| --- | ---- | ---------- | ------ |
| T17 | ...  | WS1-T1     | TODO   |

### Refactoring

| ID  | Task | Depends On | Status |
| --- | ---- | ---------- | ------ |
| T22 | ...  | None       | TODO   |

_Why this matters: [brief rationale — don't skip this, cross-cutting work gets dropped when undocumented.]_

### Type Safety

| ID  | Task | Depends On | Status |
| --- | ---- | ---------- | ------ |
| T24 | ...  | None       | TODO   |

### Documentation

| ID  | Task | Depends On | Status |
| --- | ---- | ---------- | ------ |
| T27 | ...  | None       | TODO   |

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

  - Timebox: (Human: X) , (Agent: Y)
  - Goals: What this sprint achieves.
  - Tasks: T1, T2, T3
  - Expected Outcome: System is in this state at end of sprint.

---

- **Sprint 2**

  - Timebox: (Human: X) , (Agent: Y)
  - Goals: ...
  - Tasks: ...
  - Expected Outcome: ...

---

- **Sprint N**

  - Timebox: (Human: X) , (Agent: Y)
  - Goals: ...
  - Tasks: ...
  - Expected Outcome: ...

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| ... | Low | High | ... |

---

## Research Backlog

Open technical questions. When resolved, move findings into Architecture Decisions or Implementation Notes — don't leave answers orphaned here.

| ID  | Question | Priority | Status   |
| --- | -------- | -------- | -------- |
| R1  | ...      | High     | Open     |
| R2  | ...      | Medium   | Resolved |

---

## Review Log

| Review | Model | Mode | Findings | Status |
| --- | --- | --- | --- | --- |
| Scope/Problem-Fit | ... | external / internal | N findings, M incorporated | Cleared |
| Eng/Security | ... | external / delegate / subagent | N findings, M incorporated | Cleared |
| Design/UI-UX | ... | ... | N findings, M incorporated | Cleared / Deferred |

---

## Progress Tracker

| Stream | Tasks | Done | Progress |
| --- | --- | --- | --- |
| WS1 | 5 | 0 | 0% |
| WS2 | 4 | 0 | 0% |
| Cross-Cutting | 8 | 0 | 0% |

---

## Completion Checklist

### Functional

- [ ] ...

### Problem-Fit

- [ ] Every PARTIAL FIT / MISFIT resolved or accepted as debt.

### Resilience

- [ ] ...

### Security

- [ ] All trust boundary crossings have corresponding S-id tasks.
- [ ] No WS with input/auth/third-party surface has empty Security Risks.

### Testing

- [ ] ...

### Documentation

- [ ] ...

### Performance

- [ ] ...

---

## Lessons Learned

Filled after implementation. Don't skip — this feeds the next phase.

...
