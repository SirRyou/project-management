# Scope Analysis (Phase 1)

Guides the agent through Phase 1 (Understand Scope) of the deep-plan workflow.

---

## Phase 1 — Load Context

### 1A. Resolve Standards Source

Search order:

1. `references/resilience-first-development.md` in skill dir
2. None found → use embedded generic standard in `gap-analysis.md`

Project doc exists → read full, extract relevant sections per lens.

### 1B. Read Scope Source

Look for `STATE.md`, `ROADMAP.md`, or equivalent. Extract:

```
EPIC: [name]
STATUS: [current state]
DEPENDENCIES: [what this epic depends on]
PREVIOUS PHASE SUMMARY: [what completed before]
KNOWN GAPS: [explicit gaps or TODOs]
```

No tracking doc → ask user for epic name, status, dependencies.

Multiple epics → ask which to plan.

### 1C. Scan for Review Tools

Detect available CLI tools for adversarial review. Check if different model backend/provider:

- **Different provider available** (`claude`, `codex`, `gemini`, `ollama`, etc.) → use for independent review.
- **Same provider only** → note same-model bias in review log. Merge the two review passes into a single pass.

---

## Phase 1 → Phase 2 Checkpoint

### Draft Scope Brief

```markdown
## Scope Brief: [Epic Name]

### Underlying Problem
One sentence: actual problem solved (not literal request).

### Objective
One paragraph: what this phase accomplishes.

### In Scope
- [item] — reason

### Out of Scope
- [item] — reason (defer / not this epic / already done)

### System Invariants This Phase Must Preserve
- [ ] [invariant] — tasks touching it

### Trust Boundaries This Phase Touches
- [ ] [boundary] — tasks crossing it

### Assumptions
- [assumption that breaks scope if wrong]
```

### Checkpoint — Confirm with User

**STOP. No Phase 2 without explicit confirmation.**

Present the scope brief and ask user to confirm or request changes.

User requests changes → update brief, present again, repeat checkpoint.
Confirmed → proceed to Phase 2.

> **Why hard:** Scope creep during enumeration is the number one cause of bloated roadmaps. Lock here prevents gap-found temptations.

### Scope Unlock Trigger

Lock not permanent. If Phase 2 discovers MISFIT or CRITICAL invariant violations:

1. **Auto-unlock**: Lock breaks. Gap analysis pauses.
2. **Re-scope**: Present findings to user. Update scope brief (add/remove/accept as debt).
3. **Re-lock**: User confirms updated scope. Gap analysis resumes.

> **Why:** Lock prevents casual creep. Genuine discoveries (MISFIT/CRITICAL) = gap analysis doing its job. Forcing wrong scope = plan solves wrong problem.
