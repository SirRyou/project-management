# Tree of Work

Hierarchical task tracking with context recovery and sub-agent coordination for AI coding agents.

## What Is This Skill?

Tree of Work is a task management skill that helps AI agents maintain context across sessions, track progress on complex tasks, and coordinate work across multiple sub-agents. It uses a hierarchical state file to represent the current work state, including active tasks, parked items, and discovered sub-work.

The skill is designed to be **ephemeral-first**: it tracks state in memory until complexity triggers (like task transitions or sub-agent handoffs) force materialization to disk. This minimizes overhead for simple tasks while preserving context for complex ones.

## What Problem Does It Solve?

AI agents face several challenges when working on multi-step tasks:

### Context Loss

When a session ends or crashes, agents lose track of what they were doing. Tree of Work persists state to disk, allowing seamless recovery across sessions.

```text
# Without Tree of Work
Session 1: "I was working on the auth system..."
Session 2: "Wait, what was I doing?"

# With Tree of Work
Session 1: State saved to .agent/tree-of-work/current-state.md
Session 2: python scripts/tree_of_work.py status → "Resume from [TASK-03]"
```

### Task Sprawl

Without enforcement, agents mark multiple tasks as "in progress" and lose focus. Tree of Work enforces a single ACTIVE task, forcing explicit parking before switching.

### Sub-Agent Conflicts

When delegating to sub-agents, state conflicts can occur. Tree of Work isolates sub-agent state in separate directories, preventing interference.

### Silent Drift

Agents modify files without updating their mental model. Tree of Work requires state updates when files change, maintaining consistency.

## Why Use This Skill?

### 1. Resumable Work

Stop and resume work at any point. The state file captures:

- Current task and progress
- Next concrete step
- Parked/blocked tasks with resume conditions
- Discovered sub-work (branches)

### 2. Focus Enforcement

One ACTIVE task at a time. This prevents:
- Context switching overhead
- Incomplete work accumulation
- Lost progress on abandoned tasks

### 3. Sub-Agent Isolation

Delegate work safely:
```bash
# Create isolated state for sub-agent
python scripts/tree_of_work.py --state-dir .agent/tree-of-work/subagents/feature-x init

# Sub-agent works in isolation
# After completion, merge back to main state
```

### 4. Legacy Absorption
Automatically absorbs existing project docs:
- ROADMAP.md → TODO tasks
- TODO.md → Active tasks
- CLAUDE.md → Context references

### 5. Security
Built-in secret detection prevents accidental exposure:
- Pattern matching for common secrets (GitHub tokens, API keys)
- Shannon entropy analysis for high-entropy strings
- Automatic redaction on validation

## Quick Start

### Prerequisites

- Python 3.8+ (for CLI tool)
- AI coding agent that supports skill loading
- Git (recommended)

### Installation

1. Copy the skill to your agent's skill directory:
   ```bash
   cp -r tree-of-work /path/to/your/agent/skills/
   ```

2. Initialize the state:
   ```bash
   python skills/tree-of-work/scripts/tree_of_work.py init
   ```

### Basic Usage

```bash
# Check current state
python scripts/tree_of_work.py status

# Get machine-readable output
python scripts/tree_of_work.py status --json

# Validate state integrity
python scripts/tree_of_work.py validate

# Create a snapshot
python scripts/tree_of_work.py snapshot -m "Completed auth module"

# Reset to default template
python scripts/tree_of_work.py reset
```

## State File Structure

The state file (`.agent/tree-of-work/current-state.md`) follows this structure:

```markdown
# Agent State Snapshot

## NOW

- **Task:** [TASK-01] Implement user authentication
  - **Status:** ACTIVE
  - **Primary Files:** src/auth.ts, src/middleware/auth.ts
  - **Latest Progress:** Created JWT validation middleware
  - **Next Concrete Step:** Add refresh token rotation
  - **Sub-Work / Branches:**
    - [x] [BUG-02] Fix token expiry check (Status: DONE)
    - [ ] [REFACTOR-03] Move types to auth.d.ts (Status: TODO)

## PARKED / BLOCKED

- [TASK-04] Database migration
  - STATUS: PARKED
  - Reason: Waiting for schema approval
  - Resume Condition: Run `npm run db:check`

## VALIDATION

- Unit Tests: NOT RUN
- Lint: NOT RUN
- Build: NOT RUN
```

## Status Model

| Status | Meaning | When to Use |
|--------|---------|-------------|
| `ACTIVE` | Currently working on (max 1) | Primary focus task |
| `PARKED` | Paused, unblocked | Can resume anytime |
| `BLOCKED` | Waiting on external dependency | Needs external action |
| `TODO` | Backlog, not started | Future work |
| `DONE` | Completed and verified | Finished tasks |

## Reference Files

Reference files are loaded on-demand only when specific conditions are met:

| File | Load When |
|------|-----------|
| `STATE_TEMPLATE.md` | About to run `init` |
| `ONBOARDING.md` | First session with no state file |
| `RECOVERY.md` | Resuming after crash/timeout |
| `SUBAGENTS.md` | Delegating to sub-agents |
| `CLASSIFICATION.md` | Unsure about task status |
| `STATUS_MODEL.md` | Need transition rules |
| `ANTI_PATTERNS.md` | Checking for problematic behaviors |
| `TRAPS.md` | Identifying context drift |

**Target: ~100-150 lines per session, not all 839.**

## Common Patterns

### Session Start
```bash
# 1. Check if state exists
python scripts/tree_of_work.py status

# 2. If resuming → read state, reconcile with git status
# 3. If fresh → scan for legacy docs or start ephemeral
```

### Task Transition
```bash
# 1. PARK current task
# 2. Update state file
# 3. ACTIVATE new task
# 4. Update Next Concrete Step
```

### Sub-Agent Delegation
```bash
# 1. Create isolated state
python scripts/tree_of_work.py --state-dir .agent/tree-of-work/subagents/id init

# 2. Sub-agent works in isolation
# 3. After completion: validate, merge back, archive
```

## Anti-Patterns

1. **Pasting raw API responses with secrets** → Sanitize first
2. **Marking multiple tasks ACTIVE** → One at a time, always
3. **Modifying files without updating state** → Update as you go
4. **Fixing "quick bugs" without parking** → Use Branch Promotion Protocol
5. **Scope drift** → Apply Scope Gate Test

## Gotchas

- **Never commit secrets in state files.** The script auto-redacts known patterns.
- **Single ACTIVE task is enforced.** `validate` fails if 2+ are ACTIVE.
- **Silent context drift.** Always update state when modifying files.
- **Don't fight existing state systems.** Absorb from ROADMAP.md, TODO.md.
- **Don't create files for simple tasks.** Keep tracking ephemeral until complexity warrants.
- **Python fallback.** If Python unavailable, edit `current-state.md` directly.

## CLI Reference

```bash
# Initialize state (auto-absorbs legacy docs)
python scripts/tree_of_work.py init

# Check current state
python scripts/tree_of_work.py status
python scripts/tree_of_work.py status --json

# Validate state file
python scripts/tree_of_work.py validate

# Snapshot current state
python scripts/tree_of_work.py snapshot -m "message"

# Reset to default template
python scripts/tree_of_work.py reset

# Override state directory
python scripts/tree_of_work.py --state-dir PATH <command>
```

## Contributing

See the [root README](../../README.md) for contribution guidelines.

## License

MIT License
