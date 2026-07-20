---
name: deep-plan
description: >
  Use this for any non-trivial feature or change that needs a plan before coding — from a
  small, contained addition to a complex multi-file epic. Internally picks Quick Path (small,
  linear, low-risk — 3 steps, still produces a reviewed roadmap) or Full Path (multi-stage,
  state/schema changes, unknowns, trust-boundary work — 5+ phases with adversarial review) based
  on the criteria in Execution Path below. Do not skip this skill just because a request sounds
  small — Quick Path exists exactly for that case. Only skip entirely for single-file edits,
  simple bug fixes, or changes with no real design decision to make.
  example triggers — complex: "Plan this feature", "Design an epic", "Architectural planning",
  "Break down this work", "Create a roadmap". small/quick: "quick plan for X before I start
  coding", "sanity-check this approach", "small feature, still want a plan", "roadmap for this
  bugfix-plus-refactor", "what's the plan for adding X".
---
# Deep Plan

## Iron Law

Never begin implementation without explicit user confirmation of the finalized roadmap — after Phase 5 on Full Path, or after Step 3 on Quick Path. This applies regardless of which path was taken; neither path is exempt.

## Execution Path

Decide at entry:

| Criteria                           | Quick Path (Low Overhead)                    | Full Path (Deep Plan)                               |
| ----------------------------------- | --------------------------------------------- | ----------------------------------------------------- |
| **Logic Sequencing**         | Linear or independent steps (<=3)            | Multi-stage / branching dependencies (>3)           |
| **State / Invariant Impact** | Stateless, pure additions, or isolated logic | Mutates schemas, shared state, or system invariants |
| **Uncertainty & Risk**       | Zero unknowns; high confidence               | Unknowns, spikes required, or low confidence        |
| **Security Surface**         | No trust-boundary crossings                  | New or modified trust-boundaries / auth paths       |

**Auto-escalate** from Quick to Full if Phase 2 yields `MISFIT` or `CRITICAL` items, or total scope exceeds 15 tasks.

Quick Path: skip to [quick-path.md](references/quick-path.md) (3-step workflow, checkpoint at Step 1 scope approval and Step 3 roadmap confirmation).
Full Path: Phases 1-5 below (3 checkpoints).

## Core Principles (in priority order)

1. Solve the underlying problem, not the literal request
2. Preserve system invariants — explicitly define machine-checkable exit assertions
3. Identify failure modes early — plan sad paths before implementation
4. Protect trust boundaries — explicitly design security models
5. Keep work packages independently deliverable

## Progressive Write Rule (applies to all phases below)

**The roadmap file (`.deep-plan/<feature-plan>.md`) is written incrementally, not generated once at the end.**

Each phase writes its own sections directly to the living file the moment that analysis happens — while the detail is still fresh — instead of holding it in context to be reconstructed later:

- Phase 1 output → Context / Objective / Current State / Scope written immediately
- Phase 2 output → Failure Modes / Security Risks / System Invariants written immediately, per work stream, as each is analyzed
- Phase 3 output → Tasks tables / Exit Criteria written directly into the same file (this *is* the draft — not a separate document copied in later)
- Phase 4 output → Adversarial findings are applied as **edits** to the relevant existing sections, not a rewrite of the whole file
- Phase 5 → does not "generate" the roadmap. It **audits and completes** a file that is already ~90% written, filling only what phases 1-4 don't already own: Review Log, Completion Checklist, final consistency pass

Recalling all of Phases 1-4 from memory in one shot at Phase 5 is what causes roadmaps to come out compressed/summarized instead of as detailed as the research that produced them. If you find yourself about to write a full roadmap from scratch in Phase 5, stop — go back and check whether Phases 1-4 actually wrote to the file as they went.

## Unknown Resolution Rule (applies to all phases below)

**Silently assuming and proceeding is never one of the options.** When any phase hits something it doesn't actually know — a library's real behavior, an API contract, which of two approaches the user wants, whether an access/credential exists — resolve it through one of these, in priority order:

1. **Externally verifiable** (library behavior, API semantics, documented best practice) → use `web-search` if the binding is available, then write the verified answer. Don't write a plausible-sounding guess as if it were checked.
2. **Only the user can answer** (a preference, a business decision, access only they hold) → ask directly. Don't infer an answer to make the plan look more complete than it is.
3. **Not blocking the current phase, but needs resolving before implementation** → log it in the roadmap's Research Backlog (`R{n}`, with Priority) and continue. This is what the Research Backlog section is for — it isn't decorative, every unknown that isn't resolved through (1) or (2) goes here, not silently dropped.

A gap in the roadmap the user can point to and say "wait, is this actually true?" is a sign this rule got skipped somewhere upstream.

## Full Path Workflow

### Pre-flight

```bash
git status --porcelain
git log --oneline -1 @{upstream}...HEAD 2>/dev/null || echo "no upstream"
```

Warn if uncommitted changes or branch divergence. Recommend stash/commit/pull before planning.

### Phase 1: Understand Scope

Read scope source (`STATE.md`, `ROADMAP.md`, or equivalent). Extract: epic name/feature, status, dependencies, known gaps. No tracking doc → ask user.

Any ambiguity about scope, intent, or constraints at this stage — not just a missing tracking doc — gets asked about directly (see Unknown Resolution Rule). Phase 1 is the cheapest place in the whole workflow to catch a wrong assumption; guessing here so planning can "get moving" just relocates the cost to Phase 4 or Phase 5, after review/draft effort is already sunk into the wrong premise.

Write Context / Objective / Current State / Scope directly to `.deep-plan/<feature-plan>.md` (see Progressive Write Rule).

*Detailed guide: [scope-analysis.md](references/scope-analysis.md)*

### Phase 2: Enumerate Gaps

Analyze under three lenses (parallel if possible):

1. **Problem-Fit**: Does the literal request fully solve the underlying problem?
2. **Resilience**: Failure modes — timeouts, concurrency, duplicate calls, partial updates. Includes command-line machine verification assertions. *For resilience standards: [resilience-first-development.md](references/resilience-first-development.md)*
3. **Security**: Input abuse, missing permission checks, exposed secrets. Includes defense contracts.

Tag each gap: `FIT`, `MISFIT`, `CRITICAL`, or `BLOCKER` (blocks execution until resolved — external dependency, env config, access grant).

**Blocker Gate**: if any item is tagged `BLOCKER`, stop at the end of Phase 2 — do not proceed to Phase 3 until it's resolved, explicitly deferred, or the user halts planning. See the gate procedure in the detailed guide. This is a hard stop, not a note to revisit later.

Write findings directly into each work stream's Failure Modes / Security Risks sections in the living file as they're identified — not into a scratch list to be transcribed later.

*Detailed guide: [gap-analysis.md](references/gap-analysis.md)*

### Phase 3: Draft Roadmap

Construct the roadmap in place, in the same living file — Work Streams, tasks, dependencies, exit criteria. This is the file Phase 4 reviews and Phase 5 finalizes, not a separate draft.

*Template: [roadmap-template.md](templates/roadmap-template.md)*
*Guide: [roadmap-draft.md](references/roadmap-draft.md)*

### Cost Estimate Checkpoint (after Phase 3, before Phase 4)

Before spending review/execution budget, surface the rough shape of what's left. Count from the file already written in Phase 3:

- Number of work streams and total tasks
- Whether Phase 4 will run 1 pass (skip gate met) or 2 passes (CTO + Eng)
- If handoff is likely to be opted into later: roughly `N work streams × (1 implementer + 1 reviewer + possible fix cycles)` subagent dispatches

Present as one line, not a question that blocks progress — this is a heads-up, not a checkpoint requiring an answer:

> Draft has [N] work streams, [M] tasks. Adversarial review: [1/2] pass(es). If handed off to execution later, expect roughly [N–2N] subagent dispatches depending on review-loop retries. Continuing to review.

If the estimate looks unusually large for the item's actual scope (e.g., >8 work streams, or >30 tasks), that's a signal to pause and ask whether scope crept during Phase 2/3 — surface that explicitly rather than only stating the number.

While here, also check the Research Backlog for any `High` priority item still `Open` (see Unknown Resolution Rule). This is a soft gate, not a hard stop like the Blocker Gate — an open unknown doesn't mean execution is impossible, just that review is about to happen on a plan with an acknowledged gap. Surface it alongside the estimate:

> [N] High-priority open question(s) in the Research Backlog: [R-id — question]. Resolve before review, or proceed with it as an open risk?

If the user wants to proceed, that's fine — the point is making sure it was a choice, not an oversight.

### Phase 4: Adversarial Review

**Skip gate:** Phase 4 is skipped when Phase 2 yielded all `FIT`, 0 `CRITICAL`, and <=5 total gaps. Otherwise, run the review.

Run review using "outside voice" — different training perspectives catch blind spots.

Priority order:

1. CLI model in PATH, excluding whichever model drafted this plan (`claude`, `codex`, `gemini`, `ollama`, etc.)
2. Subagent with different model provider
3. Same-model subagent (must include explicit counter-bias checklist)

Apply findings as edits to the existing sections they concern. Do not rewrite the file.

*Detailed guide: [adversarial-review.md](references/adversarial-review.md)*

### Phase 5: Finalize & Quality Gate

Phase 5 does **not** generate the roadmap — see Progressive Write Rule. It does two things, in order, before the user ever sees the roadmap:

1. **Quality Gate**: Run the full checklist in [quality-gates.md](references/quality-gates.md) item-by-item against the living file. This is mandatory, not a passive reference — every unchecked item must be either fixed or explicitly logged as accepted debt. Record results in the roadmap's Completion Checklist section.
2. **Present**: Only after the gate passes, present the finalized roadmap to the user.

**STOP. Do not begin implementation without explicit user confirmation of the roadmap itself.**

This confirmation is a separate decision from whether to hand off to execution — see the note at the top of [execution-handoff.md](references/execution-handoff.md). Do not combine the two into one question, and do not infer execution opt-in from roadmap approval.

*Quality gates: [quality-gates.md](references/quality-gates.md)*

### Phase 6: Post-Execution Retro (after handoff completes)

Only runs if execution-handoff was opted into and Final Review (execution-handoff.md Section 6) has completed. Not a checkpoint — doesn't block or need confirmation, just closes the loop.

Compare the finalized roadmap against what actually happened: which tasks matched their Confidence Level and risk estimate, which F-ids/S-ids actually fired during implementation vs stayed theoretical, which exit criteria needed rework after the reviewer's first pass. Write findings to `.deep-plan/retro.md`.

This is what makes gap analysis and confidence estimates sharper on the *next* plan — skipping it means every roadmap starts from zero calibration.

*Detailed guide: [retro.md](references/retro.md)*

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
- Deferring all roadmap writing to Phase 5 → detail collapses into a compressed summary
- Treating roadmap approval and execution opt-in as the same question → unwanted auto-execution
- Discovering a BLOCKER only at Phase 5 → wasted draft/review effort on a plan that can't run
- Skipping Phase 6 → next plan's estimates stay uncalibrated against what actually happened

## Runtime Bindings

This skill requires these capabilities from the host runtime:

- **file-read**: Read source files, tracking docs, scope sources
- **file-write**: Write `.deep-plan/<feature-plan>.md` and references, incrementally across Phases 1-5
- **question**: Checkpoint confirmations with user (3 in Full Path, 1 in Quick Path)
- **subagent** (optional): Adversarial review with different model
- **web-search** (optional): External pattern research

If a required capability is unavailable, degrade gracefully:

- No question tool → render checkpoint as prose, wait for typed reply
- No subagent → use same-model with fresh context + counter-bias checklist
- No web-search → skip external pattern search, proceed with local analysis