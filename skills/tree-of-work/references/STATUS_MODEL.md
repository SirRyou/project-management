# Status Model

## Task Statuses

| Status | Meaning | Constraint |
|--------|---------|------------|
| `ACTIVE` | Currently being worked on | Max 1 across entire workspace |
| `PARKED` | Paused, unblocked | Can resume anytime |
| `BLOCKED` | Waiting on external dependency | Requires `Reason` + `Resume Condition` |
| `TODO` | Backlog, not started | Initial status for new tasks |
| `DONE` | Completed and verified | Terminal state |

## Transition Rules

### Switching Tasks
Edit `.agent/tree-of-work/current-state.md` manually:
1. Update the previous task under `## PARKED / BLOCKED` (set its Status to `PARKED` or `BLOCKED`, and add a reason/resume condition).
2. Set the target task to `ACTIVE` under `## NOW`.
3. Update `Primary Files`, `Latest Progress`, and `Next Concrete Step` in the `## NOW` section.

### Completing a Task
1. Run validation checks (tests, lint, build).
2. Manually change the task's Status under `## NOW` to `DONE` or create the next active task.
3. Save a history snapshot of the completion by running:
   ```bash
   python scripts/tree_of_work.py snapshot -m "DONE: [TASK-XX] <task name>"
   ```
4. Update `## NOW` to contain the next active task from the parked backlog.

## Git Integration Guidelines

This skill tracks **logical state**, not Git workflow. Your project's Git conventions (commit message format, branching strategy, pre-commit hooks) take priority.

The following are **soft guidelines** to help agents avoid common pitfalls — not rigid rules.

### 1. One Physical Branch per Core Goal

Keep all logical sub-tasks and transient branches on the same physical Git branch assigned to the parent task. Do not create new Git branches for items discovered in the `BRANCHES` section unless explicitly requested by the user.

Creating a physical branch for every small bug or refactoring discovered during work leads to repository clutter, merge conflicts, and wasted execution time.

### 2. Commit on Context Shifts (Recommended)

When transitioning a task from `ACTIVE` to `PARKED` or `DONE`, it is good practice to stage and commit your work along with the state file change. This keeps Git history aligned with logical progress.

This is a recommendation, not a requirement — respect your project's own commit conventions.

### 3. Respect Local Hooks

If the repository uses pre-commit hooks, commit-msg hooks, or automated linting (e.g., Husky, lint-staged, Commitizen), follow those rules. If hooks fail, fix the code formatting rather than forcing the commit.

### Example

Agent working on Stripe webhooks discovers a timeout bug:

1. **Park parent, activate fix:**
   ```markdown
   ## NOW
   - **Task:** Fix webhook timeout
   - **Status:** ACTIVE
   - **Primary Files:** src/services/stripe.ts
   - **Latest Progress:** Discovered 10s connection timeout on validation
   - **Next Concrete Step:** Add reconnect logic

   ## PARKED / BLOCKED
   - **Task:** Integrate Stripe API
     - **Status:** PARKED
     - **Reason:** Webhook timeout blocks integration testing
     - **Resume Condition:** "Fix webhook timeout" reaches DONE
   ```

2. **Fix the bug, then resume parent:**
   - Mark "Fix webhook timeout" as DONE
   - Move "Integrate Stripe API" back to NOW as ACTIVE
   - Commit according to your project's conventions

## Validation

Always validate before marking tasks DONE:
```bash
python scripts/tree_of_work.py validate
```
