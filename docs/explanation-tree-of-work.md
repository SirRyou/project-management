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

Tree of Work now uses a state file at `.agent/tree-of-work/current-state.md`, managed by a Python CLI (`skills/tree-of-work/scripts/tree_of_work.py`). The earlier design rejected file-based state for portability. The implementation reversed this because:

- **Ephemeral-only doesn't survive context compaction.** When the agent's context window fills, in-memory state is lost. A state file survives.
- **Cross-session recovery needs a durable artifact.** "Where was I?" requires reading a file, not hoping the agent remembers.
- **The CLI enforces the Iron Law mechanically.** `validate` fails if 2+ tasks are ACTIVE — something behavioral rules can't guarantee.

**What we gained:** Survives context compaction, mechanical enforcement, audit trail via snapshots.

**What we lost:** Portability across runtimes (the CLI is Python-specific), format is now fixed, directory structure is now enforced.

The behavioral-vs-tool trade-off shifted: the tool won because the agent's context window is the real constraint, not runtime portability.

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

## Limitations

### Branching Workflows

The skill works well for linear work: one task, do it, done. It breaks down when the user has 3+ concurrent threads — a common real-world scenario:

```
Main goal: onboarding feature
├── Frontend (DONE)
├── API backend (PARKED: waiting on DB)
├── DB fix (DONE → "checkpoint")
└── Security fix (spawned from API problem)
```

At the "checkpoint" moment, the state file is flat: one ACTIVE task, a list of PARKED items with no hierarchy. The user wants to save branch B's context and resume it later. The skill can't help because:

1. **No branch-scoped snapshots.** `snapshot` archives the whole state file, not a branch. You can't save "the API backend branch" independently.
2. **No branch navigation.** There's no `switch api-backend` command. The PARKED list is flat — you manually read each item and decide.
3. **No branch relationships.** The state file doesn't record that "API backend" was parked because "DB fix" was blocking it. When DB is done, the user has to remember which parked task to activate.
4. **Resume requires re-scanning.** When loading a new session with 5 parked tasks, the skill says "begin from the last Next Concrete Step" — but which task? The skill doesn't pick for you.

### What Would Fix This

A branching workflow needs:
- **Branch-scoped snapshots:** `snapshot --branch api-backend` saves that branch's context (current files, progress, next step, why parked) to a named location.
- **Branch navigation:** `switch api-backend` saves current branch, loads target, updates state file.
- **Branch tree visualization:** `status --tree` shows the hierarchy.
- **Resume from checkpoint:** `resume api-backend` loads just that branch without scanning the whole codebase.

This is a significant feature addition. The current skill is designed for linear work; branching would require a tool layer on top of the behavioral framework.

### The Ephemeral Tension

The skill says "ephemeral first" but also needs persistent state to survive context compaction. These contradict. The implementation resolved this by using a state file — but the explanation doc still says "favors ephemeral tracking." The reality: the state file is the primary artifact, and ephemeral tracking is the fallback for simple cases.
