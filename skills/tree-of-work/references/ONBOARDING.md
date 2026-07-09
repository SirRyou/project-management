# Onboarding & Workspace Discovery

How to initialize Tree of Work when entering a repository that may already have its own state documents.

---

## Core Principle: Macro vs Micro State

| | Macro State | Micro State |
|---|---|---|
| **Examples** | `CLAUDE.md`, `ROADMAP.md`, `TODO.md`, GitHub Projects | `.agent/tree-of-work/current-state.md` |
| **Owner** | Human team / project-level | Agent (session-level) |
| **Focus** | "What are the big goals and architecture?" | "Which line am I working on right now?" |
| **Lifecycle** | Permanent, rarely changes radically | Dynamic, changes every session/turn |

**Rule:** Never delete or overwrite the user's macro documents. Use them as a compass to populate the Tree of Work's task queue.

---

## The Onboarding State Machine

When the skill activates, follow this sequence before creating any files:

```
[START: Skill Activated]
         │
         ▼
Is the request single-step/stateless? ───(Yes)───> [Do NOT initialize. Handle directly.]
         │                                        (e.g., "fix this typo", "what's in this file?")
       (No)
         ▼
Scan for Existing State Documents
(CLAUDE.md, ROADMAP.md, TODO.md, STATUS.md, git log)
         │
   ┌─────┴─────┐
[Found]    [Not Found]
   │            │
   ▼            ▼
Parse &     Use git branch
Absorb      name as default
   │        task context
   └────┬────┘
        ▼
Conflicting ACTIVE goals? ───(Yes)───> [HALT: Ask user to pick one focus]
        │
      (No)
        ▼
[Ephemeral Tracking — no file created yet]
```

---

## Ephemeral Mode (Default)

When the skill activates, the agent tracks task state **in memory only**. No file is written to disk. The agent maintains:

- Current ACTIVE task (one)
- Discovered sub-tasks (if any)
- Next Concrete Step

This is sufficient for single-focus work with no branching.

### Auto-Elevation Triggers

The agent **must** create `.agent/tree-of-work/current-state.md` (run `init`) when any of these occur:

1. **Branching detected** — a bug, blocker, or sub-task is discovered
2. **Task transition** — switching from ACTIVE to PARKED or BLOCKED
3. **Handoff** — delegating to a sub-agent or returning control to the user
4. **Session nearing end** — to preserve context for the next session

Until one of these triggers fires, keep tracking ephemeral.

---

## Pattern Recognition for Auto-Absorption

When `init` runs and legacy documents exist, scan them with these patterns and absorb into the appropriate state sections:

### Sources to Scan

| File | Pattern | Target Section |
|------|---------|----------------|
| `TODO.md` / `todo.txt` | Lines starting with `- [ ]` or `TODO:` | `PARKED / BLOCKED` or `TODO` |
| `CLAUDE.md` | Sections named `## Current Focus` or `## Next Steps` | `NOW` (if single item) or `PARKED` (if multiple) |
| `ROADMAP.md` / `STATUS.md` | Lines with `IN_PROGRESS`, `ACTIVE`, `In Progress` | `NOW` (if one) or ask user (if conflicting) |
| Git history | `git log -1 --pretty=%B` | Context for `Latest Progress` |

### Absorption Rules

1. **One ACTIVE at most.** If multiple items are marked IN_PROGRESS across sources, absorb the first one as ACTIVE and the rest as PARKED — unless they directly conflict (then ask the user).
2. **Never overwrite macro documents.** Absorption means *reading* and *mirroring*, not modifying the user's files.
3. **Prefix absorbed tasks** with the source: `[from: ROADMAP.md] Implement billing module`.

---

## When to Ask for Clarification

The agent should **not** ask questions at session start unless one of these is true:

1. **Ambiguous prompt + no state context.** The user said "fix it" and there's no TODO, no ROADMAP, no git history to infer what "it" is.

2. **Conflicting ACTIVE goals.** The macro document lists 3 features all marked IN_PROGRESS, violating the single-active-task principle. Ask which one to focus on.

3. **No detectable task.** The repo has no state docs, the git history is empty, and the user's prompt doesn't specify a task.

### Example Clarification

> "I found ROADMAP.md listing both Billing and Auth as IN_PROGRESS. Per Tree of Work, I need one focus. Which should I set as ACTIVE right now?"

Don't ask about file format preferences, state directory locations, or whether to use the skill — just do it.
