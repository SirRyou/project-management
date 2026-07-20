# Execution Handoff (Phase 5 → Implementation)

Hand finalized roadmap to execution. Three rules: isolation, WS-level dispatch, review loops.

> **This is a separate decision point from Phase 5's roadmap approval.** Phase 5 asks
> "is this roadmap correct?" — that confirmation, on its own, is not consent to execute.
> Section 1 below asks "should we execute it now?" and must be asked as its own
> question, even if the user just approved the roadmap in the same breath. Never
> infer a "yes" to Section 1 from a "yes" to the Phase 5 checkpoint — ask it explicitly
> and wait for a distinct answer.

---

## 1. Opt-In

Handoff optional. After roadmap finalized **and separately approved**, confirm with user:

> Roadmap finalized. Hand off to execution or stop for manual review?
>
> A) Hand off to execution
> B) Stop here

Declined → stop. Finalized roadmap = final deliverable.

If the user's roadmap approval message already contains an unambiguous, explicit instruction to execute (e.g. "approved, go ahead and build it"), that counts — but a bare "approved" / "looks good" / "ok" does not. When in doubt, ask Section 1 anyway.

---

## 2. Isolation Rule

**Never continue in same context that ran planning.**

Planning context loaded with drafts, review findings, rejected ideas, intermediate checklists. Wastes tokens, causes errors.

Execution starts in fresh session/subagent. Reads only finalized roadmap file.

---

## 3. Artifact Layout

All handoff artifacts live under `.deep-plan/handoff/`:

```
.deep-plan/handoff/
├── progress.md          # Ledger — survives compaction, tracks WS status
├── WS1-brief.md         # Extracted WS block for implementer
├── WS1-diff.md          # Git diff for reviewer
├── WS1-report.md        # Implementer's output (tests, concerns)
├── WS1-review.md        # Reviewer's verdict
├── WS2-brief.md
├── WS2-diff.md
├── WS2-report.md
├── WS2-review.md
└── ...
```

| Artifact | Created by | Contents |
|----------|-----------|----------|
| **Brief** | Controller (from roadmap) | Tasks + failure modes + security risks + exit criteria + sad paths for one WS |
| **Diff** | Controller (git diff) | Commit list + stat summary + full diff for the WS |
| **Report** | Implementer | What was done, exit criteria results, F-ids addressed, S-ids addressed, files changed, concerns |
| **Review** | Reviewer | Spec verdict + quality verdict + failure modes & security table |

---

## 4. Pre-Flight Scan

Before dispatching WS1, scan the roadmap once for:

- Tasks that contradict each other or the plan's global constraints
- Dependencies that form cycles
- Exit criteria that can't be machine-verified

Present findings as one batched question before execution begins. If clean, proceed without comment.

While scanning, also group work streams into dispatch waves from the Dependency Graph (see Section 5's parallel-dispatch note) — this is what Section 5 dispatches against, so do it once here rather than re-deriving it per WS.

---

## 5. Per-Workstream Dispatch Loop

For each workstream in dependency order — with one exception: **work streams the dependency graph marks as independent of each other may be dispatched in parallel**, each running its own 5a→5e loop concurrently. Only a WS with an unresolved dependency on another in-flight WS must wait. Check the roadmap's Dependency Graph section before dispatch to group WS into waves: everything with no unmet dependency in a wave goes out together, the next wave starts once its dependencies clear.

Sequential dispatch is still the default when the graph doesn't clearly separate independent work, or when running parallel dispatches would exceed what's practical to track in `progress.md` at once — parallelism is an optimization here, not an obligation.

### 5a. Extract WS Brief

Controller reads the roadmap, extracts the WS block, writes to `.deep-plan/handoff/WS{n}-brief.md`:

1. Copy the WS section from the roadmap (tasks table, failure modes, security risks, exit criteria, sad paths)
2. Copy relevant Architecture Decisions (D-ids) that affect this WS
3. Copy WS dependencies from the dependency graph
4. Write to `.deep-plan/handoff/WS{n}-brief.md`

### 5b. Dispatch Implementer

Give the implementer subagent (use [implementer-prompt.md](implementer-prompt.md)):

1. **WS brief path** — `.deep-plan/handoff/WS{n}-brief.md`
2. **Context** — what earlier workstreams produced that this WS depends on
3. **Decisions** — any D-ids that affect this WS (already in brief from 5a)
4. **Report path** — `.deep-plan/handoff/WS{n}-report.md`
5. **Working directory** — where to implement

The implementer:
- Implements all tasks in the WS
- Runs exit criteria verification commands
- Writes report with test results, commits, and concerns
- Returns: status + commit range + one-line test summary

**Status handling:**
- **DONE** → proceed to review
- **DONE_WITH_CONCERNS** → read concerns, address if correctness/scope, note if observation, proceed to review
- **NEEDS_CONTEXT** → provide missing context, re-dispatch
- **BLOCKED** → assess: context problem (re-dispatch), needs more capability (upgrade model), plan wrong (escalate to user)

### 5c. Generate Diff

Controller generates the diff file for the reviewer:

```bash
git diff [BASE_SHA]..[HEAD_SHA] > .deep-plan/handoff/WS{n}-diff.md
git log --oneline [BASE_SHA]..[HEAD_SHA] >> .deep-plan/handoff/WS{n}-diff.md
```

`BASE_SHA` = commit before this WS started. `HEAD_SHA` = current HEAD after implementer commits.

### 5d. Dispatch Reviewer

Give the reviewer subagent (use [reviewer-prompt.md](reviewer-prompt.md)):

1. **WS brief path** — `.deep-plan/handoff/WS{n}-brief.md`
2. **WS report path** — `.deep-plan/handoff/WS{n}-report.md`
3. **Diff path** — `.deep-plan/handoff/WS{n}-diff.md`
4. **Global constraints** — verbatim from roadmap (copy into prompt)

The reviewer returns two verdicts:
- **Spec compliance**: did implementer build what the WS tasks specify? Extra = bad, missing = bad.
- **Code quality**: implementation soundness, no new failure modes introduced.
- **Failure modes & security**: F-ids and S-ids addressed? Adequate?

### 5e. Review Loop

- Review passes → mark WS complete in progress.md, move to next WS
- Review fails → dispatch fix subagent with specific findings → re-review
- Repeat until approved. Never skip re-review.

**Fix subagent dispatch:**

Give the fix subagent:

1. **Findings** — the Critical and Important issues from the reviewer's verdict
2. **WS brief** — same brief the implementer used (for context)
3. **WS report** — implementer's report (for what was done)
4. **Diff** — the review diff (for what changed)

The fix subagent:
- Fixes all Critical and Important findings
- Re-runs the tests covering its changes
- Appends fix results to the same WS report file
- Returns: status + commits + test results

After fix, re-dispatch the reviewer with the updated report and new diff.

### 5f. Progress Ledger

Append to `.deep-plan/handoff/progress.md` after each WS completes. When WS are dispatched in parallel, log each independently as it finishes — don't wait for the whole wave:

```
WS1: complete (commits abc1234..def5678, review clean)
WS2: in progress (parallel wave with WS3)
WS3: in progress (parallel wave with WS2)
```

This survives compaction. After any context loss, check the ledger and `git log` to resume — for a wave in progress, resume only the WS still marked in-progress, not the ones already complete.

---

## 6. Final Review

After all workstreams complete, dispatch one final reviewer:

- Scope: cross-WS interactions, integration, overall plan compliance
- Give it: full roadmap + all WS reports + all WS diffs
- One fix subagent for all findings (not one per finding)

---

## Anti-Patterns

- **Auto-chaining** — starting implementation immediately after Phase 5. Skips user review.
- **Merging checkpoints** — treating roadmap approval and the Section 1 opt-in as the same question.
- **Same context** — writing code in planning session. Wastes tokens.
- **Bare titles** — delegating task list without steps/exit criteria/sad paths.
- **Per-task dispatch** — 10 tasks = 20+ subagent calls. Dispatch per WS instead.
- **Skipping re-review** — reviewer found issues = implementer fixes = review again.
- **Pasting context** — hand artifacts as files, not pasted text. Fresh subagent needs task + context, not session history.
- **Ignoring ledger** — after compaction, trust the ledger and `git log` over recollection.
- **Skipping brief extraction** — don't paste roadmap sections into prompts. Extract to file, pass path.