# Scope Analysis (Step 1 & Step 2)

Guides agent through Step 1 (Load Context) and Step 2 (Scope + Boundary).

---

## Step 1 — Load Context

### 1A. Resolve Standards Source

Search order:

1. `*references/resilience-first-development.md` in skill dir
2. None found → use embedded generic standard in `gap-analysis.md`

Project doc exists → read full, extract relevant sections per lens. Note if Lens 1/3 missing → fallback to generic.

### 1B. Read Scope Source

Look for `STATE.md`, `ROADMAP.md`, or equivalent. Extract:

```
EPIC: [name]
STATUS: [current state]
DEPENDENCIES: [what this epic depends on]
PREVIOUS PHASE SUMMARY: [what completed before]
KNOWN GAPS: [explicit gaps or TODOs]
```

No tracking doc → ask user:

```
ask_question(
  question="No tracking document found. Provide epic/feature name, status, dependencies.",
  options=["Enter details manually", "Scan again / specify custom path"]
)
```

Multiple epics → ask which to plan.

### 1C. Scan Collaborative Tools & Resolve Review Path

Detect available collaborative skills/CLI tools. For review tools, check if different model backend/provider:

- **`HAS_BACKEND`**: Different provider available (e.g. `claude`, `gpt`, `gemini`, `ollama`). Use for independent review.
- **`NO_OTHER_MODEL`**: Only same-provider available. Note same-model bias in review log. Merge Steps 5 & 6 into single review pass.

Details: see `adversarial-review.md`.

---

## Step 2 — Scope + Boundary → HUMAN CHECKPOINT

### 2A. Draft Scope Brief

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

### 2B. HARD CHECKPOINT — Human Must Confirm

**STOP. No Step 3 without explicit confirmation.**

```
ask_question(
  question="Scope brief correct? Any mismatches, missing items, or OOS items?",
  options=["Yes, proceed to Step 3.", "No, modify scope brief."]
)
```

User requests changes → update brief, present again, repeat checkpoint.
Confirmed → proceed to Step 3.

> **Why hard:** Scope creep during enumeration = #1 cause of bloated roadmaps. Lock here prevents gap-found temptations.

### Scope Unlock Trigger

Lock not permanent. If Phase 3 discovers MISFIT or CRITICAL invariant violations:

1. **Auto-unlock**: Lock breaks. Gap analysis pauses.
2. **Re-scope**: Present findings to user. Update scope brief (add/remove/accept as debt).
3. **Re-lock**: User confirms updated scope. Gap analysis resumes.

> **Why:** Lock prevents casual creep. Genuine discoveries (MISFIT/CRITICAL) = gap analysis doing its job. Forcing wrong scope = plan solves wrong problem.
