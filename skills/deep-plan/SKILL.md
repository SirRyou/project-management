---
name: deep-plan
description: Use when planning medium-to-large engineering features, epics spanning multiple files or layers, or changes requiring complex architectural decisions and trust-boundary modifications.
license: MIT
metadata:
  version: "2.0"
---

# Deep Plan

## Overview

Deep Plan creates resilient, problem-driven, security-aware, implementation-ready roadmaps for complex software changes.

## When to Use

Use when **all** conditions met:
- **Scope**: >3 files affected
- **Complexity**: Multiple independent work streams
- **Architecture**: Design decisions or trust-boundary updates needed
- **Rollout**: Phased delivery beneficial

**When NOT to use:**
- Trivial changes, single-file edits, simple bug fixes. Use direct implementation instead.

## Core Principles

Optimize priorities:
1. **Solve underlying problem** — not just literal request
2. **Preserve system invariants** — don't break existing guarantees
3. **Identify failure modes early** — plan sad paths before implementation
4. **Protect trust boundaries** — explicitly design security models
5. **Independent deliverability** — keep work packages decoupled

### Execution Paths (Quick Path vs Full Path)

Choose workflow path based on epic complexity:

| Feature | Quick Path (Simple Epic) | Full Path (Default) |
|---------|---------------------------|---------------------|
| **Complexity Criteria** | Small changes (≤ 3 work streams, 0 `CRITICAL` failure/security items expected) | Default for all other complex changes |
| **Workflow Steps** | Fallback to [quick-path.md](references/quick-path.md) (3-step workflow) | Full Deep-Plan Workflow (Phase 1 → 5) |
| **User Checkpoints** | 1 checkpoint (Scope Brief) | 3 checkpoints (Scope, Review, Amendment) |
| **Plan Format** | Single, living `plan.md` updated incrementally | Full detailed document + templates |

**Auto-Escalate Conditions (Quick → Full Path):**
- Step 2 (Gap Analysis) yields `MISFIT` or `CRITICAL` items
- Total scope exceeds 15 tasks

### Workflow Flexibility

Phases sequential by default, non-linear flow triggers:

**Early Exit (skip Phase 4 in Full Path):**
- Phase 2 yields all `FIT` verdicts, 0 `CRITICAL` items, ≤5 total gaps → skip Phase 4. Plan clean. Proceed to Phase 5.

**Jump-Back (Phase 4 → Phase 2):**
- Phase 4 review finds scope issues (new items needed, wrong boundaries) → Update plan.

**Parallel Execution:**
- Phase 2: Problem-Fit, Resilience, Security lenses run parallel per item
- Phase 4: Steps 5 and 6 run parallel if different reviewers available

## Workflow Phases

Execute phases sequentially.

> [!NOTE]
> **Git-Awareness & Pre-flight Check**: Before planning, verify git initialized. Run `git status --porcelain` to check uncommitted changes, check if current branch diverged from upstream. If uncommitted changes or divergence, warn user, recommend stashing/committing/pulling first.
>
> **Gitignore Configuration**: Add `.deep-plan/` to `.gitignore` if planning files are local/temporary, or keep tracked if shared team documentation.
>
> **Interaction & Tool Rule**: At checkpoints, use native `ask_question` tool or equivalent. If unavailable, **STOP and ask user via plain text**.
>
> **Checkpoint Loops**: User rejects draft/scope brief → revise, present again, repeat confirmation.
>
> **Checkpoint Minimization**: 3 checkpoints: (1) Scope Brief after Phase 2, (2) Review findings after Phase 4, (3) Amendment before Phase 5.
>
> **Living Document Updates**: Don't create new plan files (e.g. `v1.md`, `v2.md`). Maintain single living `.deep-plan/plan.md` (or `.deep-plan/{feature-slug}/plan.md`). Update incrementally via code editing tools. Keeps file concise, saves tokens, enables clean `git diff` tracking.

### Phase 1: Understand Scope

Understand baseline requirements and context. If scope unclear, ask user before proceeding.
*Details: [scope-analysis.md](references/scope-analysis.md)*

### Phase 2: Enumerate Gaps

Analyze codebase using Problem Fit, Resilience, Security lenses.
*Details: [gap-analysis.md](references/gap-analysis.md)*

### Phase 3: Draft Roadmap

Construct lightweight, tentative roadmap.
*Details: [roadmap-draft.md](references/roadmap-draft.md)*

### Phase 4: Adversarial Review

Run adversarial review using "outside voice" principle — different training perspectives catch blind spots. Execution order:
1. CLI model in PATH (e.g., `claude`, `codex`, `agy`, `ollama`, `opencode`, `qwen`)
2. Subagent with different model provider
3. Same-model subagent (flag `NO_OTHER_MODEL`)
*Details: [adversarial-review.md](references/adversarial-review.md)*

### Phase 5: Finalize Roadmap

Generate final, comprehensive roadmap.
*Templates & Quality Gates: [roadmap-template.md](templates/roadmap-template.md) and [quality-gates.md](references/quality-gates.md)*

---

## Special Considerations

### UI Projects

If roadmap touches user interfaces or visual components, execute UI review checklist.
*Details: [ui-review.md](references/ui-review.md)*

### Execution Confirmation

Final roadmap execution **not automatic**. Don't begin implementation without explicit user confirmation.
*Details: [execution-handoff.md](references/execution-handoff.md)*

---

## Quick Reference

| Phase | Purpose | Target Document |
|---|---|---|
| **Phase 1** | Scope understanding | None (alignment) |
| **Phase 2** | Analyze weaknesses | Gap Analysis |
| **Phase 3** | Formulate plan | Draft Roadmap |
| **Phase 4** | Resilience check | Review Results |
| **Phase 5** | Production readiness | Final Roadmap |

---

## Common Mistakes

- **Skipping Adversarial Review**: Failing Phase 4 → missing edge cases, single-path designs
- **Starting Code Work Automatically**: Implementing before user approval
- **Vague Task Descriptions**: Roadmap items lacking concrete verification steps or boundary definitions