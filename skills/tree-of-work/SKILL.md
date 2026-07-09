---
name: tree-of-work
description: >
  Track tasks, maintain context across sessions, and coordinate sub-agents
  using a hierarchical state file. Activate this skill immediately — even
  for casual phrases like "where was I", "lanjut dari mana", "what's next",
  "I'm lost", "lost track", or "resume" — without waiting for explicit
  task management language. Also triggers on: organize work, break down a
  complex task, track progress, manage multiple tasks, delegate to sub-agents,
  "task breakdown", or "worktree".
license: MIT
compatibility: Requires Python 3.8+ (for scripts/tree_of_work.py). Falls back to manual markdown editing if Python is unavailable.
metadata:
  author: ryou
  version: "2.0"
---

# Tree of Work

Hierarchical task tracking with context recovery and sub-agent coordination.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python scripts/tree_of_work.py init` | Create state directory (scans and auto-absorbs legacy roadmaps/todos) |
| `python scripts/tree_of_work.py status` | Print current state summary |
| `python scripts/tree_of_work.py validate` | Verify state file formatting, parent-child ID relationships, and check secrets |
| `python scripts/tree_of_work.py snapshot -m "msg"` | Save timestamped copy of state to history (run this when completing tasks or creating progress logs) |
| `python scripts/tree_of_work.py reset` | Reset state to default template |
| `--state-dir PATH` | Override state directory (any command) |
| `python scripts/tree_of_work.py status --json` | Machine-readable JSON output |

State lives in `.agent/tree-of-work/current-state.md` by default. Created only when complexity triggers auto-elevation — not at skill activation.

## Core Workflow

### Ephemeral First

When the skill activates, track state **in memory only**. No file on disk. The agent knows its ACTIVE task and Next Concrete Step internally.

**Do not run `init` unless one of these triggers fires:**
- Branching detected (bug, blocker, sub-task discovered)
- Task transition (ACTIVE → PARKED/BLOCKED)
- Handoff to sub-agent or back to user
- Session nearing end (to preserve context)

When a trigger fires, run `init` to create the state file, then record the current state.

### Session Start

1. Check if state file exists: `python scripts/tree_of_work.py status`
2. If it exists and you're resuming → read it, reconcile with `git status`, continue from `Next Concrete Step`
3. If it doesn't exist → scan for existing state docs. Read `references/ONBOARDING.md` **only if** you need to absorb legacy docs (ROADMAP.md, TODO.md, CLAUDE.md)
4. If resuming after a crash → read `references/RECOVERY.md`

## Reference File Loading Protocol

**Do NOT read all reference files.** Load only when the specific condition is met. This prevents context bloat — the agent's job is to write code, not read project management manuals.

| File | Load when... | Skip when... |
|------|-------------|--------------|
| `STATE_TEMPLATE.md` | You're about to run `init` and need the template | State file already exists |
| `ONBOARDING.md` | First session in a repo with no state file | State file exists or task is simple |
| `RECOVERY.md` | Resuming after crash/timeout/handoff | Fresh session, no prior state |
| `SUBAGENTS.md` | You're about to delegate to a sub-agent | Working solo |
| `CLASSIFICATION.md` | You can't decide if a task is PARKED, BLOCKED, or TODO | Status is obvious |
| `STATUS_MODEL.md` | You need transition rules not covered in SKILL.md | The status table above is sufficient |
| `ANTI_PATTERNS.md` | You're unsure if a behavior is problematic | You're following the Gotchas section |
| `TRAPS.md` | You caught yourself drifting and want to identify the trap | You're focused and on-track |

**Total lines you should ever load in one session: ~100-150, not 839.**

### During Work

- **One ACTIVE task at all times.** Never mark multiple tasks ACTIVE.
- Update `Latest Progress` and `Next Concrete Step` after each meaningful change.
- When discovering sub-work, add it to `BRANCHES` with a `Parent Task` reference.
- When switching tasks: PARK the current one first, then ACTIVATE the new one.

Progress:
- [ ] Step 1: Check for existing state or legacy docs
- [ ] Step 2: Work on the single ACTIVE task
- [ ] Step 3: Auto-elevate to file when complexity triggers (branching, transition, handoff)
- [ ] Step 4: Validate state (`validate`) before marking DONE

### Git Awareness

This skill tracks **logical state** (what you're working on), not Git workflow. How you commit, branch, and manage source control is your project's own convention. If you need guidance on avoiding branch clutter, read `references/STATUS_MODEL.md`.

## State File Structure

The state file is created on-demand (auto-elevation), not at skill activation. When you run `init`, read `references/STATE_TEMPLATE.md` for the template format.

**Key rules:**
- `NOW` section: exactly one ACTIVE task with `Task`, `Status`, `Primary Files`, `Latest Progress`, `Next Concrete Step`
- `PARKED / BLOCKED` section: paused tasks with `Reason` and `Resume Condition`
- `BRANCHES` section: discovered sub-work, each with a `Parent Task` reference
- `VALIDATION` section: optional test/lint/build status

## Status Model

| Status | Meaning |
|--------|---------|
| `ACTIVE` | Currently being worked on (max 1) |
| `PARKED` | Paused, unblocked, can resume anytime |
| `BLOCKED` | Waiting on external dependency |
| `TODO` | Backlog, not started |
| `DONE` | Completed and verified |

If you can't decide between PARKED and BLOCKED, read `references/CLASSIFICATION.md`.

## Sub-Agent Delegation

When delegating to sub-agents, isolate their state to prevent conflicts. Read `references/SUBAGENTS.md` before launching a sub-agent.

**TL;DR:**
1. Create isolated state dir: `.agent/tree-of-work/subagents/<id>/`
2. Init with `--state-dir .agent/tree-of-work/subagents/<id> init`
3. Write only the sub-task in the sub-agent's `NOW` section
4. After completion: validate, merge status back, archive sub-agent dir

## Gotchas

- **Never commit secrets in state files.** The script auto-redacts known patterns (GitHub tokens, Stripe keys, JWTs, AWS keys) and blocks high-entropy strings. If `validate` fails with a security alert, sanitize the value before proceeding.
- **Single ACTIVE task is enforced.** `validate` fails if 2+ tasks are ACTIVE. Mark tasks DONE or PARKED before switching.
- **Silent context drift.** Once a state file exists, always update it when modifying files. Successor agents rely on this file to know what happened.
- **Don't fight existing state systems.** If the repo has ROADMAP.md, TODO.md, or a project board, absorb from them — don't create a competing source of truth. Read `references/ONBOARDING.md` if you need to absorb legacy docs.
- **Don't create files for simple tasks.** Single-step requests ("fix this typo") should never trigger `init`. Keep tracking ephemeral until complexity warrants a file.
- **Python fallback.** If Python is unavailable, edit `current-state.md` directly following the template. The script is a helper, not a gatekeeper.

## Anti-Patterns

**Most common mistakes:**
1. Pasting raw API responses with secrets into state → sanitize first
2. Marking multiple tasks ACTIVE → one at a time, always
3. Modifying files without updating state → update `Latest Progress` as you go
4. Fixing "quick bugs" without parking the main task → Branch Promotion Protocol
5. Scope drift — fixing unrelated code → apply the Scope Gate Test

Read `references/ANTI_PATTERNS.md` for the full catalog, or `references/TRAPS.md` for context drift traps with concrete mitigations.