# Reference: Roadmap Draft (Phase 3)

**Progressive Write Rule:** Write directly to `.deep-plan/<epic-name-in-kebab-case>.md` as you build. Do NOT hold everything in memory.

---

## Step 3.0: Reorganize to Roadmap Template
Before drafting workstreams, reorganize the existing Phase 1 Scope Brief and Phase 2 Gap Analysis findings into the unified structure defined in [roadmap-template.md](templates/roadmap-template.md):
1. **Context & Invariants**: Group the problem, objective, scopes, assumptions, codebase context, and invariants at the top of the file.
2. **Architecture Decisions**: Create a `## Architecture Decisions` table for recording cross-cutting design decisions made during planning.
3. **Work Stream Sections**: For each deliverable workstream you group:
   - Move the corresponding item-level Problem-Fit, Failure Modes, and Security Risks from the Phase 2 Gap Analysis section into this workstream section under `#### Problem-Fit`, `#### Failure Modes`, and `#### Security Risks`.
   - If a workstream has no security surface, write `No security surface — reason: [why]`.
4. **Clean up**: Remove the redundant `# Phase 2: Gap Analysis` section once its contents are distributed.

---

## Step 3.1: Structure Work Streams

From Phase 2's gap clusters, group into **deliverable work streams** (WS). Each WS must:
- Be independently reviewable
- Have clear completion criteria
- Not cross too many domains/files (spike if >5 files)

**Format (append to file):**

```markdown
## Work Streams (Phase 3)

### WS1: [Name]
- **Objective:** [One sentence]
- **Owner:** [Role/person, if known]
- **Dependencies:** [Other WS IDs or external deps]
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
### WS1 — Task Breakdown

| ID  | Task | Dependencies | Verification |
|-----|------|--------------|--------------|
| T1.1 | [Action + file] | None | [Command to prove it works] |
| T1.2 | [Action + file] (Mitigates S1) | T1.1 | [Test case to pass] |

#### WS1 — Sad Paths
- **T1.1:** [What fails]. **Mitigation:** [How it is handled].
- **T1.2:** [What fails]. **Mitigation:** [How it is handled].
```

## Step 3.3: Define Exit Criteria (Machine-Checkable)
For each WS, write **exit criteria** – not "done", but provable verification.

```markdown
### WS1 — Exit Criteria
- [ ] All tests pass: `go test ./...`
- [ ] Integration test for [endpoint] returns 200
- [ ] `grep -r "old_function"` returns 0 hits
- [ ] No new linter warnings
```

## Step 3.4: Map Dependencies & Critical Path
Write a simple text graph:

```markdown
## Dependency Map
WS1 (auth) → WS2 (db migration) → WS3 (api handler)
WS1 → WS4 (frontend client) (can run in parallel with WS2)
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
- [ ] Every task is ≤ 2h work (or split)
- [ ] Every task has a Sad Path mitigation defined
- [ ] All Phase 2 gaps (F-ids and S-ids) trace directly to tasks
- [ ] Research Backlog has priority tags
- [ ] Full file is written, not just the digest

## Failure Modes (Anti-Patterns)

| Anti-Pattern | Why It Fails |
| ------------ | ------------ |
| Writing only the digest, skipping the full file | Phase 5 can't audit what doesn't exist |
| Tasks with vague verbs ("implement", "refactor") | No verification possible → scope creep |
| No exit criteria | "Done" is subjective → rushed PRs |
| Holding roadmap in memory until Phase 5 | Memory collapse → compressed details → wrong plan |
