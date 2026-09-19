# Reference: Adversarial Plan Review (Phase 4)

Dispatch the Plan Challenger after Tier 1, Tier 2, Tier 3, and the DAG exist but before implementation begins.

## Inputs

- `.deep-plan/<epic-slug>/00-intent.md`
- `.deep-plan/<epic-slug>/01-grounding.md`
- `.deep-plan/<epic-slug>/02-risk-register.md`
- `03-tier1-epic.md`
- All Tier 2 module specifications.
- All Tier 3 task cards.
- `dependency-dag.json`.
- Repository workflow and verification commands.

## Challenge

Review the plan for:

1. Scope drift or missing user outcomes.
2. Inferred invariants that require confirmation.
3. Architecture boundaries that do not match ownership or data flow.
4. Risks without mitigation, acceptance, or explicit deferral.
5. Missing or circular artifact and contract dependencies.
6. Tasks that are too broad, too narrow, or not independently verifiable.
7. Verification commands that cannot prove the acceptance criteria.
8. Unresolved external behavior that workers might guess at.
9. Security, privacy, performance, migration, or rollback gaps.

## Verdict

Return:

```markdown
### Plan Challenge: [Epic Name]
- **Verdict:** PASS | REVISE | USER_DECISION_REQUIRED
- **Findings:** [file or artifact path, issue, impact]
- **Required Changes:** [concrete remediation]
- **User Decisions:** [boundary-changing choices with recommendation and tradeoffs]
```

Do not approve a plan with an unresolved material finding. When the verdict is `USER_DECISION_REQUIRED`, pause execution and use the runtime's structured question tool one decision at a time.
