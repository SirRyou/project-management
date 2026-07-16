# Tree of Work: Why It Works This Way

Tree of Work enforces focus for AI agents through a simple but strict behavioral framework. This document explains the design decisions behind it.

**Related docs:** [Tutorial](tutorial-tree-of-work.md) | [How-To Guide](howto-tree-of-work.md) | [Reference](reference-tree-of-work.md)

## The Problem

AI agents lose focus. They drift to unrelated code, forget what they were working on, and produce scattered diffs that are hard to review. The root cause: agents have no built-in mechanism for task boundaries or context preservation.

Common failure modes:
- **Context splitting**: Agent works on two things simultaneously, mental model fragments
- **Silent drift**: Agent fixes typos in unrelated files, refactors modules outside scope
- **Lost progress**: Agent forgets what it was doing between sessions
- **Vague next steps**: Agent writes "continue working on app" instead of actionable instructions

## The Approach

Tree of Work solves this with three mechanisms:

### 1. One ACTIVE Task Rule

The Iron Law: **one ACTIVE task at all times.** This is the core constraint that prevents context splitting.

Why not allow multiple active tasks? Because:
- Context switching is expensive for LLMs (context window pressure)
- Mental models don't fork cleanly (unlike git branches)
- Reviewers can't tell which changes belong to which task

The rule is absolute: no exceptions for "quick fixes." If you need to fix something else, park the current task first.

### 2. Scope Gate

Before modifying a file outside your current task, run the Substitution Test:

> "If I remove this change, does the main task still fail?"

If no — the change is drift. Revert it, log it in the backlog, return to the main task.

Why this works:
- It's mechanical (no judgment required)
- It catches the "over-helpful" tendency of LLMs to fix nearby issues
- It keeps diffs clean and reviewable

### 3. Context Recovery

When resuming a session:
1. Check for prior state (progress notes, task list, memory files)
2. Reconcile with `git status` (do modified files match expectations?)
3. If state is stale, trust git (git is the source of truth)
4. Begin from the last `Next Concrete Step` (don't restart from scratch)

Why trust git over state files? Because:
- Git is always up-to-date (state files can go stale)
- Git shows what actually happened (state files show what was planned)
- Git is machine-readable (state files can be ambiguous)

## Trade-offs

### Ephemeral vs Persistent State

Tree of Work favors ephemeral tracking. State is kept in memory and only written to disk when complexity demands it (branching, task transition, sub-agent handoff, session end).

**What we gain:**
- No file format to maintain
- No directory structure to enforce
- Works on any platform

**What we lose:**
- No audit trail (unless you snapshot manually)
- No cross-session history (unless you write to memory files)
- No analytics (unless you add telemetry)

The bet: most agents don't need persistent state. The ones that do can add it.

### Behavioral vs Tool-Based

Tree of Work is a behavioral skill, not a tool. It tells agents how to think about focus — it doesn't impose specific file formats, directory structures, or CLI tools.

**What we gain:**
- Portable across any agent runtime (Claude Code, Cursor, Copilot, Codex, Gemini CLI)
- No installation dependencies
- Works with any persistence layer

**What we lose:**
- No built-in UI (agents must render state themselves)
- No automatic enforcement (agents must follow the rules)
- No analytics (unless you add telemetry)

The bet: behavioral constraints are more durable than tool constraints. Tools change; principles don't.

### Strict vs Flexible

Tree of Work is strict about the Iron Law (one ACTIVE task) but flexible about everything else. It adapts to the user's level of organization:

| User provides | Skill tracks |
|---------------|--------------|
| Detailed state file | Full tracking with all fields |
| Simple checklist | Completion status per item |
| Single task | Ephemeral tracking, no file created |
| No task at all | Discovery mode — scan for context, ask if needed |

Why not enforce a single format? Because:
- Users have different workflows
- Forcing a format creates friction
- The skill should adapt to the user, not the other way around

## Alternatives Considered

### Multiple Active Tasks

Some task trackers allow multiple active items. Tree of Work rejects this because:
- Context switching is expensive for LLMs
- Mental models don't fork cleanly
- Reviewers can't tell which changes belong to which task

### File-Based State

Some skills enforce a specific file format (e.g., `.tree-of-work/state.md`). Tree of Work rejects this because:
- File formats change
- Directory structures vary
- The skill should be portable

### Automatic Enforcement

Some tools automatically prevent scope drift (e.g., git hooks, linters). Tree of Work rejects this because:
- Tools are platform-specific
- Tools can be bypassed
- Behavioral constraints are more durable

## Design Principles

1. **One rule to rule them all**: The Iron Law (one ACTIVE task) is the core. Everything else is commentary.
2. **Ephemeral first**: Track state in memory. Only write to disk when complexity demands it.
3. **Adapt to the user**: Don't force a format. Match the user's level of organization.
4. **Trust git**: Git is the source of truth. State files are convenience, not truth.
5. **Be mechanical**: The Scope Gate Test is mechanical (no judgment required). This makes it reliable.
