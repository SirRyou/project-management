# How-To Guide: Deep Plan Recipes

This guide provides practical, task-oriented procedures for common planning and execution challenges using Deep Plan.

**Related docs:** [Tutorial](tutorial-deep-plan.md) | [Reference](reference-deep-plan.md) | [Explanation](explanation-deep-plan.md)

---

## 1. How to Initiate a Deep Plan Session

### Problem
You have a multi-file feature, architectural refactor, database migration, or security change that requires structured decomposition and coordinated execution.

### Procedure
1. **Ensure Repository Cleanliness:**
   Before planning, run preflight commands to verify the repository is in a clean state:
   ```bash
   git status --porcelain
   git log -1 --oneline
   ```
   If uncommitted changes or divergent branches exist, commit or stash them before proceeding.

2. **Trigger Deep Plan:**
   Invoke the agent with an epic-level objective:
   ```text
   Plan and execute the migration of our session storage to Redis with distributed locks.
   ```

3. **Capture Intent in `00-intent.md`:**
   The agent extracts the intent dossier into `.deep-plan/<epic-slug>/00-intent.md` containing:
   - Problem statement and underlying goal.
   - Desired behaviors and output artifacts.
   - Candidate system invariants.
   - Autonomy mode: `Collaborative` (requires user approval after planning) or `Autonomous` (proceeds after plan validation unless a boundary fork occurs).

4. **Run Entry Preflight & Complexity Triage:**
   If repository grounding later reveals the request is actually a simple single-file change or trivial tweak, present an explicit choice to the user:
   - **Option A:** Direct implementation (bypass full multi-tier planning).
   - **Option B:** Full Deep Plan lifecycle.
   Record the decision in `00-intent.md`.

---

## 2. How to Ground the Codebase and Build the Risk Register

### Problem
You need to map repository facts, dependencies, and potential hazards before authoring architecture.

### Procedure
1. **Map the Repository Architecture:**
   Use native repository mapping tools or dispatch the **Codebase Explorer** subagent. Instruct the Explorer to return file-and-line evidence for:
   - Framework conventions, database access patterns, and testing harnesses.
   - Blast radius: exact files and symbols that will be modified or referenced.
   - Existing test commands and coverage gaps.
   Persist this to `.deep-plan/<epic-slug>/01-grounding.md`.

2. **Construct the Risk Register:**
   Create `.deep-plan/<epic-slug>/02-risk-register.md` **before** designing architecture:
   - Enumerate technical risks across concurrency, security, data loss, and external dependencies.
   - Score each risk by **Impact** (High/Medium/Low) and **Uncertainty** (High/Medium/Low).
   - Require every High-impact or High-uncertainty risk to link to a mitigation strategy in Tier 2 architecture.

3. **Resolve External Unknowns:**
   If an external SDK or API behavior is uncertain, research its documentation immediately. If unresolved, schedule an explicit DAG research task (see [Recipe 11](#11-how-to-resolve-blocked-tasks-with-research-spikes)).

---

## 3. How to Author Three-Tier Planning Artifacts

### Problem
You need to produce clear, contract-ready specifications that workers can implement independently without cross-task confusion.

### Procedure
1. **Tier 1 — Scope & Invariants (`03-tier1-epic.md`):**
   - Use [tier1-epic-template.md](../skills/deep-plan/templates/tier1-epic-template.md).
   - Define strict, numbered invariants (e.g. `INV-1: Unhashed passwords are never written to disk`).
   - Define explicit in-scope and out-of-scope boundaries to prevent scope creep.

2. **Freeze the inter-module contract registry and the ID ledger — before any fan-out:**
   - Complete §6 of `03-tier1-epic.md`: one `C-xx` entry per cross-module contract, each naming its producer, its **explicit consumer list**, the ID it supersedes (or `None`), and the verbatim shape.
   - A frozen entry is **immutable**. To change a contract, file a **new** `C-xx` that names the ID it supersedes. Never append an amendment to a frozen entry — amendments accumulating against a "frozen" section are the exact failure this registry prevents.
   - Author `tasks/ID-LEDGER.md` (`T-id → slug → module → assigned range`) and freeze it. Name it `ID-LEDGER.md`, not `T00-*.md`, or the task-card glob will pick it up as a task.
   - Only then dispatch module architects. An architect fanned out against a moving contract writes against a snapshot that will drift, and the resulting contradictions are invisible to `validate`.

3. **Tier 2 — Architecture Contracts (`modules/M{n}-[name].md`):**
   - Dispatch the **System Architect** subagent for each logical module using [tier2-module-template.md](../skills/deep-plan/templates/tier2-module-template.md).
   - Define interface contracts, TypeScript types, database migration schemas, and sequence diagrams.
   - Specify module-level sad paths and error contracts (`SP-1`, `SP-2`).
   - Require each module to cite every cross-module contract it consumes by `C-xx` ID, and to **never assert another module's contract state** unless that module's artifact carries the same `C-xx`.
   - Do not ask a per-module architect to verify cross-module agreement; it cannot see its peers. That check belongs to the PM and the Plan Challenger.

4. **Tier 3 — Atomic Task Cards (`tasks/T{n}-[name].md`):**
   - Dispatch the **Task Decomposer** subagent using [tier3-task-template.md](../skills/deep-plan/templates/tier3-task-template.md).
   - Ensure each task represents **one independently verifiable change**. (File count is a heuristic; contract atomicity is the hard rule).
   - Declare the task kind, prerequisite tasks, exact file paths, ordered implementation steps, failure defenses, declared verification mode, and acceptance criteria.
   - Cite each cross-module prerequisite with its **slug as well as its ID** (`T11-localvadport`, not `T11`). The slug is a semantic handle: if a renumber later moves the ID, a mismatched slug at the citation site exposes it, where a bare ID stays silently plausible. Keep the DAG's `dependencies` ID-only.
   - **When fanning out multiple decomposers**, give each a disjoint task-ID range, forbid renumbering within a range another agent may have referenced, and forbid globbing `tasks/T*.md`. Concurrent writers into one `tasks/` directory have deleted each other's cards mid-edit and produced duplicates.

5. **Assemble the Dependency DAG (`dependency-dag.json`):**
   Declare tasks, module ownership, kind, and dependency IDs:
   ```json
   {
     "epic": "session-redis-migration",
     "tasks": [
       { "id": "T01", "module": "M01", "kind": "migration", "dependencies": [] },
       { "id": "T02", "module": "M01", "kind": "implementation", "dependencies": ["T01"] },
       { "id": "T03", "module": "M02", "kind": "implementation", "dependencies": ["T02"] }
     ]
   }
   ```
   Validate that the graph is acyclic and all referenced dependencies exist.

6. **Initialize the Progress Ledger:**
   Copy [progress-ledger-template.md](../skills/deep-plan/templates/progress-ledger-template.md) to `.deep-plan/<epic-slug>/progress-ledger.md`. Populate the task state matrix with all tasks initialized to `READY_TO_DISPATCH` (if 0 dependencies) or `BLOCKED` (if waiting on prerequisites).

---

## 4. How to Handle Architecture Forks and User Decisions

### Problem
During planning or plan challenge, an architectural decision arises that alters system boundaries, data ownership, or security trust boundaries.

### Procedure
1. **Recognize Boundary-Changing Forks:**
   A decision is a boundary-changing fork if it affects:
   - Module boundaries or service interfaces.
   - Data ownership or storage persistence guarantees.
   - Public API contracts or breaking changes.
   - External third-party providers or SDKs.
   - Security trust boundaries and permission models.
   - Irreversible database migration strategies.

2. **Pause Execution (Even in Autonomous Mode):**
   Do not assume or guess. Pause execution and invoke the structured question tool.

3. **Formulate the Decision:**
   Present the decision with:
   - Clear problem description.
   - Recommendation prefixed with `(Recommended)`.
   - Concrete options with explicit technical tradeoffs.
   ```text
   [Question] How should we store session state during failover?
   1. (Recommended) Hybrid Redis with local memory fallback (High availability, bounded memory).
   2. Pure Redis with hard error on disconnect (Strict consistency, potential outage during Redis downtime).
   ```

4. **Record the Decision:**
   Update `00-intent.md` and the relevant Tier 2 module specification with the user's choice before continuing.

---

## 5. How to Run Adversarial Plan Review (Phase 4 Gate)

### Problem
You have completed the draft plan (Tier 1, Tier 2, Tier 3, and DAG) and need to stress-test it against blind spots before writing code.

### Procedure
1. **Inspect the edges first:**
   Run `python "<skill-dir>/script/deep_plan.py" edges <epic-slug>` and read the cross-module list. It prints every edge beside its target's semantic handle, so a citation pointing at a renumbered ID is visible in one screen. It is a report, not a gate — it always exits `0`.

2. **Dispatch the Plan Challenger:**
   Invoke the **Plan Challenger** subagent using the `plan-challenge` contract. Supply the full planning bundle:
   - `00-intent.md`, `01-grounding.md`, `02-risk-register.md`, `03-tier1-epic.md`, all `modules/`, all `tasks/`, the `edges` report, and `dependency-dag.json`.

3. **Evaluate the Verdict:**
   The Challenger returns one of three verdicts:
   - **`PASS`:** All invariants are verifiable, dependencies are sound, and risks are mitigated. Proceed to Phase 5.
   - **`REVISE`:** Concrete findings identified (e.g. missing error handling, unverified invariant, circular dependency). The PM must update the affected task or module cards and re-run the challenge.
   - **`USER_DECISION_REQUIRED`:** A boundary-changing fork was uncovered. Follow [Recipe 4](#4-how-to-handle-architecture-forks-and-user-decisions).

4. **Enforce the Gate:**
   Never begin implementation with an unresolved material finding or an unapproved plan.

### The Four Checks That Catch Cross-Module Plan Corruption

These are criteria 10–14 in [plan-review.md](../skills/deep-plan/references/plan-review.md), called out separately because a real epic shipped with all four defects present and `validate` passing:

- **Cross-module contract agreement.** For every `C-xx`, do all listed consumers cite the same ID, and is any **superseded** ID still cited? Compare IDs and acknowledgement cells, not prose. A citation that exists but points at a superseded contract is the defect, and an existence check cannot see it.
- **Semantic ID drift.** Does every prerequisite citation's slug match its target card's filename stem? `T11-localvadport` resolving to a card named `capabilities-card` means the ID was renumbered after the citation was written. The DAG stays acyclic, resolvable, and wrong. `deep_plan.py edges` reports this as citation drift; bare-ID citations are printed but not checked.
- **Test integrity.** Does the test configuration exclude the correct paths? Are stale copies — worktrees, build output — reachable from a repo-wide run? A suite that runs stale code reports green while the real tree is red.
- **Silent data loss.** Does any design path discard, truncate, or reorder data without emitting a signal? Capped buffers that drop the *oldest* input are the canonical case: the result is committed and plausible, merely missing its beginning.

---

## 6. How to Select and Configure Verification Modes

### Problem
Different software tasks require different proof mechanisms. Universal TDD does not fit database migrations, documentation, or static configurations.

### Procedure
In each Tier 3 task card, set `Verification Mode` to one of the following:

| Verification Mode | Best Suited For | Required Verification Procedure |
| :--- | :--- | :--- |
| **`behavioral-tdd`** | Business logic, API routes, utilities | 1. Write failing unit/integration test demonstrating missing behavior.<br>2. Implement minimal code to pass.<br>3. Verify test passes and run linters. |
| **`migration`** | Schema changes, data transforms | 1. Verify pre-migration schema.<br>2. Apply migration up.<br>3. Test schema constraints and data integrity.<br>4. Apply migration down and verify clean rollback. |
| **`static-config`** | CI/CD, TypeScript configs, env schemas | 1. Run schema validation or linter (`tsc --noEmit`, JSON schema check).<br>2. Verify generated build artifacts. |
| **`documentation`** | API docs, user guides, changelogs | 1. Validate all Markdown links.<br>2. Test runnable code examples.<br>3. Verify formatting and table rendering. |
| **`benchmark`** | Performance-critical paths, caching | 1. Capture reproducible pre-change baseline.<br>2. Execute post-change measurement.<br>3. Verify latency/throughput meets declared budget. |
| **`repository-specific`** | Custom compilation, container builds | Follow the repository's documented build and verification commands. |

Ensure the task's `Verification Command(s)` contains the exact shell commands required to prove the outcome.

---

## 7. How to Execute Tasks with Workers in Isolated Worktrees

### Problem
You need to implement ready tasks without contaminating the parent branch or creating merge collisions.

### Procedure
1. **Identify Ready Tasks:**
   Check `progress-ledger.md` and `dependency-dag.json`. A task is ready only when all prerequisite tasks have an integrated commit on the parent branch.

2. **Create an Isolated Worktree:**
   ```bash
   git worktree add .worktrees/T01 -b task/T01-feature-name
   ```

3. **Dispatch Worker Implementer:**
   Supply the worker with:
   - Tier 3 task path (`tasks/T01-*.md`).
   - Parent Tier 2 module path.
   - Target files and declared verification mode.
   - Parent branch integration target.

4. **Worker Execution Rules:**
   - Worker implements the change strictly within the task's declared scope.
   - Worker runs the declared verification commands in the isolated worktree.
   - Worker creates **one clean commit** on the task branch.
   - Worker **never** merges directly into the parent branch.
   - Worker reports back the commit SHA, modified files, and verification evidence.

---

## 8. How to Audit Worker Commits with Multi-Axis Reviews

### Problem
A worker has submitted a commit. You must ensure it meets quality standards, conforms to specifications, and does not break invariants before integration.

### Procedure
1. **Transition Ledger State:**
   Update the task status in `progress-ledger.md` to `IN_REVIEW`.

2. **Dispatch Code Auditor (Parallel Dual-Axis Review):**
   The **Code Auditor** subagent reviews the exact commit SHA across two axes:
   - **Standards Axis:** Coding style, repository linting rules, naming conventions, maintainability.
   - **Spec Axis:** Strict conformance to Tier 3 acceptance criteria, preserving target boundaries, avoiding unrequested logic.
   Both axes must return `PASS`.

3. **Dispatch Adversarial Challenger:**
   The **Adversarial Challenger** subagent probes the commit:
   - Does this code threaten any Tier 1 system invariant?
   - Are failure modes and timeouts handled or silently swallowed?
   - Do tests meaningfully assert real behavior or just tautological mocks?
   Must return `PASS`.

4. **Dispatch Specialists When Activated:**
   - If the task touched auth/PII, dispatch **Security Auditor**.
   - If tagged `perf`, dispatch **Performance Benchmarker**.

5. **Review Gate:**
   Integration is authorized **only** when all required review axes return `PASS`.

---

## 9. How to Handle Review Failures and Bounded Remediation

### Problem
A review axis returned `FAIL` (e.g., Code Auditor found missing input validation, or Challenger identified an unhandled error state).

### Procedure
1. **Update Ledger:**
   Mark task status as `IN_REMEDIATION` and increment `Remediation Count` in `progress-ledger.md`.

2. **Check Remediation Limit:**
   Compare count against configured maximum (default: 2 retries):
   - If `count <= limit`: Proceed to step 3.
   - If `count > limit`: Mark task as `BLOCKED` or `FAILED`. Stop execution, log remediation history, and escalate to the user with actionable findings.

3. **Dispatch Focused Remediation:**
   Send the worker:
   - Reviewer findings with exact file paths and symbol references.
   - Required remediation instructions.
   The worker updates the commit in the worktree and re-runs verification.

4. **Re-Run Review:**
   Transition status back to `IN_REVIEW` and re-run all failing review axes.

---

## 10. How to Integrate Approved Commits and Verify the Parent Tree

### Problem
All reviewers have passed the worker commit. You must safely merge it into the parent branch and verify the integrated state.

### Procedure
1. **Set Status to `INTEGRATING`:**
   Update `progress-ledger.md`.

2. **Merge into Parent Branch:**
   Using the explicit merge seam, pull the commit into the parent branch:
   ```bash
   git merge --ff-only <worker_commit_sha>
   ```

3. **Run Integrated-Tree Verification:**
   Execute regression tests and affected checks directly on the parent branch:
   ```bash
   npm test
   ```

4. **Record Completion & Unlock Dependents:**
   - Record the integrated commit SHA and test output in `progress-ledger.md`.
   - Transition status to `COMPLETED`.
   - Remove the task worktree:
     ```bash
     git worktree remove .worktrees/T01
     ```
   - Evaluate `dependency-dag.json`. For each task whose prerequisites are now all `COMPLETED`, transition status from `BLOCKED` to `READY_TO_DISPATCH`.

---

## 11. How to Pause, Checkpoint, and Resume Execution

### Problem
Execution needs to pause due to quota exhaustion, end-of-day stop, fatigue, or session interruption.

### Procedure
1. **Gracefully Pause the Epic:**
   Prompt the agent to pause or run the CLI (located at `<skill-dir>/script/deep_plan.py`):
   ```bash
   python "<skill-dir>/script/deep_plan.py" pause <epic-slug> \
     --reason quota \
     --note "Worker finished step 2, ready for verification" \
     --task-progress T03:2:5
   ```
   *Note: Ensure any active in-flight worker commits pending changes as a WIP commit (`git commit -m "wip(T{n}): step X/Y - <summary>"`) in its worktree before pausing so uncommitted files are preserved.*
   
   This snapshots parent Git state, records task step progress, populates Section 5 of `progress-ledger.md`, and generates a timestamped dossier at `.deep-plan/<epic-slug>/handoff/HANDOFF-YYYY-MM-DDTHHMM.md`.

2. **Resume and Reconcile in a New Session:**
   In the new session, prompt the agent:
   ```text
   Resume execution of epic <epic-slug>.
   ```
   The PM agent executes:
   ```bash
   python "<skill-dir>/script/deep_plan.py" resume <epic-slug>
   ```
   The CLI verifies that parent branch HEAD matches the recorded checkpoint, reconciles in-flight worktrees (detecting commits and step progress), reports pending reviews, lists dispatchable tasks, and prints an actionable briefing.

3. **Continue Dispatch Loop:**
   Follow the briefing's recommended actions (e.g. advance completed commits to review, continue next implementation steps, or dispatch newly unblocked tasks) without re-planning or repeating completed tasks.

---

## 12. How to Resolve Blocked Tasks with Research Spikes

### Problem
A task cannot proceed because third-party library behavior or undocumented API responses are unknown.

### Procedure
1. **Insert a Research Task into the DAG:**
   Update `dependency-dag.json` to insert a research task with a stable `research_id`:
   ```json
   {
     "id": "T05",
     "module": "M02",
     "kind": "research",
     "research_id": "R01",
     "dependencies": []
   }
   ```
   Update downstream implementation tasks to depend on `T05`.

2. **Dispatch Researcher Subagent:**
   Dispatch the **Researcher** subagent using contract `research-spike`. The Researcher probes library docs, runs prototype spikes, and writes `.deep-plan/<epic-slug>/research/R01-spike-report.md`.

3. **Unblock Implementation:**
   The PM records findings, marks `T05` as `COMPLETED`, updates downstream task cards with concrete API signatures, and transitions dependent tasks to `READY_TO_DISPATCH`.

---

## 13. How to Conduct Final Epic Verification and Closeout

### Problem
All tasks in the DAG are `COMPLETED`. You need to ensure the overall epic satisfies all Tier 1 requirements and clean up the environment.

### Procedure
1. **Run Global Verification:**
   Execute full repository checks on the parent branch:
   ```bash
   npm run lint
   npm test
   npm run build
   ```

2. **Audit Tier 1 Invariants:**
   Cross-check each invariant in `03-tier1-epic.md` (`INV-1`, `INV-2`, etc.) against completion evidence recorded in `progress-ledger.md`. Confirm no invariant was violated or left unverified.

3. **Dispatch Documentation Writer (If Applicable):**
   If public APIs, configuration keys, or migrations were modified, dispatch the **Documentation Writer** subagent to update READMEs, API docs, and CHANGELOG entries.

4. **Clean Up Worktrees & Branches:**
   ```bash
   git worktree prune
   git branch -d $(git branch --list 'task/*')
   ```

5. **Provide Completion Summary:**
   Deliver the requirement-to-proof summary to the user, referencing all integrated commits and verification evidence.
