# State Template

Copy this template when creating or editing `.agent/tree-of-work/current-state.md`:

```markdown
# Agent State Snapshot

## NOW

- **Task:** [TASK-01] <task name>
  - **Status:** ACTIVE
  - **Primary Files:** <files being modified>
  - **Latest Progress:** <what was completed>
  - **Next Concrete Step:** <specific next action>
  - **Sub-Work / Branches:** -> example if exist
    - [ ] [BUG-02] Fix Timeout Webhook (Status: TODO) 
    - [x] [REFACTOR-03] Pindahin tipe data ke stripe.d.ts (Status: DONE)

## PARKED / BLOCKED

- [TASK-04] Migrasi Database Auth -> if exist example
  - STATUS: PARKED
  - Reason: Nunggu skema fix dari tim DevOps.
  - Resume Condition: Jalankan script `npm run db:check`.

## VALIDATION

- Unit Tests: NOT RUN
- Lint: NOT RUN
- Build: NOT RUN
```

## Field Rules

### NOW Section
- Exactly one task with `Status: ACTIVE`
- Prefix the task name with a unique sequential task ID, e.g. `[TASK-01]` or `[BUG-02]`.
- `Next Concrete Step` must be actionable (not "continue working on app")
- `Primary Files` lists actual file paths being modified

Good `Next Concrete Step`:
```
Add exponential backoff to WebSocket reconnect in prices.ts
```

Bad `Next Concrete Step`:
```
Continue working on app
```

### PARKED / BLOCKED Section
```markdown
- **Task:** [TASK-02] <task name>
  - **Status:** PARKED | BLOCKED
  - **Reason:** <why paused>
  - **Resume Condition:** <what must happen>
```

### BRANCHES Section
```markdown
- **Issue:** <description>
  - **Parent Task:** [TASK-01]
  - **Priority:** High | Medium | Low
  - **Status:** ACTIVE | PARKED | BLOCKED
```

Every branch **must** reference a parent task using its defined Task ID (e.g. `[TASK-01]`). Branches represent bugs, refactoring, failed tests, investigations, or dependency issues discovered during work.

### Relational Integrity Rules
- The validation engine (`validate` command) checks that the referenced parent ID in the `BRANCHES` section matches an existing defined ID in `## NOW` or `## PARKED / BLOCKED`. If a branch references an undefined ID, validation will fail.

### VALIDATION Section
Optional. Use when validation status matters for recovery or handoff.
