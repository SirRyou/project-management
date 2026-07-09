# Context Recovery Protocol

Use this protocol when resuming work after a crash, timeout, session restart, or workspace handoff.

## Recovery Steps

### 1. Read State
```bash
python scripts/tree_of_work.py status
```
Identify: ACTIVE task, `Primary Files`, `Next Concrete Step`.

### 2. Reconcile with Disk
```bash
git status
git diff --name-only
```
Verify modified files match `Primary Files` in state.

### 3. If State File is Missing or Corrupt
1. Check `history/` for the latest snapshot: `history/snapshot_<timestamp>_<message>.md`
2. Restore snapshot contents into `current-state.md`
3. Validate: `python scripts/tree_of_work.py validate`

### 4. Resume
Begin from the `Next Concrete Step`. Do not switch tasks until the ACTIVE task is DONE or PARKED.

## Example

Agent starts a session, detects interrupted work:

```
$ python scripts/tree_of_work.py status
[ACTIVE FOCUS]
- **Task:** Implement WebSocket reconnect in prices.ts
- **Next Concrete Step:** Add exponential backoff algorithm
- **Primary Files:** src/utils/prices.ts

$ git status
modified: src/utils/prices.ts
```

Agent reads `prices.ts`, sees the reconnect loop is written but backoff is missing. Proceeds directly to implement backoff. Zero duplicated work.

## Snapshot Before Pausing

Always snapshot before returning control or ending a session:
```bash
python scripts/tree_of_work.py snapshot -m "Task phase completed"
```
