# Reference: Quality Gates & Self-Check Checklist

This reference document outlines the quality gates required before finalizing the phase roadmap.

---

## 1. High-Level Quality Gates

Before saving and presenting the final roadmap, verify the following:

- [ ] **Scope Alignment**: Every in-scope item has at least one corresponding task.
- [ ] **Gap Mitigations**: All critical/high failure modes and security risks have explicit mitigation tasks.
- [ ] **Machine Verification Commands**: Every task has a machine-executable verification command (e.g. `npm test`, `pytest`, `cargo test`, `git diff`) — no subjective "looks good" text.
- [ ] **Invariant Assertions**: System invariants are explicitly checked before and after execution steps.
- [ ] **Git-Aware Versioning**: The roadmap is updated incrementally in the living `.deep-plan/<epic-name-in-kebab-case>.md` file.
- [ ] **Required Sections Present**: The finalized roadmap contains every required section from [roadmap-template.md](../templates/roadmap-template.md), matched **by heading**, not by physical position (the file is phase-appended; order varies). Required:
  - Phase 1 block: `## PROBLEM`, `## OBJECTIVE`, `## IN-SCOPE`, `## OUT-OF-SCOPE`, `## SYSTEM INVARIANTS & TRUST BOUNDARIES`, `## Codebase Context`, `## Research Backlog` (optional: `## BLOCKERS`, `## ASSUMPTIONS`)
  - Phase 2 block: `## Phase 2: Gap Analysis` containing per-item `Problem-Fit & Status`, `Failure Modes`, `Security Risks`, and the `Review Gate` (2F)
  - Phase 3 block: `## Phase 3: Roadmap` containing `### Architecture Decisions`, `### Work Streams` (each WS has Objective, Tasks, Sad Paths, Exit Criteria, **and Unit Tests**), `### Cross-Cutting Work`, `### Dependency Graph`, `### Implementation Order`, `### Risks`, `### Completion Checklist`, `### Review Log`
  - Phase 4 block: `## Phase 4: Findings & Amendments`
- [ ] **Per-WS Unit Tests**: Every work stream owns minimal unit test(s) for its own logic. Cross-WS / integration / e2e tests live in `## Cross-Cutting Work`, not inside a WS.
- [ ] **Test Non-Vacuity**: Every new test that guards a failure handler or edge case must **fail against pre-fix code** — assert the test is credible before the fix exists. A test that passes both pre-fix and post-fix asserts nothing. Mark non-vacuity as an explicit acceptance criterion on the task, not an afterthought.
- [ ] **User Agreement**: All adversarial review findings are resolved and confirmed by the user.
