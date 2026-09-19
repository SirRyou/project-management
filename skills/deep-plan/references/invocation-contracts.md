# Deep Plan Invocation Contracts

The parent PM owns the dynamic user prompt. Runtime adapters must preserve the static system prompt and pass this message as the task/user prompt.

## Common envelope

Every invocation should include:

1. Agent role and invocation contract.
2. Epic and task identifiers.
3. Authoritative artifact paths.
4. Explicit task objective.
5. Relevant intent, grounding, and risk evidence.
6. Worktree, branch, integration target, and permission boundaries.
7. Verification mode and required commands.
8. Required output contract.

Example:

```text
Execute task T3 for epic <epic-slug>.

Authoritative inputs:
- Tier 3 task: .deep-plan/<epic-slug>/tasks/T3-name.md
- Parent module: .deep-plan/<epic-slug>/modules/M2-name.md

Constraints:
- Modify only the target files listed in the task card.
- Follow repository conventions and the task acceptance criteria.
- Run every required verification command.

Return the output contract defined by your role specification.
```

## Contract names

| Contract | Used by | Required result |
| --- | --- | --- |
| `exploration-dossier` | Codebase Explorer | Grounding Dossier |
| `tier2-module-design` | System Architect | Tier 2 module contract |
| `tier3-task-decomposition` | Task Decomposer | Tier 3 cards and dependency DAG |
| `worker-task-execution` | Worker Implementer | Commit, tests, and execution summary |
| `plan-challenge` | Plan Challenger | Plan PASS/REVISE/USER_DECISION_REQUIRED verdict |
| `code-audit` | Code Auditor | Separate Standards and Spec PASS/FAIL verdicts |
| `adversarial-challenge` | Adversarial Challenger | Invariant and edge-case findings |
| Specialist contracts | Specialist agents | Role-specific evidence and output |

Do not place task-specific file paths, acceptance criteria, or reviewer findings in the installed system prompt.
