# Deep Plan

Planning for features spanning multiple files, work streams, or architectural decisions. Produces phased, adversarial-reviewed roadmaps.

## What It Does

Deep Plan guides agents through a structured planning workflow that catches blind spots before implementation. It enforces three things no agent does naturally:

1. **Problem-fit analysis** — are you solving the right problem, or just implementing the literal request?
2. **Resilience and security lenses** — what breaks when things fail? What gets abused?
3. **Adversarial review** — a different model catches what you missed.

## When to Use

- Multi-stage logic with sequential dependencies
- Changes impacting persistent state, database schemas, or system invariants
- Design decisions, trust-boundary updates, or security-critical paths
- High-uncertainty features benefiting from structured gap analysis and adversarial review

## When NOT to Use

- Trivial changes, single-file edits, simple bug fixes. Implement directly.

## How It Works

### Execution Path (<!-- ponytail: simplified to use logical complexity/uncertainty instead of fragile file-count metric -->)

| Criteria | Quick Path (Low Overhead) | Full Path (Deep Plan) |
|----------|-----------|-----------|
| **Logic Sequencing** | Linear or independent steps (<=3) | Multi-stage / branching dependencies (>3) |
| **State / Invariant Impact** | Stateless, pure additions, or isolated logic | Mutates schemas, shared state, or system invariants |
| **Uncertainty & Risk** | Zero unknowns; high confidence | Unknowns, spikes required, or low confidence |
| **Security Surface** | No trust-boundary crossings | New or modified trust-boundaries / auth paths |

Quick Path: 3-step workflow, 1 checkpoint.
Full Path: 5 phases, 3 checkpoints.

Auto-escalate from Quick to Full if Phase 2 yields `MISFIT` or `CRITICAL` items, or total scope exceeds 15 tasks.

### Phases (Full Path)

1. **Understand Scope** — read tracking docs, extract requirements, lock scope with user
2. **Enumerate Gaps** — analyze under three lenses (Problem-Fit, Resilience, Security) in parallel. Tag gaps: `FIT`, `MISFIT`, `CRITICAL`, `BLOCKER`.
3. **Draft Roadmap** — work streams, tasks, dependencies, exit criteria
4. **Adversarial Review** — "outside voice" using different model provider (CTO + Eng passes)
5. **Finalize Roadmap** — quality gates, user confirmation required before any implementation

### Non-linear flow

- Phase 4 review finds scope issues → jump back to Phase 2
- Phase 2 yields all FIT, 0 CRITICAL, <=5 gaps → skip Phase 4

## Core Principles

1. Solve the underlying problem, not the literal request
2. Preserve system invariants
3. Identify failure modes early
4. Protect trust boundaries
5. Keep work packages independently deliverable

## Architecture

```
deep-plan/
├── SKILL.md                    # Behavioral spec (the skill)
├── README.md                   # This file
├── references/
│   ├── scope-analysis.md       # Phase 1 guide
│   ├── gap-analysis.md         # Phase 2 guide + 3-lens framework
│   ├── roadmap-draft.md        # Phase 3 template
│   ├── adversarial-review.md   # Phase 4 review protocol
│   ├── quality-gates.md        # Phase 5 verification
│   ├── execution-handoff.md    # Post-plan handoff to implementation
│   ├── implementer-prompt.md   # WS-scoped implementer subagent prompt
│   ├── reviewer-prompt.md      # WS-scoped reviewer subagent prompt
│   ├── ui-review.md            # Conditional UI/UX review
│   ├── quick-path.md           # 3-step workflow for simple epics
│   └── resilience-first-development.md  # Engineering standards reference
│       └── resilience-development-book/ # 18 standard sub-files
└── templates/
    └── roadmap-template.md     # Final roadmap format
```

## Runtime Requirements

| Capability | Required | Purpose |
|------------|----------|---------|
| file-read | Yes | Read source files, tracking docs |
| file-write | Yes | Write plan files |
| question | Yes | Checkpoint confirmations (3 in Full Path, 1 in Quick Path) |
| subagent | No | Adversarial review with different model |
| web-search | No | External pattern research |

Graceful degradation: if a capability is missing, the skill adapts (prose checkpoints, same-model review, skip external search).

## Triggers

- "plan this feature"
- "design an epic"
- "architectural planning"
- "break down this work"
- "create a roadmap"

## License

MIT
