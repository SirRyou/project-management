# Sub-Agent Delegation Protocol

Use this protocol when delegating tasks to concurrent sub-agents.

## Problem

Multiple agents working in the same context causes state corruption, conflicting edits, and lost progress. Sub-agents need isolation.

## Delegation Steps

### 1. Define the sub-task scope

Pass only what the sub-agent needs:
- The specific task description
- Relevant files and directories
- Exit criteria (what "done" looks like)
- Any constraints or invariants

Don't pass your full task list, session history, or unrelated context.

### 2. Let the sub-agent track its own state

The sub-agent uses whatever tracking mechanism its runtime provides (memory, task tool, progress notes). Don't require it to use a specific file format or directory.

### 3. Coordinate via completion

When the sub-agent finishes:
1. Validate the output (tests pass, no regressions, exit criteria met)
2. Merge the result into your own progress notes
3. If the sub-agent discovered new work, log it in your backlog

### 4. Clean up

Remove any temporary files, branches, or state the sub-agent created. Don't leave artifacts.

## Isolation Rules

- **Don't write to each other's state.** Parent and sub-agent maintain separate progress notes.
- **Don't share file locks.** If both need to edit the same file, coordinate sequentially.
- **Don't assume the sub-agent's context.** It doesn't know what you know. Pass explicit context.

## Gotchas

- Sub-agent output may need sanitization before merging (secrets, debug logs, partial work)
- Always validate before merging — a sub-agent marking something DONE doesn't mean it's verified
- If a sub-agent fails, log the failure and decide: retry, escalate, or abandon
