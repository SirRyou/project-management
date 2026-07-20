# Deep Plan: Why It Works This Way

Deep Plan enforces structured planning for complex features through a phased workflow with adversarial review. This document explains the design decisions behind it.

**Related docs:** [Tutorial](tutorial-deep-plan.md) | [How-To Guide](howto-deep-plan.md) | [Reference](reference-deep-plan.md)

## The Problem

AI agents plan poorly. They implement the literal request without understanding the underlying problem, miss failure modes, and skip security analysis. The result: features that work in the happy path but break under pressure.

Common failure modes:
- **Literal implementation**: Agent implements exactly what was asked, not what was needed
- **Blind spots**: Agent misses failure modes, security risks, and edge cases
- **Single-path design**: Agent designs for success, not for failure
- **Scope creep**: Agent adds "nice to have" features that bloat the roadmap

## The Approach

Deep Plan solves this with three mechanisms:

### 1. Problem-Fit Analysis

Before planning, ask: "Does the literal request fully solve the underlying problem?"

Why this matters:
- Users often describe symptoms, not root causes
- "Add a retry button" might mean "the request times out silently"
- Implementing the literal request can miss the point entirely

The Problem-Fit lens forces the agent to:
1. State the literal ask
2. Identify the underlying goal
3. Check if the ask closes the gap
4. Flag any MISFIT or PARTIAL_FIT

### 2. Three-Lens Gap Analysis

For each item in scope, run three independent analyses:

1. **Problem-Fit**: Does this solve the right problem?
2. **Resilience**: What fails when things go wrong?
3. **Security**: What gets abused?

Why three lenses?
- Each catches different blind spots
- Running them in parallel prevents tunnel vision
- Tagging gaps (FIT, MISFIT, CRITICAL, BLOCKER) enables prioritization

### 3. Adversarial Review

After drafting the plan, run it by a different model (or same model with fresh context) using the "outside voice" principle.

Why adversarial review?
- Different training catches different blind spots
- A skeptical CTO finds scope issues
- A senior engineer finds technical risks
- The counter-bias checklist prevents self-confirmation

## Trade-offs

### Quick Path vs Full Path

Deep Plan offers two execution paths (<!-- ponytail: simplified to use logical complexity/uncertainty instead of fragile file-count metric -->):

| Criteria | Quick Path (Low Overhead) | Full Path (Deep Plan) |
|----------|-----------|-----------|
| **Logic Sequencing** | Linear or independent steps (<=3) | Multi-stage / branching dependencies (>3) |
| **State / Invariant Impact** | Stateless, pure additions, or isolated logic | Mutates schemas, shared state, or system invariants |
| **Uncertainty & Risk** | Zero unknowns; high confidence | Unknowns, spikes required, or low confidence |
| **Security Surface** | No trust-boundary crossings | New or modified trust-boundaries / auth paths |

**What we gain with Quick Path:**
- Faster for simple changes
- Less overhead for small features
- 1 checkpoint instead of 3

**What we lose with Quick Path:**
- Less thorough analysis
- May miss edge cases
- No adversarial review (unless auto-escalated)

The bet: most features are simple. Quick Path handles them without overhead.

### Auto-Escalation

If Quick Path yields `MISFIT` or `CRITICAL` items, or total scope exceeds 15 tasks, auto-escalate to Full Path.

Why auto-escalate?
- Prevents under-planning for complex features
- Catches scope issues early
- Ensures adversarial review for risky changes

### Skip Phase 4

If Phase 2 yields all `FIT`, 0 `CRITICAL`, and <=5 total gaps, skip Phase 4 (adversarial review).

Why skip?
- Low-risk changes don't need adversarial review
- Saves time and tokens
- The three-lens analysis already caught issues

### Non-Linear Flow

Deep Plan supports non-linear flow:
- Phase 4 review finds scope issues → jump back to Phase 2
- Phase 2 yields all FIT, 0 CRITICAL, <=5 gaps → skip Phase 4

Why non-linear?
- Planning is iterative, not linear
- New information changes the plan
- The skill should adapt to reality

## Alternatives Considered

### Single-Pass Planning

Some planners do a single pass: gather requirements, draft plan, done. Deep Plan rejects this because:
- Single-pass misses blind spots
- No adversarial review
- No problem-fit analysis

### Tool-Based Planning

Some tools enforce planning formats (e.g., Jira, Linear). Deep Plan rejects this because:
- Tools are platform-specific
- Formats change
- The skill should be portable

### Fixed Workflow

Some planners enforce a fixed workflow (Phase 1 → Phase 2 → ... → Phase 5). Deep Plan rejects this because:
- Planning is iterative
- New information changes the plan
- The skill should adapt to reality

## Design Principles

1. **Solve the right problem**: Problem-Fit analysis ensures the plan addresses the underlying goal, not just the literal request.
2. **Plan for failure**: Resilience lens catches failure modes before implementation.
3. **Plan for abuse**: Security lens catches adversarial inputs before implementation.
4. **Outside voice**: Adversarial review catches blind spots that same-model analysis misses.
5. **User confirmation**: Never implement without explicit user approval after Phase 5.

## The "Outside Voice" Principle

Deep Plan uses different model providers for adversarial review. Why?

Different models have different training data, different biases, and different blind spots. A model that drafted a plan may not catch its own assumptions. A different model is more likely to challenge them.

Priority order:
1. CLI model in PATH (`claude`, `codex`, `ollama`, etc.)
2. Subagent with different model provider
3. Same-model subagent (must include explicit counter-bias checklist)

The counter-bias checklist for same-model review:
- Challenge every assumption marked "assumed obvious" or "standard pattern"
- Verify that every work package has a machine-executable verification step
- Assume every network/database call can hang for 30s or return malformed JSON
- Assume inputs are crafted by an adversary seeking auth bypass or secret extraction

## Quality Gates

Before finalizing the roadmap, verify:

- [ ] Every task has a machine-executable exit criterion
- [ ] Every CRITICAL gap has a corresponding task
- [ ] Every MISFIT has been resolved or accepted as debt
- [ ] Every work stream is independently deliverable
- [ ] The plan addresses the underlying problem, not just the literal request

If any gate fails, the plan is not ready.
