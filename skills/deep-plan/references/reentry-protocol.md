# Mid-Execution Plan Re-Entry Protocol

Guides the agent when unexpected scope drift, broken system invariants, or persistent blockers occur during implementation.

---

## 1. Re-Entry Triggers

Re-enter planning mode when any of the following occur during execution:

- **Scope Breach**: Implementation uncovers required tasks expanding overall scope by >15% or adding new external security boundaries.
- **Invariant Violation**: A code change breaks an existing system invariant or regression test that cannot be fixed within the current work package.
- **3-Strike Blocker**: 3 consecutive execution attempts fail on a single task.
- **Architectural Misfit**: Discovered code realities directly contradict assumptions in the active roadmap.

---

## 2. Re-Entry Procedure (Targeted Delta Planning)

Do NOT erase the existing roadmap or restart from Phase 1. Perform targeted incremental re-planning:

1. **Pause Implementation**: Freeze active branch state. Mark affected task `BLOCKED` in execution tracking.
2. **Execute Delta Gap Analysis (Phase 2 Delta)**:
   - Run 3 lenses (*Problem-Fit*, *Resilience*, *Security*) **only** on the newly discovered scope or blocker.
   - Categorize new gaps: `FIT`, `MISFIT`, or `CRITICAL`.
3. **Execute Mini-Adversarial Pass (Phase 4 Delta)**:
   - Validate proposed roadmap adjustment against existing system invariants.
4. **Update Active Plan**:
   - Insert delta work package into active `.deep-plan/plan.md`.
   - Re-sequence downstream dependencies.
5. **Resume Handoff Checkpoint**:
   - Present delta changes to user for confirmation before resuming execution.
