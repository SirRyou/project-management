---
name: deep-plan
description: >
  Performs structured pre-code planning for non-trivial features. Use when the user requests a plan,
  epic, roadmap, or approach review, or when a change couples >3 files with cross-file dependencies/design
  decisions, mutates DB schemas, touches auth/trust boundaries, or adds concurrency.
---

# Deep Plan

## Iron Law
**Never begin implementation without explicit user confirmation of the finalized roadmap.**

## Entry Decision
1. **Decline** if change is trivial (docs, typos, comments). Suggest coding directly.
2. **Full Path triggers** (any one): DB schema mutation, new auth/permission boundary, concurrent flow, multi-file coupling (>3 files) with cross-file dependencies/design decisions, or high rollback risk.
3. **Default:** Quick Path (see [quick-path.md](references/quick-path.md)).

## Core Execution Rules
*   **Progressive Write:** Write each phase's output directly to the roadmap file `.deep-plan/<epic-name-in-kebab-case>.md` as you execute it. Do not wait until the end.
*   **Unknowns Resolution:** Handle unknowns immediately: 1) verify via web search, 2) ask the user, or 3) log as `R{n}` in the roadmap's research backlog.

---

## Full Path Phases
For each phase, read its reference file **only** when starting that phase.

### Phase 1: Scope Analysis
1. Read [scope-analysis.md](references/scope-analysis.md).
2. Synthesize the Scope Brief and codebase context.
3. **Hard Stop:** Wait for user confirmation of the brief before writing the file.

### Phase 2: Gap Analysis (Adversarial)
1. Read [gap-analysis.md](references/gap-analysis.md).
2. Run gap check. **Hard Stop:** If any blockers or mismatches are found, present them and pause.

### Phase 3: Draft Roadmap
1. Read [roadmap-draft.md](references/roadmap-draft.md).
2. Break down tasks. Flag if >8 streams or >30 tasks.

### Phase 4: Adversarial Review
1. Skip Phase 4 only if Phase 2 yielded all `FIT` (no MISFIT/PARTIAL_FIT), 0 `CRITICAL`, and <=5 total gaps.
2. Read [adversarial-review.md](references/adversarial-review.md) to stress-test the draft.
3. If UI/frontend work is present, also read and execute [ui-review.md](references/ui-review.md), appending its findings to the Phase 4 checkpoint.

### Phase 5: Quality Gate & Approval
1. Read [quality-gates.md](references/quality-gates.md).
2. Run checklist. **Hard Stop:** Present final roadmap and ask to hand off or stop.

### Phase 6: Post-Execution Retro
1. If handoff was approved, read [retro.md](references/retro.md) post-completion to calibrate.
