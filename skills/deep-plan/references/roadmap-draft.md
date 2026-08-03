# Reference: Roadmap Draft (Phase 3)

**Progressive Write Rule:** Write directly to `.deep-plan/<epic-name-in-kebab-case>.md` as you build. Do NOT hold everything in memory.

---

## Step 3.0: Append Roadmap Under Its Own Heading (do NOT restructure Phase 1-2)

Phase 3 **appends** a `## Phase 3: Roadmap` block to the living file under `## Phase 3: Roadmap` (H2). It does **not** rewrite or re-flow the Phase 1 Scope Brief or Phase 2 Gap Analysis — those stay where the progressive write put them. The template ([roadmap-template.md](../templates/roadmap-template.md)) is an append-order skeleton, not a final-layout contract; consumers locate sections by heading.

1. **Keep Phase 1-2 untouched.** Do not move `## PROBLEM` sections, do not merge `## Codebase Context`, do not delete `## Phase 2: Gap Analysis`. Failure Modes / Security Risks remain in 2A-2D and are referenced by F-id / S-id from the WS tables below.
2. **Architecture Decisions**: Create a `### Architecture Decisions` table under the Phase 3 heading for cross-cutting design decisions made during planning.
3. **Work Stream Sections**: For each deliverable workstream, build `### WS{n}` sections referencing the item-level Problem-Fit / Failure Modes / Security Risks from Phase 2 by F-id / S-id — do not copy their content in.

Only structural exception: if Phase 1 used a `# <Name>` title, keep it; it is the file title, not a phase section.

---

## Step 3.1: Structure Work Streams

From Phase 2's gap clusters (2E), group into **deliverable work streams** (WS). Each WS must:
- Be independently reviewable
- Have clear completion criteria
- Not cross too many domains/files (spike if >5 files)

**Format (append under `## Phase 3: Roadmap`):**

```markdown
### Work Streams

#### WS1: [Name]
##### Objective
[One sentence — why this WS exists, what invariant it protects]
##### Tasks
| ID | Task | Depends On | Mitigates (F-/S-id) | Risk | Status |
##### Sad Paths
##### Exit Criteria
##### Unit Tests
[Minimal unit tests for THIS WS's own logic — required. Cross-WS/integration/e2e goes in Cross-Cutting Work.]
```

## Step 3.2: Break Down Tasks (Per WS)
For each WS, list tasks **in execution order.**

### Architectural Rules for Task Design:

1. **Task Size Limit:** Each task must be ≤ 2 hours of work. If estimated higher, split it into atomic sub-tasks (e.g., T1.1a, T1.1b).
2. **Gap-to-Task Traceability:** Every failure mode (F{n}) and security risk (S{n}) identified in Phase 2 must map directly to at least one task or mitigation task in the roadmap (e.g., `T1.2: Add rate-limiting middleware (Mitigates S1)`).
3. **Opinionated Recommendation:** If a task has multiple implementation paths, do not simply ask the user. You must:
   - Present trade-offs of each option against system invariants (complexity, performance, security).
   - Declare a single, concrete recommendation.
   - Define the decision trigger (e.g., *"Choose Option B only if database scale exceeds X"*).
4. **Sad Path Mitigation:** Every task must have an explicit Sad Path entry defining what happens if operations fail, timeout, or receive malformed input, and how it is handled.

**Format (append to file):**

```markdown
#### WS1 — Task Breakdown

| ID  | Task | Depends On | Mitigates (F-/S-id) | Risk | Status |
|-----|------|------------|---------------------|------|--------|
| T1.1 | [Action + file] | None | F1 | Low | TODO |
| T1.2 | [Action + file] | T1.1 | S1 | Med | TODO |

#### WS1 — Sad Paths
- **T1.1:** [What fails]. **Mitigation:** [How it is handled].
- **T1.2:** [What fails]. **Mitigation:** [How it is handled].

#### WS1 — Unit Tests
- [ ] [minimal unit test(s) for THIS WS — required. No WS ships without its own unit test.]
- [ ] [cross-WS / integration / e2e tests → NOT here, put in `## Cross-Cutting Work`]
```

> **WS task table columns (canonical):** `ID | Task | Depends On | Mitigates (F-/S-id) | Risk | Status`.
> `Mitigates` carries the gap-to-task traceability from Phase 2 — every F-/S-id must map to >=1 task.

## Step 3.3: Define Exit Criteria (Machine-Checkable)
For each WS, write **exit criteria** – not "done", but provable verification.

```markdown
#### WS1 — Exit Criteria
- [ ] All tests pass: `go test ./...`
- [ ] Integration test for [endpoint] returns 200
- [ ] `grep -r "old_function"` returns 0 hits
- [ ] No new linter warnings
```

## Step 3.35: Define Cross-Cutting Work (required section)

After all WS are drafted, add a `### Cross-Cutting Work` section under `## Phase 3: Roadmap` for tasks
that bridge multiple WS or sprints: **integration / e2e test suites**, shared refactoring, type-safety
wiring, migration glue. Do **not** bury these inside a WS's task table.

```markdown
### Cross-Cutting Work
| ID | Task | Work Stream | Depends On | Status |
|----|------|-------------|------------|--------|
| X1 | [e2e harness] | WS1, WS3 | WS1-T1 | TODO  |
```

## Step 3.4: Map Dependencies & Critical Path
Write a simple text graph (canonical heading `## Dependency Graph` — not `Dependency Map`):

```markdown
## Dependency Graph
WS1 (auth) -> WS2 (db migration) -> WS3 (api handler)
WS1 -> WS4 (frontend client) (can run in parallel with WS2)
```

## Step 3.5: Log Open Unknowns (Research Backlog)
If Phase 2 left any `R{n}` items unresolved, write them here:

```markdown
## Research Backlog
| ID | Question | Priority | Status |
|----|----------|----------|--------|
| R1 | Does `libX` support retries? | High | Open |
| R2 | Which env var holds DB URL? | Low | Resolved (found in `.env.example`) |
```

## Step 3.6: Generate Reviewer Digest (for Phase 4)
Once the full roadmap file is written, extract **only this digest**. It is disposable, held in memory, and used exclusively to optimize reviewer prompts (saving token cost and context window bloat during adversarial review).

```markdown
## Reviewer Digest (DO NOT WRITE TO FILE – just hold for Phase 4)

**Problem-Fit Note:** [Summary of PARTIAL_FIT/MISFIT handled as debt]

**WS1 — [Name]**
- Key tasks: T1.1, T1.2, T1.3
- Highest risk: F1 ([trigger])

**Dependency Sketch:** WS1 → WS2 → WS3

**Confidence:** WS1=High, WS2=Med (R1 unresolved)
```

---

### Phase 3 Checklist (Self-QC before Phase 4)

- [ ] Every WS has at least 1 exit criterion
- [ ] Every task has a dependency (or "None")
- [ ] Every task is <= 2h work (or split)
- [ ] Every task has a Sad Path mitigation defined
- [ ] Every WS has its own minimal unit test (no WS ships untested)
- [ ] All Phase 2 gaps (F-ids and S-ids) trace directly to tasks via the `Mitigates` column
- [ ] `## Cross-Cutting Work` exists and holds integration/e2e/multi-WS tasks
- [ ] Research Backlog has priority tags
- [ ] Full file is written, not just the digest (`## Phase 3: Roadmap` appended, Phase 1-2 left intact)

## Failure Modes (Anti-Patterns)

| Anti-Pattern | Why It Fails |
| ------------ | ------------ |
| Writing only the digest, skipping the full file | Phase 5 can't audit what doesn't exist |
| Tasks with vague verbs ("implement", "refactor") | No verification possible → scope creep |
| No exit criteria | "Done" is subjective → rushed PRs |
| Holding roadmap in memory until Phase 5 | Memory collapse → compressed details → wrong plan |
