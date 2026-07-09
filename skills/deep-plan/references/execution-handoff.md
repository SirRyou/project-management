# Execution Handoff (Phase 5 → Implementation)

Hand finalized roadmap to execution. Three rules: isolation, task unit format, implementation review.

---

## 1. Opt-In

Handoff optional. Confirm with user after roadmap finalized:

```
ask_question(
  question="Roadmap finalized. Hand off to execution or stop for manual review?",
  options=["Hand off to execution", "Stop here"]
)
```

Declined → stop. Finalized roadmap = final deliverable.

## 2. Isolation Rule

**Never continue in same context that ran planning.**

Planning context loaded with drafts, review findings, rejected ideas, intermediate checklists. Wastes tokens, causes errors.

Execution starts in fresh session/subagent. Reads only finalized roadmap file.

---

## 3. Task Unit Format

Each task self-contained. Implementing agent needs no other context.

```
### T[n] — [task title]

- **Parent WS:** [one line objective context]
- **Steps:** [bite-sized, ordered, independently verifiable]
- **Exit criteria:** [testable, specific]
- **Sad paths:** [F-id + one-line description]
- **Security risks:** [S-id + one-line description]
- **Constrained by:** [D-ids]
- **Depends on:** [T-ids]
```

Bare task titles = agent stalls or drifts. Always include steps, exit criteria, sad paths inline.

---

## 4. Implementation Review

After sprint/WS implementation completes, verify against plan requirements:

- Exit criteria met?
- Sad paths handled?
- Security risks addressed?
- Constraints respected?
- Dependencies satisfied?

Gaps → flag for rework. Match implementation to plan, not plan to implementation.

---


---

## Anti-Patterns

- **Auto-chaining** — starting implementation immediately after Step 7. Skips user review.
- **Batched execution** — handing off high-level roadmap without expanded task units.
- **Same context** — writing code in planning session. Wastes tokens.
- **Bare titles** — delegating task list without steps/exit criteria/sad paths.
