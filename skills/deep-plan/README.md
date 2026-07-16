# Deep Plan

Planning for features spanning multiple files, work streams, or architectural decisions. Produces phased, adversarial-reviewed roadmaps.

## What It Does

Deep Plan guides agents through a structured planning workflow that catches blind spots before implementation. It enforces three things no agent does naturally:

1. **Problem-fit analysis** — are you solving the right problem, or just implementing the literal request?
2. **Resilience and security lenses** — what breaks when things fail? What gets abused?
3. **Adversarial review** — a different model catches what you missed.

## When to Use

- More than 3 files affected
- Multiple independent work streams
- Design decisions or trust-boundary updates needed
- Phased delivery beneficial

## When NOT to Use

- Trivial changes, single-file edits, simple bug fixes. Implement directly.

## How It Works

### Execution Path

| Criteria | Quick Path | Full Path |
|----------|-----------|-----------|
| Files affected | <=3 | >3 |
| Work streams | <=3 | >3 |
| CRITICAL security items | 0 | any |

Quick Path: 3-step workflow, 1 checkpoint.
Full Path: 5 phases, 3 checkpoints.

Auto-escalate from Quick to Full if Phase 2 yields `MISFIT` or `CRITICAL` items, or total scope exceeds 15 tasks.

### Phases (Full Path)

1. **Understand Scope** — read tracking docs, extract requirements, lock scope with user
2. **Enumerate Gaps** — analyze under three lenses (Problem-Fit, Resilience, Security) in parallel
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
