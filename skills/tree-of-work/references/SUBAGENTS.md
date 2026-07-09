# Sub-Agent Delegation Protocol

Use this protocol when delegating tasks to concurrent sub-agents within the same workspace.

## Problem

Multiple agents writing to the same `current-state.md` causes state corruption, status loss, and conflicting progress logs.

## Delegation Steps

### 1. Create Isolated State Directory
```bash
python scripts/tree_of_work.py --state-dir .agent/tree-of-work/subagents/<sub-agent-id> init
```

### 2. Write Sub-Agent Task State

In `.agent/tree-of-work/subagents/<sub-agent-id>/current-state.md`:
```markdown
## NOW
- **Task:** <specific sub-task>
- **Status:** ACTIVE
- **Primary Files:** <files for this sub-task>
- **Next Concrete Step:** <first action>
```

No unrelated parent tasks. Only the sub-agent's assignment.

### 3. Launch Sub-Agent

Pass the state directory via:
- CLI flag: `--state-dir .agent/tree-of-work/subagents/<sub-agent-id>`
- Environment variable: `TREE_OF_WORK_DIR=.agent/tree-of-work/subagents/<sub-agent-id>`

### 4. Validate and Merge

After sub-agent completes:
```bash
python scripts/tree_of_work.py --state-dir .agent/tree-of-work/subagents/<sub-agent-id> validate
```

If valid and status is DONE:
1. Update parent's `current-state.md` — mark the delegated branch as DONE
2. Archive or delete the sub-agent directory

## Directory Structure

```
.agent/tree-of-work/
├── current-state.md              ← Main state
├── history/                      ← Snapshots
└── subagents/
    └── <sub-agent-id>/
        ├── current-state.md      ← Isolated state
        └── history/              ← Sub-agent snapshots
```

## Gotchas

- Sub-agent directories are in `.gitignore` — don't commit them
- Always validate sub-agent output before merging back to parent state
- Clean up sub-agent directories after merging to avoid clutter
