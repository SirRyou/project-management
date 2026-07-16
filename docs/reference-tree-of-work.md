# Tree of Work Reference

Tree of Work is a behavioral skill for AI agents that enforces focus and enables context recovery. It keeps one active task at a time, prevents drift, and preserves progress across sessions.

**Related docs:** [Tutorial](tutorial-tree-of-work.md) | [How-To Guide](howto-tree-of-work.md) | [Explanation](explanation-tree-of-work.md)

## Core Concepts

### Status Model

Every task has exactly one status:

| Status | Meaning | Rule |
|--------|---------|------|
| `ACTIVE` | Being worked on now | Max 1. Always. |
| `PARKED` | Paused by choice | You control the resume. |
| `BLOCKED` | Waiting on external dependency | Someone else has the ball. |
| `TODO` | Backlog | Not started. |
| `DONE` | Completed and verified | Terminal. |

### The Iron Law

**One ACTIVE task at all times. Never mark multiple tasks ACTIVE.**

This is the single most important rule. Everything else is commentary.

### Core Rules

1. **Ephemeral first.** Track state in memory. Only write to disk when complexity demands it (branching, task transition, sub-agent handoff, session end).
2. **Update as you work.** After each meaningful change, update your current progress and next step. Don't batch updates at the end.
3. **Park before switching.** When switching tasks: mark current as PARKED with reason, then activate new one.
4. **Scope gate every change.** Before modifying a file outside your current task: "If I remove this change, does the main task still fail?" If no — it's drift. Revert it, log it, move on.
5. **Validate before DONE.** Run tests, check for regressions, update progress notes. A task isn't done until it's verified.

## Status Classification

### PARKED vs BLOCKED

The question: **Do you control the resume?**

- Yes → PARKED. You chose to stop. You can continue when ready.
- No → BLOCKED. External dependency. Someone else must act first.

A task that depends on another task *you are also doing* is PARKED, not BLOCKED. You control both.

### DONE Criteria

A task is NOT DONE until all are true:

1. Code change is made
2. Tests pass (if the project has tests)
3. No regressions in existing functionality
4. Progress notes reflect what was actually done

If the user says "this is done, move on" without testing, mark it `DONE (untested — user confirmed)` and log the gap.

## Context Recovery

When resuming a session:

1. Check for prior state — progress notes, task list, or memory files
2. Reconcile with `git status` — do modified files match what you expected?
3. If state is stale (git history diverged), trust git. Update state to reflect reality.
4. Begin from the last `Next Concrete Step`. Don't restart from scratch.

When ending a session:

1. Record current progress and next concrete step
2. If work is in progress, PARK the active task with reason and resume condition

## Sub-Agent Delegation

When delegating to a sub-agent:

1. Pass only the sub-task scope — not your full task list
2. Sub-agent tracks its own state independently
3. After completion: validate output, merge status back, clean up

Don't let sub-agents write to your state. Isolation prevents corruption.

## Focus Traps

### Double Active

Two tasks marked ACTIVE simultaneously. The agent jumps between them without transitions.

**Fix:** One ACTIVE always. PARK the current one before touching anything else. No exceptions for "quick fixes."

### Silent Branching

Making broad code changes outside current scope without recording them. Fixing typos in other files, refactoring unrelated modules, reorganizing imports.

**Fix:** The Scope Gate Test. "If I remove this change, does the main task still fail?" If no — revert, log in backlog, return to main task.

### Vague Next Step

`Next Concrete Step` says "continue working on app" or "debug the failing connection."

**Fix:** Next step must answer: what file, what line, what change. "Add exponential backoff to WebSocket reconnect in prices.ts:42" — not "continue implementing websocket."

### God Object Mutation

Agent starts refactoring multiple unrelated modules while supposed to be working on a localized sub-task. The diff explodes, context window fills.

**Fix:** Before modifying any file outside original scope, run the Substitution Test. If the primary task works without the change, it's drift.

## Clarification Protocol

**Ask the user only when:**

1. True ambiguity — multiple valid interpretations, wrong choice wastes significant work
2. Conflicting signals — state says one thing, git says another, user says a third
3. Destructive action — about to do something hard to reverse
4. No task discoverable — no state, no history, vague prompt

**Don't ask when:**

- The answer is inferable from context (git status shows modified files → continue that work)
- The choice is low-stakes (picking between two backlog items → just pick one, document why)
- You can make a reasonable default (no state file → scan for context, proceed)

**How to ask:** Constrained choice with a default, not open-ended.

Bad: "What would you like me to do?"
Good: "I found two items in progress: Auth and Billing. I'll default to Auth unless you specify."

## References

| File | Load when |
|------|-----------|
| [CLASSIFICATION.md](../skills/tree-of-work/references/CLASSIFICATION.md) | Unsure if a task is PARKED, BLOCKED, or TODO — or facing an edge case |
| [TRAPS.md](../skills/tree-of-work/references/TRAPS.md) | You caught yourself drifting and want to identify the trap |
| [ANTI_PATTERNS.md](../skills/tree-of-work/references/ANTI_PATTERNS.md) | Unsure if a behavior is problematic |
| [SUBAGENTS.md](../skills/tree-of-work/references/SUBAGENTS.md) | About to delegate to a sub-agent |

## Scope Boundary

This skill **enforces focus**. It does not:

- Generate implementation plans (use a planning skill)
- Decide what the user should work on (that's the user's call)
- Create roadmaps or project timelines
- Replace your platform's built-in task tracking

It tells the agent **how to think**, not where to write files. Delegate persistence to your platform's native tools.

## Completion Status

- **DONE** — task completed, verified, no regressions
- **DONE_WITH_CONCERNS** — completed but with known gaps (documented)
- **BLOCKED** — cannot proceed, external dependency named
