# Deep Plan Automation Gates

Use `script/deep_plan.py` for deterministic workspace and plan-state checks. Run it from the repository root containing `.deep-plan/`.

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

## Phase 5 and Execution: Derive Ready Work

After the plan has passed its review and approval gate, derive work only from the synchronized DAG and ledger:

```bash
python script/deep_plan.py status <epic-slug>
python script/deep_plan.py ready <epic-slug>
```

`ready` returns only tasks already marked `READY_TO_DISPATCH` whose dependencies are all `COMPLETED`. It does not promote `BLOCKED` tasks or silently resolve review and integration gates.

## PM-Owned State Mutations

Run all mutation commands from the parent PM checkout. They append an event, increment `state_revision`, atomically replace `execution-state.json`, and regenerate the ledger projection.

After a worker returns:

```bash
python script/deep_plan.py worker-record <epic-slug> <task-id> \
  --commit <worker-sha> --evidence reviews/<task-id>-worker.md
```

The task enters `IN_REVIEW` and receives the default review set: `standards`, `spec`, and `challenger`. Add risk-specific axes with repeated `--required-review security` or `--required-review performance`.

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

The command refuses a dirty parent checkout, an existing task branch or worktree, an unknown/non-ready task, and an unverifiable parent ref. On success it creates `.worktrees/<task-id>-<slug>`, creates a `task/<task-id>-<slug>` branch, and records the worktree with status `IN_PROGRESS` in the ledger.

## Safety Boundary

Treat task-provided verification commands as untrusted input until the PM has reviewed them. The CLI deliberately never runs them. Likewise, it never performs integration or removes worktrees. Those actions need the PM's explicit review of fan-in evidence and the repository's normal Git workflow.
