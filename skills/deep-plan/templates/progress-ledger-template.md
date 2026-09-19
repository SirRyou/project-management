# Swarm Execution Ledger

> Single source of truth for execution progress. Maintained by the PM / Orchestrator.

## 1. Task Execution State Matrix

| Task ID | Module | Dependencies | Worker Worktree | Worker Commit | Integrated Commit | Verification | Code Auditor | Challenger | Status | Remediation Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **T01** | M01 | None | `worktrees/T01` | `abc1234` | `abc1234` | `PASS` | `PASS` | `PASS` | **COMPLETED** | 0 |
| **T02** | M01 | T01 | `worktrees/T02` | `def5678` | — | `PASS` | `PASS` | `FAIL` | **IN_REMEDIATION** | 1 |
| **T03** | M02 | T01 | — | — | — | — | — | — | **READY_TO_DISPATCH** | 0 |

Allowed statuses:

```text
READY_TO_DISPATCH
IN_PROGRESS
IN_REVIEW
IN_REMEDIATION
INTEGRATING
VERIFIED
COMPLETED
BLOCKED
FAILED
CANCELLED
```

## 2. State Transition Rules

```text
READY_TO_DISPATCH -> IN_PROGRESS -> IN_REVIEW -> INTEGRATING -> VERIFIED -> COMPLETED
IN_REVIEW -> IN_REMEDIATION -> IN_REVIEW
IN_PROGRESS -> BLOCKED | FAILED
IN_REVIEW -> BLOCKED | FAILED
```

Unlock dependents only after the integrated commit, integrated-tree verification, and ledger update are recorded. Record the actor, timestamp, evidence path, and reason for every non-routine transition.

## 3. Review and Integration Evidence

### Task T01

- **Worker:** `[role and worktree]`
- **Worker Commit:** `abc1234`
- **Integrated Commit:** `abc1234`
- **Verification Mode:** `[mode]`
- **Verification Evidence:** `[commands and outputs]`
- **Code Auditor Standards Verdict:** `PASS`
- **Code Auditor Spec Verdict:** `PASS`
- **Adversarial Challenger Verdict:** `PASS`
- **Specialist Verdicts:** `[security/performance/documentation or N/A]`
- **Invariant Impact:** `[preserved or changed with reference]`

## 4. Active Blockers and Remediation Items

- **Task:** `[T{n}]`
- **Reason:** `[concrete blocker]`
- **Remediation Count:** `[number]`
- **Limit:** `[configured number]`
- **Escalation:** `[user decision, planning revision, or new session]`

## 5. Resume Checkpoint

- **Last completed transition:** `[task/state]`
- **Parent branch:** `[branch]`
- **Integrated commits:** `[list]`
- **Next ready tasks:** `[list]`
- **Pending user decisions:** `[list]`
- **Handoff summary:** `[path]`
