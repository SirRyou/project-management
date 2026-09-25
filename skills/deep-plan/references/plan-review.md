# Reference: Adversarial Plan Review (Phase 4)

Dispatch the Plan Challenger after Tier 1, Tier 2, Tier 3, and the DAG exist but before implementation begins.

This is the canonical challenge checklist. The Plan Challenger role specification points here rather than restating it; `docs/reference-deep-plan.md` mirrors this list and its count.

For resilience-specific criteria (failure handling, async lifecycles, state integrity, backward compatibility, and the rest), the reviewer may consult [resilience-first-development.md](resilience-first-development.md), which indexes ~20 chapters under `resilience-development-book/`. That book is not reachable from anywhere else in the workflow — treat this as its entry point.

## Inputs

- `.deep-plan/<epic-slug>/00-intent.md`
- `.deep-plan/<epic-slug>/01-grounding.md`
- `.deep-plan/<epic-slug>/02-risk-register.md`
- `.deep-plan/<epic-slug>/03-tier1-epic.md` (including §6, the frozen contract registry)
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
10. **Cross-module contract agreement.** For every `C-xx` in `03-tier1-epic.md` §6: do all listed consumers cite the same ID, and is any **superseded** ID still cited by a consumer? Compare IDs and acknowledgement cells, not prose signatures — a citation that exists but points at a superseded contract is the defect, and an existence check cannot see it. An unacknowledged consumer (`—`) is a blocking finding, not a formatting gap.
11. **Semantic ID drift.** Does every prerequisite citation's slug match its target card's filename stem? `T11-localvadport` resolving to a card named `capabilities-card` means the ID was renumbered after the citation was written. Renumbering preserves referential integrity while destroying meaning; the DAG stays acyclic, resolvable, and wrong.
12. **Test integrity.** Does the test configuration exclude the correct paths? Are stale copies reachable from a repo-wide run — worktrees, build output, vendored duplicates? A suite that runs stale code can report green while the real tree is red.
13. **Silent data loss.** Does any path discard, truncate, or reorder data without emitting a signal to the user or an observable? Capped buffers that drop the *oldest* input are the canonical case: the result is committed and plausible, merely missing its beginning. This is the **plan-time** counterpart to the Adversarial Challenger's code-time "Silent Failures" check — raise it here when the design itself creates the silent path, not merely when an implementation forgets to log.
14. **Deletion parity.** For every deletion or replacement, is a parity proof for the replaced behavior recorded **before** the delete? See `resilience-development-book/Pre-Merge-Checklist.md` (Two-Step Deprecation) and `Backward-Compatibility-&-Deprecation.md`.

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
