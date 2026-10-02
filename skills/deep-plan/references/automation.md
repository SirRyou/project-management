# Deep Plan Automation Gates

The automation CLI script is located at `<skill-dir>/script/deep_plan.py`, where `<skill-dir>` is the installation directory of this `deep-plan` skill (e.g. `skills/deep-plan/`, `~/.claude/skills/deep-plan/`, or your global/workspace skill directory).

Always execute CLI commands with the **target repository root** (containing `.deep-plan/`) as your working directory (`CWD`), pointing to the script via its skill directory path:
```bash
python "<skill-dir>/script/deep_plan.py" <command> <epic-slug> [options]
```
*(In the examples below, `deep_plan.py` refers to `<skill-dir>/script/deep_plan.py`)*.

The canonical execution state is `.deep-plan/<epic-slug>/execution-state.json`. The PM / Orchestrator is the only writer. Workers and reviewers return summaries and verdicts; the PM records them through the CLI. `progress-ledger.md` is a generated human-readable projection and must not be edited independently.

All agents may read the state needed for their role. The PM may read and mutate the full state. Planning agents may write only their assigned planning artifacts; workers may write only code in their worktree; reviewers return evidence but do not mutate execution state. State mutations must run from the parent PM checkout, never from a worker worktree.

The CLI validates structure and records a newly provisioned worktree. It does not run task-defined verification commands, infer task atomicity, dispatch child agents, decide parallel safety, interpret review findings, or merge commits. Those remain PM / Orchestrator decisions.

## Phase 1: Scaffold

After the PM selects an epic slug, create the isolated artifact workspace:

```bash
python script/deep_plan.py init <epic-slug>
python script/deep_plan.py validate <epic-slug> --stage scaffold
```

`init` refuses to overwrite an existing epic. It creates the required artifact files, `modules/`, `tasks/`, `research/`, and `handoff/`. The generated plan is deliberately incomplete; do not run full plan validation until Phase 3 artifacts exist.

## Phase 3: Validate the Plan and Initialize the Ledger

After Tier 1, Tier 2, Tier 3, and `dependency-dag.json` are authored:

```bash
python script/deep_plan.py sync-ledger <epic-slug>
python script/deep_plan.py validate <epic-slug>
```

Full validation checks required artifacts, safe task IDs, task-card/DAG correspondence, declared verification modes and commands, artifact traces, duplicate or unknown dependencies, self-dependencies, cycles, and ledger rows/statuses. It cannot prove that a task is truly atomic or that commands prove behavior; the Plan Challenger still owns that assessment.

Validation is a **shape** check, so read the edges before Phase 4:

```bash
python script/deep_plan.py edges <epic-slug>
```

This prints every DAG edge beside its target's semantic handle (the slug from the target card's filename), cross-module edges first. It always exits `0` — it is a review aid, not a gate. Use it to spot a citation that points at an ID renumbered after the citation was written: the DAG stays acyclic and resolvable while the meaning is gone, which `validate` cannot detect. Cards that cite a prerequisite with a slug (`T11-local-vad-port`) get a citation-drift check against the target's filename; bare-ID citations (`[T02, T11]`) are printed but not checked.

## Phase 5 and Execution: Derive Ready Work

After the plan has passed its review and approval gate, derive work only from the synchronized DAG and ledger:

```bash
python script/deep_plan.py status <epic-slug>
python script/deep_plan.py ready <epic-slug>
```

`ready` returns only tasks already marked `READY_TO_DISPATCH` whose dependencies are all `COMPLETED`. It does not promote `BLOCKED` tasks or silently resolve review and integration gates.

### Reopen a Blocked Task

When an external blocker is resolved, the PM may explicitly reopen a clean blocked task:

```bash
python script/deep_plan.py unblock <epic-slug> <task-id> \
  --reason "The required provider contract is approved." \
  --evidence evidence/provider-contract.md
```

The command requires a non-empty reason, evidence inside the epic, and completed dependencies. It returns the task to `READY_TO_DISPATCH` and records an audit event. It rejects failed-review tasks, tasks with prior worker/integration artifacts, and tasks at the remediation limit. Those cases require a formally revised and reviewed plan before reopening.

## PM-Owned State Mutations

Run all mutation commands from the parent PM checkout. They append an event, increment `state_revision`, atomically replace `execution-state.json`, and regenerate the ledger projection.

After a worker returns:

```bash
python script/deep_plan.py worker-record <epic-slug> <task-id> \
  --commit <worker-sha> --evidence reviews/<task-id>-worker.md
```

The task enters `IN_REVIEW` and receives the default review set: `standards`, `spec`, and `challenger`. Add risk-specific axes with repeated `--required-review security` or `--required-review performance`.

After a failed review, transition to `IN_REMEDIATION` and record the follow-up worker commit with `worker-record`; the command accepts that status, clears old verdicts, preserves all required axes, keeps the remediation count, and returns the task to `IN_REVIEW`.

Record each reviewer independently:

```bash
python script/deep_plan.py review-record <epic-slug> <task-id> \
  --axis standards --verdict PASS --evidence reviews/<task-id>-standards.md
```

Move to integration only after every required review is present and passing:

```bash
python script/deep_plan.py transition <epic-slug> <task-id> --to INTEGRATING
python script/deep_plan.py integration-record <epic-slug> <task-id> --commit <integrated-sha>
python script/deep_plan.py verify-record <epic-slug> <task-id> --evidence verification/<task-id>-integrated.md
python script/deep_plan.py transition <epic-slug> <task-id> --to COMPLETED
```

The CLI rejects incomplete fan-in, illegal transitions, missing evidence, worker-worktree mutations, and completion without an integrated commit plus integrated verification.

## Worker Worktrees

From the clean parent repository checkout, provision one worktree for a ready task:

```bash
python script/deep_plan.py worktree-create <epic-slug> <task-id> --parent <branch-or-commit>
```

`worktree-create` keeps the parent-checkout cleanliness guard by default. Use `--allow-dirty` only when unrelated parent changes are safe to leave out of the worker checkout. Set `--worktree-root <absolute-path>` to place the checkout on another drive; Deep Plan records that path for later resume and removal. Add `--install-deps` to install dependencies from a single recognized JavaScript lockfile using its frozen-lockfile mode. Package-manager lifecycle scripts run as part of installation, so use this option only with a repository whose dependencies you trust.

Remove a task checkout with `worktree-remove <epic-slug> <task-id>` after worker, reviewer, or integration activity has stopped. The command refuses active task states and dirty worktrees, and preserves the branch unless `--delete-branch` is passed; Git still refuses deletion of an unmerged branch. For an interrupted create whose path was not saved to execution state, pass its absolute registered path with `--worktree-path`. Unregistered paths are left untouched for manual inspection. `worktree-prune <epic-slug>` is a dry run for completed tasks. Pass `--apply` to remove eligible clean worktrees, and `--delete-branch` only when merged task branches should also be removed. Cleanup detaches directory links inside the worktree without following or deleting their targets.

After a worker records its commit and the task enters `IN_REVIEW`, pause worker edits. Reviewers inspect the recorded worker commit in that same checkout as read-only. Keep generated review artifacts outside the checkout or in isolated temporary directories. Do not start remediation until the review round has finished.

### Maintaining the Python CLI

From the repository root, install the development tools and run the focused checks with:

```powershell
uv sync --group dev
uv run ruff check skills/deep-plan/script
uv run pytest skills/deep-plan/script/test_deep_plan.py
```

The command refuses a dirty parent checkout unless `--allow-dirty` is set, and refuses an existing task branch or path rather than overwriting it. On success it creates a `task/<task-id>-<slug>` branch under `.worktrees/` by default (or under `--worktree-root`) and records the worktree with status `IN_PROGRESS` in the ledger.

## Pause and Resume Protocol

The CLI is the PM / Orchestrator agent's tool for gracefully stopping and restoring swarm execution when the user wants to stop for later (quota limits, fatigue, end-of-day, external blockers).

### In-Flight Pause Playbook

When execution must pause while tasks are in flight:

1. **Signal Active Workers:** Request each running Worker Implementer subagent to halt and provide an in-flight status report. Workers should report their last completed step based on incremental logs (`[Step X/Y Completed: ...]`).
2. **Enforce Worktree Hygiene (WIP Commit):** Ensure each active worker stages and commits all modified files in its worktree (`git commit -m "wip(T{n}): step X/Y - <summary>"`). 
   > [!IMPORTANT]
   > `pause` snapshots the *parent repository's* HEAD and branch, but **does not touch or commit files inside `.worktrees/`**. Never leave uncommitted dirty files in worker worktrees when pausing, or uncommitted work may be lost during session reset.
3. **Determine Step Counts:** Cross-check the worker's reported step `X` and total steps `Y` against the ordered list in Section 3 of `.deep-plan/<epic-slug>/tasks/<task-id>-*.md`.
4. **Execute CLI Pause:** Run the `pause` command from the parent repository root, repeating `--task-progress` for every in-flight task:

```bash
python "<skill-dir>/script/deep_plan.py" pause <epic-slug> \
  --reason quota \
  --note "T03 worker finished implementing interfaces, needs test run" \
  --task-progress T03:3:5 \
  --task-progress T04:1:3
```

The command:
1. Records declared step-level progress for in-flight tasks (`TASK_ID:COMPLETED_STEP:TOTAL_STEPS`).
2. Snapshots parent branch name and current HEAD commit.
3. Generates a timestamped handoff dossier in `.deep-plan/<epic-slug>/handoff/HANDOFF-YYYY-MM-DDTHHMM.md` containing session summaries, in-flight worktree details, step progress, and resume instructions.
4. Projects real checkpoint data into Section 5 of `progress-ledger.md`.
5. Sets `pause_state` in `execution-state.json` and records a `paused` audit event.

Allowed reasons: `quota`, `tired`, `eod`, `blocker`, `other`.

### Resume

```bash
python "<skill-dir>/script/deep_plan.py" resume <epic-slug>
```

The command:
1. Verifies parent branch HEAD matches the recorded checkpoint and warns on discrepancies.
2. Reconciles in-progress worktrees (checks for worker commits ahead of parent, reports next implementation steps).
3. Reports pending and failed reviews for in-review tasks.
4. Identifies ready-to-dispatch tasks from the DAG.
5. Clears `pause_state`, records a `resumed` audit event, and prints an actionable briefing for the next session.

`resume` is report-only and does not auto-advance tasks; the PM decides next actions. It also supports crash recovery when no prior pause command was executed.

## Safety Boundary

Treat task-provided verification commands as untrusted input until the PM has reviewed them. The CLI deliberately never runs them. Likewise, it never performs integration or removes worktrees. Those actions need the PM's explicit review of fan-in evidence and the repository's normal Git workflow.
