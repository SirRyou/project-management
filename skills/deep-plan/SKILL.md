---
name: deep-plan
description: >
  Adversarial-reviewed roadmap for multi-file features. Phased planning
  with scope analysis, gap enumeration, and outside-voice review.
  NOT for trivial changes, single-file edits, or simple bug fixes.
triggers:
  - "plan this feature"
  - "design an epic"
  - "break down this work"
  - "create a roadmap"
requires:
  - file-read
  - file-write
  - question
capabilities:
  optional:
    - subagent        # for adversarial review with different model
    - web-search      # for external pattern research
---

# Deep Plan

## Iron Law

Never begin implementation without explicit user confirmation after Phase 5.

## Execution Path

Decide at entry:

| Criteria | Quick Path | Full Path |
|----------|-----------|-----------|
| Files affected | <=3 | >3 |
| Work streams | <=3 | >3 |
| CRITICAL security items expected | 0 | any |

**Auto-escalate** from Quick to Full if Phase 2 yields `MISFIT` or `CRITICAL` items, or total scope exceeds 15 tasks.

Quick Path: skip to [quick-path.md](references/quick-path.md) (3-step workflow, 1 checkpoint).
Full Path: Phases 1-5 below (3 checkpoints).

## Core Principles (in priority order)

1. Solve the underlying problem, not the literal request
2. Preserve system invariants — explicitly define machine-checkable exit assertions
3. Identify failure modes early — plan sad paths before implementation
4. Protect trust boundaries — explicitly design security models
5. Keep work packages independently deliverable

## Full Path Workflow

### Pre-flight

```bash
git status --porcelain
git log --oneline -1 @{upstream}...HEAD 2>/dev/null || echo "no upstream"
```

Warn if uncommitted changes or branch divergence. Recommend stash/commit/pull before planning.

### Phase 1: Understand Scope

Read scope source (`STATE.md`, `ROADMAP.md`, or equivalent). Extract: epic name, status, dependencies, known gaps. No tracking doc → ask user.

*Detailed guide: [scope-analysis.md](references/scope-analysis.md)*

### Phase 2: Enumerate Gaps

Analyze under three lenses (parallel if possible):

1. **Problem-Fit**: Does the literal request fully solve the underlying problem?
2. **Resilience**: Failure modes — timeouts, concurrency, duplicate calls, partial updates. Includes command-line machine verification assertions. *For resilience standards: [resilience-first-development.md](references/resilience-first-development.md)*
3. **Security**: Input abuse, missing permission checks, exposed secrets. Includes defense contracts.

Tag each gap: `FIT`, `MISFIT`, or `CRITICAL`.

*Detailed guide: [gap-analysis.md](references/gap-analysis.md)*

### Phase 3: Draft Roadmap

Construct tentative roadmap. Work streams with tasks, dependencies, exit criteria.

*Template: [roadmap-template.md](templates/roadmap-template.md)*
*Guide: [roadmap-draft.md](references/roadmap-draft.md)*

### Phase 4: Adversarial Review

**Skip gate:** Phase 4 is skipped when Phase 2 yielded all `FIT`, 0 `CRITICAL`, and <=5 total gaps. Otherwise, run the review.

Run review using "outside voice" — different training perspectives catch blind spots.

Priority order:
1. CLI model in PATH (`claude`, `codex`, `ollama`, etc.)
2. Subagent with different model provider
3. Same-model subagent (must include explicit counter-bias checklist)

*Detailed guide: [adversarial-review.md](references/adversarial-review.md)*

### Phase 5: Finalize Roadmap

Generate final roadmap. **STOP. Do not begin implementation without explicit user confirmation.**

After confirmation, hand off to execution: *Guide: [execution-handoff.md](references/execution-handoff.md)*

*Quality gates: [quality-gates.md](references/quality-gates.md)*

### Non-linear & Mid-Execution Flow

- Phase 4 review finds scope issues → jump back to Phase 2
- Phase 2 yields all FIT, 0 CRITICAL, <=5 gaps → skip Phase 4
- **Mid-Execution Scope Drift / Blocker**: If execution hits an invariant violation or unblocked scope growth during coding, activate the [reentry-protocol.md](references/reentry-protocol.md) for targeted delta planning.

## UI Projects

If roadmap touches visual components, run UI review checklist after Phase 5.
*Guide: [ui-review.md](references/ui-review.md)*

## Common Failure Modes

- Skipping adversarial review → missing edge cases, single-path designs
- Implementing before user approval → builds the wrong thing
- Vague task descriptions → no verification criteria, no exit conditions
- Scope creep during gap enumeration → bloated roadmaps

## Runtime Bindings

This skill requires these capabilities from the host runtime:

- **file-read**: Read source files, tracking docs, scope sources
- **file-write**: Write `.deep-plan/plan.md` and references
- **question**: Checkpoint confirmations with user (3 in Full Path, 1 in Quick Path)
- **subagent** (optional): Adversarial review with different model
- **web-search** (optional): External pattern research

If a required capability is unavailable, degrade gracefully:
- No question tool → render checkpoint as prose, wait for typed reply
- No subagent → use same-model with fresh context + counter-bias checklist
- No web-search → skip external pattern search, proceed with local analysis
