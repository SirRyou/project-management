# Deep Plan Reference

Deep Plan is a behavioral skill for AI agents that guides structured planning for complex features. It enforces problem-fit analysis, resilience and security lenses, and adversarial review before implementation.

**Related docs:** [Tutorial](tutorial-deep-plan.md) | [How-To Guide](howto-deep-plan.md) | [Explanation](explanation-deep-plan.md)

## Core Concepts

### The Iron Law

**Never begin implementation without explicit user confirmation after Phase 5.**

### Execution Path

Decide at entry (<!-- ponytail: simplified to use logical complexity/uncertainty instead of fragile file-count metric -->):

| Criteria | Quick Path (Low Overhead) | Full Path (Deep Plan) |
|----------|-----------|-----------|
| **Logic Sequencing** | Linear or independent steps (<=3) | Multi-stage / branching dependencies (>3) |
| **State / Invariant Impact** | Stateless, pure additions, or isolated logic | Mutates schemas, shared state, or system invariants |
| **Uncertainty & Risk** | Zero unknowns; high confidence | Unknowns, spikes required, or low confidence |
| **Security Surface** | No trust-boundary crossings | New or modified trust-boundaries / auth paths |

**Auto-escalate** from Quick to Full if Phase 2 yields `MISFIT` or `CRITICAL` items, or total scope exceeds 15 tasks.

Quick Path: 3-step workflow, 1 checkpoint.
Full Path: Phases 1-5 below (3 checkpoints).

### Core Principles (in priority order)

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

*Detailed guide: [scope-analysis.md](../skills/deep-plan/references/scope-analysis.md)*

### Phase 2: Enumerate Gaps

Analyze under three lenses (parallel if possible):

1. **Problem-Fit**: Does the literal request fully solve the underlying problem?
2. **Resilience**: Failure modes — timeouts, concurrency, duplicate calls, partial updates. Includes command-line machine verification assertions.
3. **Security**: Input abuse, missing permission checks, exposed secrets. Includes defense contracts.

Tag each gap: `FIT`, `MISFIT`, `CRITICAL`, or `BLOCKER` (blocks execution until resolved — external dependency, env config, access grant).

*Detailed guide: [gap-analysis.md](../skills/deep-plan/references/gap-analysis.md)*

### Phase 3: Draft Roadmap

Construct tentative roadmap. Work streams with tasks, dependencies, exit criteria.

*Template: [roadmap-template.md](../skills/deep-plan/templates/roadmap-template.md)*
*Guide: [roadmap-draft.md](../skills/deep-plan/references/roadmap-draft.md)*

### Phase 4: Adversarial Review

Run review using "outside voice" — different training perspectives catch blind spots.

Priority order:
1. CLI model in PATH (`claude`, `codex`, `ollama`, etc.)
2. Subagent with different model provider
3. Same-model subagent (must include explicit counter-bias checklist)

Skip Phase 4 if Phase 2 yielded all `FIT`, 0 `CRITICAL`, and <=5 total gaps.

*Detailed guide: [adversarial-review.md](../skills/deep-plan/references/adversarial-review.md)*

### Phase 5: Finalize Roadmap

Generate final roadmap. **STOP. Do not begin implementation without explicit user confirmation.**

*Quality gates: [quality-gates.md](../skills/deep-plan/references/quality-gates.md)*

### Execution Handoff (Phase 5 → Implementation)

After user confirms roadmap, hand off to execution via subagent-driven workflow:

1. **Opt-in** — confirm with user: hand off or stop
2. **Isolation** — fresh session, reads only roadmap file
3. **Pre-flight scan** — check for plan contradictions before execution
4. **Per-WS dispatch loop** (in dependency order):
   - Extract WS brief → `.deep-plan/handoff/WS{n}-brief.md`
   - Dispatch implementer subagent ([implementer-prompt.md](../skills/deep-plan/references/implementer-prompt.md))
   - Generate diff → `.deep-plan/handoff/WS{n}-diff.md`
   - Dispatch reviewer subagent ([reviewer-prompt.md](../skills/deep-plan/references/reviewer-prompt.md))
   - Review loop: fix → re-review until approved
   - Update progress ledger → `.deep-plan/handoff/progress.md`
5. **Final review** — cross-WS integration check after all WS complete

Artifacts live under `.deep-plan/handoff/`. Progress ledger survives compaction.

*Detailed guide: [execution-handoff.md](../skills/deep-plan/references/execution-handoff.md)*

### Non-linear & Mid-Execution Flow

- Phase 4 review finds scope issues → jump back to Phase 2
- Phase 2 yields all FIT, 0 CRITICAL, <=5 gaps → skip Phase 4
- **Mid-Execution Scope Drift / Blocker**: If execution hits an invariant violation or unblocked scope growth during coding, activate the [reentry-protocol.md](../skills/deep-plan/references/reentry-protocol.md) for targeted delta planning.

## UI Projects

If roadmap touches visual components, run UI review checklist after Phase 5.
*Guide: [ui-review.md](../skills/deep-plan/references/ui-review.md)*

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

## Gap Analysis Details

### Three-Lens Framework

#### Lens 1: Problem-Fit Check

```markdown
### Problem-Fit: [Item Name]
- Literal ask: [what was requested]
- Underlying goal: [what actually needs to be true for the user]
- Gap: [does the literal ask fully close that gap? if not, what's missing?]
- Verdict: [FIT | PARTIAL_FIT | MISFIT] — missing: [description or N/A]
- Invariant Impact: [Preserved | Threatened: state invariant broken]
```

#### Lens 2: Failure Mode Table

```markdown
### [Item Name] — Failure Modes

| # | Failure Mode | Trigger | Impact | Machine Exit Verification |
|---|-------------|---------|--------|---------------------------|
| F1 | [what fails] | [what causes it] | [what breaks] | [test case or command to prove fix] |
```

#### Lens 3: Security Risk Table

```markdown
### [Item Name] — Security Risks

| # | Risk | Trust Boundary Crossed | Adversarial Trigger | Impact | Defense Contract |
|---|------|------------------------|----------------------|--------|------------------|
| S1 | [what could be abused/leaked] | [where] | [what a malicious actor would send/do] | [blast radius] | [exact check/guard condition] |
```

## Adversarial Review Details

### CTO Review (Pass 1)

Challenge on:
1. PROBLEM-FIT: Does plan solve underlying problem, or just literal request?
2. SCOPE: Boundary right? What's missing? What's bloat?
3. ASSUMPTIONS: List every implicit assumption. Which wrong or unvalidated?
4. SEQUENCING: Right first thing? Real critical path?
5. OVER-ENGINEERING: What's solving hypothetical problem, not real one?

### Eng Review (Pass 2)

Challenge on:
1. HIDDEN DEPENDENCIES: Dependencies between tasks author missed?
2. SDK/LIBRARY RISKS: Third-party behaviors invalidating approach?
3. OVER-CONFIDENCE: Tasks marked High/Medium confidence but risky?
4. MISSING TASKS: Implementation work implied but not listed?
5. TESTING GAPS: Exit criteria can't actually be verified?
6. RESOURCE LEAKS: Async lifecycle, event listener, resource issues?
7. SECURITY: Missing input validation, permission checks, secret handling, trust boundary leaks?

### Combined Pass (Quick Path / No Other Model)

Counter-Bias Checklist:
- Challenge every assumption marked "assumed obvious" or "standard pattern".
- Verify that every work package has a machine-executable verification step (tests/lint/cli).
- Assume every network/database call can hang for 30s or return malformed JSON.
- Assume inputs are crafted by an adversary seeking auth bypass or secret extraction.
