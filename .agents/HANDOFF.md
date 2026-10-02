# Session Handoff: Deep Plan Phase 3 Role Contracts

- **Timestamp**: 2026-09-20T00:00:00+07:00
- **Current Stage**: Phase 3 planning-contract refinement complete
- **Gate Token Status**: N/A - no active Cartesian epic

## Completed in this session

- [x] Made Phase 3 dispatch inputs explicit: fresh System Architect and Task Decomposer agents receive the epic slug and full `.deep-plan/<epic-slug>/...` artifact paths rather than vague tier names.
- [x] Defined System Architect ownership: Tier 2 module contracts only; no production-code edits, task-ID assignment, dependency decisions, ledger mutation, or silent boundary-fork resolution.
- [x] Added architecture contract expectations for ownership, preconditions, outcomes, failure behavior, compatibility, observability, invariants, NFRs, and risk evidence.
- [x] Defined Task Decomposer ownership: Tier 3 task cards, `dependency-dag.json`, and each Tier 2 module's Child Tasks manifest.
- [x] Replaced the absolute no-redecomposition rule with a controlled stop, report, PM replan, validate, and redispatch path.
- [x] Added executable task-card, dependency, parallel-safety, and plan-revision requirements.
- [x] Updated Tier 2 and Tier 3 templates to capture the new contract, traceability, and stop-condition evidence.
- [x] Verified whitespace with `git diff --check`.

## Changed files

- `skills/deep-plan/SKILL.md`
- `skills/deep-plan/references/tiered-planning.md`
- `skills/deep-plan/references/subagents/system-architect.md`
- `skills/deep-plan/references/subagents/task-decomposer.md`
- `skills/deep-plan/templates/tier2-module-template.md`
- `skills/deep-plan/templates/tier3-task-template.md`

## Next immediate steps for next session

- [ ] Exercise the revised System Architect and Task Decomposer contracts against a real Phase 3 epic; assess whether the resulting artifacts are independently actionable for workers.
- [ ] If the dry run reveals repeated ambiguity, extend the PM invocation envelope in `skills/deep-plan/references/invocation-contracts.md` with role-specific Phase 3 examples.
- [ ] Run the repository's documentation or skill validation command if one is introduced; this session changed only Markdown guidance and templates.

## Open Questions & Blockers

- No active blocker.
- The repository emits normal Git autocrlf warnings during checks; `git diff --check` passes.

## Commit status

- The Phase 3 refinement and this handoff document are included in the requested local commit.

# Session Handoff: Deep Plan Worktree Lifecycle Safety

- **Timestamp**: 2026-10-02T00:00:00+07:00
- **Current Stage**: Implementation complete; changes remain uncommitted
- **Gate Token Status**: N/A - no active Cartesian epic

## Problem and plan

The reported worktree lifecycle had unsafe cleanup paths, incomplete recovery/unblock behavior, limited support for external worktree roots, and weak diagnostics. The implementation plan ranked the risks as:

1. **P0 — prevent data loss on Windows**: treat junctions/symlinks safely and avoid deleting their targets.
2. **P1 — make cleanup and recovery reliable**: require registered Git worktree identity and expected branch, guard dirty and active work, support external roots, and provide dry-run pruning.
3. **P2 — improve operator control and diagnosis**: explicit dirty override, optional dependency install, orphan recovery, and clearer parent-checkout errors.
4. **P2 — reduce review races**: have reviewers inspect the worker's shared, frozen worktree read-only instead of creating a separate reviewer worktree.
5. **P2 — ease iteration**: configure Python linting and tests through uv.

## Built

- Added configurable external worktree roots with validation against nesting or containing the parent repository; persisted external paths as absolute paths and retained relative paths for the default root.
- Added `--allow-dirty` and opt-in `--install-deps` during worktree creation. Dependency setup recognizes supported JS lockfiles and uses their frozen/immutable install mode.
- Hardened removal around Git's registered worktree metadata and task-card branch identity. Dirty worktrees and tasks in active/review/integration states are protected. Directory links are detached without following their targets; tracked links are refused. Branch deletion is optional and uses safe `git branch -d`, preserving unmerged branches.
- Added `worktree-remove` recovery and `worktree-prune`, which previews by default and only targets completed tasks; `--apply` performs the cleanup.
- Improved parent checkout detection, including external worktrees, with diagnostics that identify the detected checkout.
- Documented the reviewer flow as read-only inspection of the worker worktree, plus lifecycle commands and uv checks.
- Added `pyproject.toml`, `uv.lock`, ignore rules for local uv/test artifacts, and regression coverage for lifecycle safety and recovery.

## Verification

- `uv --cache-dir .uv-cache run ruff check skills/deep-plan/script` — passed.
- `uv --cache-dir .uv-cache sync --locked --offline --group dev` — passed.
- `uv --cache-dir .uv-cache run pytest -rs skills/deep-plan/script/test_deep_plan.py` — 32 passed, 1 skipped. The skip is an existing directory-symlink test blocked by Windows symlink privilege (WinError 1314); the junction cleanup/target-preservation test passed.
- `git diff --check` — passed; Git reported normal LF-to-CRLF warnings.

## Changed files

- `.gitignore`
- `pyproject.toml` (new)
- `uv.lock` (new)
- `skills/deep-plan/SKILL.md`
- `skills/deep-plan/references/automation.md`
- `skills/deep-plan/script/deep_plan.py`
- `skills/deep-plan/script/test_deep_plan.py`

## Next steps

- Review the uncommitted diff, then commit when ready.
- In a real epic, exercise reviewer read-only inspection against the worker checkout and confirm the documented freeze is followed during review.
- Run `uv run ruff check skills/deep-plan/script` and `uv run pytest -rs skills/deep-plan/script/test_deep_plan.py` for subsequent Python changes. Use `uv sync --locked --group dev` to provision dependencies.
- If Windows symlink privilege is available in CI, run the skipped symlink case there as well.

## Open questions and blockers

- No implementation blocker remains. One platform-dependent symlink test was skipped due to the local Windows privilege limitation.
- `--install-deps` executes package-manager lifecycle scripts; it remains opt-in and should only be used for trusted repositories.
- No active Cartesian epic exists, so no gate token or epic progress ledger was updated.

## Commit status

- Implementation and verification are complete, but all listed changes remain uncommitted.
