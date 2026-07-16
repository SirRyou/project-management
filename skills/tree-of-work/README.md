# Tree of Work

Focus enforcement and context recovery for AI agents.

## What It Does

Keeps agents on track through three mechanisms:

1. **One ACTIVE task rule** — prevents context splitting and drift
2. **Context recovery** — preserves progress across sessions and handoffs
3. **Scope gate** — catches silent scope drift before it compounds

## When to Use

- Multi-step work that spans sessions
- Agent keeps losing focus or drifting to unrelated code
- Handing off work between agents or sessions
- Any phrase like "where was I", "what's next", "resume"

## When NOT to Use

- Single-step requests ("fix this typo")
- Work that doesn't span sessions
- When your platform already handles focus tracking natively

## Core Rules

1. One ACTIVE task at all times
2. Park before switching tasks
3. Scope gate every change outside your current task
4. Update progress as you work, not at the end
5. Validate before marking DONE

## Status Model

| Status | Meaning |
|--------|---------|
| `ACTIVE` | Being worked on (max 1) |
| `PARKED` | Paused by choice |
| `BLOCKED` | Waiting on external dependency |
| `TODO` | Backlog |
| `DONE` | Completed and verified |

## References

| File | Purpose |
|------|---------|
| `references/CLASSIFICATION.md` | Decision tree for status classification, edge cases |
| `references/TRAPS.md` | Common focus traps with concrete mitigations |
| `references/ANTI_PATTERNS.md` | Behaviors that undermine focus and git stability |
| `references/SUBAGENTS.md` | Delegation protocol for sub-agent coordination |

## Design Philosophy

This is a **behavioral skill**, not a tool. It tells agents how to think about focus and progress — it doesn't impose a specific file format, directory structure, or CLI tool.

Delegate persistence to your platform's native tools (task tracker, memory files, checkpoints). The skill provides the rules; the platform provides the storage.

## Architecture

```
tree-of-work/
├── SKILL.md                    # Behavioral spec (the skill)
├── README.md                   # This file
├── scripts/
│   └── tree_of_work.py         # Python CLI tool
└── references/
    ├── CLASSIFICATION.md       # Status decision tree + edge cases
    ├── TRAPS.md                # Focus drift traps + mitigations
    ├── ANTI_PATTERNS.md        # Anti-patterns catalog
    └── SUBAGENTS.md            # Delegation protocol
```

## License

MIT
