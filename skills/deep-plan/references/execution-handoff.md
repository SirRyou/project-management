# Execution Handoff (Phase 5 → Implementation)

Hand finalized roadmap to execution. Three rules: isolation, sprint-level dispatch, review loops.

---

## 1. Isolation Rule

**Never continue in same context that ran planning.**

Planning context loaded with drafts, review findings, rejected ideas, intermediate checklists. Wastes tokens, causes errors.

Execution starts in fresh session/subagent. Reads only finalized roadmap file.

---

## 2. Artifact Layout

**Dispatch unit is the Sprint** (from the roadmap's Implementation Order), not the Workstream. A Workstream (WS) is a conceptual grouping of tasks in the roadmap; a Sprint is the actual execution order after cross-WS dependencies are resolved. Since a single WS can split across multiple sprints (see Pre-Flight Scan), Sprint is the only grain that reflects real dispatch order — using both as separate handoff keys is redundant and a source of confusion.

WS still shows up as metadata inside each brief (so you can trace a task back to its roadmap section), and as a lane suffix only when a sprint has multiple independent task lanes dispatched in parallel.

All handoff artifacts live under `.deep-plan/handoff/`:

```
.deep-plan/handoff/
├── progress.md              # Ledger — survives compaction, tracks Sprint status
├── Sprint1-brief.md         # Extracted task set for this sprint
├── Sprint1-diff.diff        # Git diff for reviewer
├── Sprint1-report.md        # Implementer's output (tests, concerns)
├── Sprint1-review.md        # Reviewer's verdict
├── Sprint2-brief.md
├── Sprint2-diff.diff
├── Sprint2-report.md
├── Sprint2-review.md
└── ...
```

If a sprint has parallel lanes (independent WS running concurrently within the same sprint), suffix the lane: `Sprint3-WS1-brief.md`, `Sprint3-WS3-brief.md` — but log a single `Sprint3` entry in `progress.md`, not one per lane, so the ledger still reads as one row per dispatch wave.

| Artifact   | Created by                | Contents                                                                                        |
| ---------- | ------------------------- | ----------------------------------------------------------------------------------------------- |
| **Brief**  | Controller (from roadmap) | Tasks + failure modes + security risks + exit criteria + sad paths for this sprint's task set    |
| **Diff**   | Controller (via script)   | Commit list + stat summary + full diff for the sprint                                            |
| **Report** | Implementer               | What was done, exit criteria results, F-ids addressed, S-ids addressed, files changed, concerns |
| **Review** | Reviewer                  | Spec verdict + quality verdict + failure modes & security table                                 |

---

## 3. Pre-Flight Scan

Before dispatching Sprint 1, scan the roadmap once for:

- Tasks that contradict each other or the plan's global constraints
- Dependencies that form cycles
- Exit criteria that can't be machine-verified

**Dependency Graph ↔ Implementation Order cross-check (mandatory):**

- Every task ID (`Tn`) that appears in the Dependency Graph must appear exactly once in the Implementation Order. A task missing from every sprint is a **dropped dependency** — stop and report before any dispatch, don't proceed silently.
- For every task's declared dependency (`── Tx`), `Tx` must be scheduled in the same sprint or an earlier one. If `Tx` is referenced but never scheduled anywhere, that's the same dropped-dependency error above, just surfaced from the other direction — check both directions.
- If a WS's tasks are split across multiple sprints (not dispatched as one contiguous block, e.g. a WS whose header lists dependencies on other WS but whose own tasks land in different sprints), verify each split task still only depends on tasks from its own or earlier sprints — a later-sprint task can't quietly depend on a same-WS task that got pushed to an even later sprint.

> Present findings as one batched question before execution begins. If clean, proceed without comment.

While scanning, also group tasks into sprint dispatch waves from the Dependency Graph and Implementation Order (see Section 4's parallel-dispatch note) — this is what Section 4 dispatches against, so do it once here rather than re-deriving it per sprint.

---

## 4. Per-Sprint Dispatch Loop

For each sprint in Implementation Order — with one exception: **task lanes the dependency graph marks as independent of each other within the same sprint may be dispatched in parallel**, each running its own 4a→4e loop concurrently as a lane under that sprint. Only a lane with an unresolved dependency on another in-flight lane must wait.

Sequential dispatch is still the default when the graph doesn't clearly separate independent lanes, or when running parallel lanes would exceed what's practical to track in `progress.md` at once — parallelism is an optimization here, not an obligation.

**Parallel lanes must be isolated**, not just diffed carefully after the fact: give each lane its own git worktree/branch off the same base commit. This is what makes Section 4c's ancestor check meaningful — without isolation, commits from concurrent lanes interleave in `git log` and a naive `BASE..HEAD` diff for one lane can silently capture another lane's changes.

### 4a. Extract Sprint Brief

Controller reads the roadmap, extracts the task set for this sprint, and writes to `.deep-plan/handoff/Sprint{m}-brief.md` (or `Sprint{m}-{lane}-brief.md` for a parallel lane):

1. Identify the task IDs scheduled in this sprint (from Implementation Order) — this may be a full WS or a subset of one
2. Copy each task's row from the WS task table(s) it belongs to — if tasks come from more than one WS, pull from each source WS section, and note the source WS per task for traceability
3. Copy relevant Architecture Decisions (D-ids) that affect these tasks
4. Copy each task's dependencies resolved to specific task IDs (not "depends on WS1") — the brief should never require the implementer to re-derive dependencies from the graph
5. Note which prior sprint(s) produced the dependencies listed, so the implementer knows what already exists to build on
6. Include failure modes, security risks, exit criteria, and sad paths for these specific tasks
7. Write to `.deep-plan/handoff/Sprint{m}-brief.md`

### 4b. Dispatch Implementer

Give the implementer subagent (use [implementer-prompt.md](implementer-prompt.md)):

1. **Sprint brief path** — `.deep-plan/handoff/Sprint{m}-brief.md`
2. **Context** — what earlier sprints produced that this sprint depends on
3. **Decisions** — any D-ids that affect this sprint (already in brief from 4a)
4. **Report path** — `.deep-plan/handoff/Sprint{m}-report.md`
5. **Working directory** — where to implement (or the isolated worktree path, for a parallel lane)

The implementer:

- Implements all tasks in the sprint brief
- Runs exit criteria verification commands
- Writes report with test results, commits, and concerns
- Returns: status + commit range + one-line test summary

**Status handling:**

- **DONE** → proceed to review
- **DONE_WITH_CONCERNS** → read concerns, address if correctness/scope, note if observation, proceed to review
- **NEEDS_CONTEXT** → provide missing context, re-dispatch
- **BLOCKED** → assess: context problem (re-dispatch), needs more capability (upgrade model), plan wrong (escalate to user)

### 4c. Generate Diff

Controller generates the diff file for the reviewer using the shared script rather than raw `git diff`, so the ancestor check and expected-files cross-check always run:

```bash
script/generate-diff.sh \
  --sprint {m} \
  [--ws-lane WS{n}] \
  --base [BASE_SHA] \
  --head [HEAD_SHA] \
  [--worktree [WORKTREE_PATH]]
```

`BASE_SHA` = commit before this sprint (or lane) started. `HEAD_SHA` = current HEAD after implementer commits. The diff is **raw** — no scoping, no filtering. The reviewer sees everything, including shared-file changes from parallel work. The script's only guardrail is the ancestor check: it refuses to diff if `BASE_SHA` is not an ancestor of `HEAD_SHA`.

Shared-file changes (orchestrator, runtime, typed wiring) in the diff are handled by the reviewer, not filtered by the diff generator — see `reviewer-prompt.md` §Shared Files.

### 4d. Dispatch Reviewer

Give the reviewer subagent (use [reviewer-prompt.md](reviewer-prompt.md)):

1. **Sprint brief path** — `.deep-plan/handoff/Sprint{m}-brief.md`
2. **Sprint report path** — `.deep-plan/handoff/Sprint{m}-report.md`
3. **Diff path** — `.deep-plan/handoff/Sprint{m}-diff.diff`
4. **Global constraints** — verbatim from roadmap (copy into prompt)

The reviewer returns two verdicts:

- **Spec compliance**: did implementer build what the sprint's tasks specify? Extra = bad, missing = bad.
- **Code quality**: implementation soundness, no new failure modes introduced.
- **Failure modes & security**: F-ids and S-ids addressed? Adequate?

### 4e. Review Loop

- Review passes → mark sprint complete in progress.md, move to next sprint
- Review fails → dispatch fix subagent with specific findings → re-review
- Repeat until approved. Never skip re-review.

**Fix subagent dispatch:**

Give the fix subagent:

1. **Findings** — the Critical and Important issues from the reviewer's verdict
2. **Sprint brief** — same brief the implementer used (for context)
3. **Sprint report** — implementer's report (for what was done)
4. **Diff** — the review diff (for what changed)

The fix subagent:

- Fixes all Critical and Important findings
- Re-runs the tests covering its changes
- Appends fix results to the same sprint report file
- Returns: status + commits + test results

After fix, re-dispatch the reviewer with the updated report and new diff (regenerate via `script/generate-diff.sh`, don't hand-edit the old one).

### 4f. Progress Ledger

Append to `.deep-plan/handoff/progress.md` after each sprint completes. When lanes are dispatched in parallel within a sprint, log the sprint as one entry, in progress until all its lanes clear:

```
Sprint1: complete (commits abc1234..def5678, review clean)
Sprint2: complete (commits def5678..a1b2c3d, review clean)
Sprint3: in progress (lanes: WS1 done, WS3 in progress)
```

This survives compaction. After any context loss, check the ledger and `git log` to resume — for a sprint with lanes in progress, resume only the lanes still marked in-progress, not the ones already complete.

---

## 5. Final Review

After all sprints complete, dispatch one final reviewer:

- Scope: cross-sprint interactions, integration, overall plan compliance
- Give it: full roadmap + all sprint reports + all sprint diffs
- One fix subagent for all findings (not one per finding)

---

## Anti-Patterns

- **Auto-chaining** — starting implementation immediately after Phase 5. Skips user review.
- **Same context** — writing code in planning session. Wastes tokens.
- **Bare titles** — delegating task list without steps/exit criteria/sad paths.
- **Per-task dispatch** — 10 tasks = 20+ subagent calls. Dispatch per sprint instead.
- **WS as the dispatch key** — dispatching by Workstream when the roadmap's Implementation Order splits a WS across sprints causes dropped dependencies (a task scheduled in an earlier sprint than the WS-mate it depends on, or never scheduled at all). Sprint is the source of truth for order; WS is metadata.
- **Unscoped diffs** — filtering the diff to hide shared-file changes from the reviewer. Shared files are integration points; hiding them breaks cross-sprint coordination. The reviewer handles shared files, not the diff generator.
- **Skipping re-review** — reviewer found issues = implementer fixes = review again.
- **Pasting context** — hand artifacts as files, not pasted text. Fresh subagent needs task + context, not session history.
- **Ignoring ledger** — after compaction, trust the ledger and `git log` over recollection.
- **Skipping brief extraction** — don't paste roadmap sections into prompts. Extract to file, pass path.