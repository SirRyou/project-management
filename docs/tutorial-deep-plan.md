# Tutorial: End-to-End Planning and Execution with Deep Plan

In this tutorial, you will learn how to use Deep Plan to take a non-trivial feature from initial concept through repository grounding, tiered planning, adversarial plan review, isolated swarm execution, multi-axis review, tree integration, and final verification.

By the end of this tutorial, you will understand how Deep Plan orchestrates planning artifacts, enforces verification gates, and maintains an unbroken chain of evidence from user intent to working code.

**Related docs:** [How-To Guide](howto-deep-plan.md) | [Reference](reference-deep-plan.md) | [Explanation](explanation-deep-plan.md)

---

## What You'll Build

You will walk through a realistic, multi-file feature: **API Key Authentication with Tiered Rate Limiting and Token Invalidation** for a backend service. This feature spans:

- A database schema migration for API keys and usage counters.
- Core authentication middleware enforcing key validity and invariant checks.
- Rate-limiting middleware with Redis caching and in-memory fallbacks.
- Key revocation and administrative endpoints.

This requires careful dependency sequencing, multi-file coordination, database mutations, and security trust-boundary handling—making it an ideal candidate for Deep Plan.

---

## Prerequisites

- An AI coding agent supporting tool use (such as Claude Code, Codex, or Gemini CLI / Antigravity).
- Git installed on your system.
- 20 minutes to complete the walk-through.

---

## Step 1: Project Setup and Baseline Context

To ground our walk-through in concrete code, establish a sample project repository with a basic API layout:

```bash
mkdir auth-service
cd auth-service
git init
git config user.name "Tutorial Developer"
git config user.email "developer@example.com"

# Create a baseline package structure
mkdir -p src/middleware src/routes src/db
cat << 'EOF' > README.md
# Auth Service
Sample microservice with REST endpoints.
EOF

cat << 'EOF' > src/db/schema.sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF

cat << 'EOF' > src/server.js
const express = require('express');
const app = express();
app.use(express.json());

app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

module.exports = app;
EOF

git add .
git commit -m "chore: initial project layout"
```

Verify your repository is clean:

```bash
git status --porcelain
```

---

## Step 2: Phase 1 — Intent Capture and Entry Preflight

Deep Plan begins when you give your agent a complex, multi-file request. You trigger it with a feature prompt:

```text
User: We need to add API key authentication with tiered rate limiting and token revocation to our API.
```

The agent activates Deep Plan. As PM / Orchestrator, it does not immediately start writing code. Instead, it runs an **entry preflight** and infers communication depth from your request:

```text
Agent: Activating Deep Plan for API Key Authentication & Rate Limiting.
       Preflight check: Git working tree is clean on branch 'master'.
       Running Phase 1: Intent and Entry Preflight.
```

The agent extracts your core requirements into `.deep-plan/api-key-auth/00-intent.md`:

```markdown
# Intent Dossier: API Key Authentication & Rate Limiting

## 1. Problem Statement
External clients require programmatic access via API keys with tier-based rate limits and instant revocation.

## 2. Desired Behaviors & Outputs
- Secure hashing of API keys (SHA-256 with key prefixes).
- Per-request rate limiting (Free tier: 60 req/min, Pro tier: 600 req/min).
- Immediate invalidation upon revocation.
- Standardized 401 Unauthorized and 429 Too Many Requests HTTP responses.

## 3. Candidate Invariants
- INV-1: Plaintext API keys are never stored in the database or logged.
- INV-2: Revoked keys must fail authentication immediately across all instances.
- INV-3: Rate limit state mutations must never block authentication under Redis failure.

## 4. Operational Context
- Autonomy Mode: Collaborative (user confirms plan before execution).
- Provisional Complexity: High (schema mutation, auth boundary, caching dependency).
- Unresolved Decisions: Rate limit fallback policy when Redis is unavailable.
```

Because the Redis fallback choice materially impacts architecture, the agent presents a focused question with concrete options, a recommendation, and explicit tradeoffs:

```text
Agent: [Question] When Redis is unreachable, should rate limiting fail open (allow requests) or fall back to an in-memory sliding window?
       1. (Recommended) Fall back to local in-memory sliding window (preserves availability while bounding abuse).
       2. Fail open (maximum availability, but allows unbounded requests).
       3. Fail closed (blocks requests, but risks self-inflicted outage).

User: 1
```

The agent records the decision in `00-intent.md` and advances to Phase 2.

---

## Step 3: Phase 2 — Repository Grounding, Gaps, and Risks

Next, the PM orchestrator maps existing repository facts before designing architecture. It dispatches the **Codebase Explorer** subagent to inspect the repository:

```text
Agent: Dispatching Codebase Explorer to ground architecture and blast radius...
```

The Explorer examines `src/db/schema.sql`, `src/server.js`, and existing dependencies, returning file-and-line evidence. The agent writes `.deep-plan/api-key-auth/01-grounding.md`:

```markdown
# Grounding Dossier: API Key Authentication

## 1. Stack & Conventions
- Runtime: Node.js / Express.
- Persistence: SQL (`src/db/schema.sql`).
- Test Framework: Jest configured via `package.json`.

## 2. File Map & Blast Radius
- `src/db/schema.sql` (schema expansion)
- `src/middleware/auth.js` (new middleware)
- `src/middleware/rate-limit.js` (new middleware)
- `src/routes/keys.js` (new management routes)
- `src/server.js` (mounts middleware and routes)

## 3. Known Facts vs. Unknowns
- Fact: No existing auth middleware or session mechanism is present.
- Unknown: Redis client library choice and connection pooling behavior.
```

With grounding established, the PM builds the **Risk Register** at `.deep-plan/api-key-auth/02-risk-register.md` before any architecture is designed:

```markdown
# Risk Register: API Key Authentication

| ID | Risk Description | Impact | Uncertainty | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **R01** | Redis outage causes auth cascading failure | HIGH | MEDIUM | In-memory sliding window fallback (Tier 2 contract) |
| **R02** | Key generation entropy vulnerability | HIGH | LOW | Use `crypto.randomBytes(32)` with checksum prefix |
| **R03** | Race condition on rate limit counter increments | MEDIUM | LOW | Atomic Redis Lua script or in-memory lock |
```

---

## Step 4: Phase 3 — Tiered Planning and Dependency DAG

With intent, grounding, and risks locked, the agent initiates **Tiered Planning**. It generates three linked layers of specifications plus the dependency graph.

### Tier 1: Epic Scope and Invariants

The agent creates `.deep-plan/api-key-auth/03-tier1-epic.md` using [tier1-epic-template.md](../skills/deep-plan/templates/tier1-epic-template.md):

```markdown
# Tier 1: Epic Overview & Invariants — API Key Auth

## 1. System Invariants
- **INV-1:** Raw key secrets exist only at generation time; database stores only salted SHA-256 digests.
- **INV-2:** Revocation status is checked on every authenticated request.
- **INV-3:** Downstream rate-limiting failures degrade gracefully to local memory without throwing 500 errors.

## 2. Scope Boundaries
- **In-Scope:** Database migration, API key generation & validation, tiered rate limiting, revocation endpoint.
- **Out-of-Scope:** OAuth2/OIDC integration, billing tier payment integration, frontend UI management console.

## 3. Module Topology
`M01-data-model` -> `M02-auth-core` -> `M03-rate-limiter` -> `M04-key-routes`
```

### Tier 2: Module Architecture Contracts

The **System Architect** subagent authors detailed specifications in `modules/`:
- `modules/M01-data-model.md`: API key schema, status enums (`active`, `revoked`), indexing on key hashes.
- `modules/M02-auth-core.md`: Key extraction header contract (`X-API-Key`), validation function, error format.
- `modules/M03-rate-limiter.md`: Redis counter logic with in-memory fallback adapter.
- `modules/M04-key-routes.md`: `POST /api/keys` (generate) and `DELETE /api/keys/:id` (revoke).

### Tier 3: Atomic Task Cards and Dependency DAG

The **Task Decomposer** slices each module into atomic tasks under `tasks/` using [tier3-task-template.md](../skills/deep-plan/templates/tier3-task-template.md):
- `tasks/T01-key-schema-migration.md` (`kind: migration`, `verification_mode: migration`)
- `tasks/T02-key-validator-core.md` (`kind: implementation`, `verification_mode: behavioral-tdd`)
- `tasks/T03-rate-limiting-middleware.md` (`kind: implementation`, `verification_mode: behavioral-tdd`)
- `tasks/T04-key-management-endpoints.md` (`kind: implementation`, `verification_mode: behavioral-tdd`)

The Decomposer outputs `.deep-plan/api-key-auth/dependency-dag.json`:

```json
{
  "epic": "api-key-auth",
  "tasks": [
    { "id": "T01", "module": "M01", "kind": "migration", "dependencies": [] },
    { "id": "T02", "module": "M02", "kind": "implementation", "dependencies": ["T01"] },
    { "id": "T03", "module": "M03", "kind": "implementation", "dependencies": ["T02"] },
    { "id": "T04", "module": "M04", "kind": "implementation", "dependencies": ["T02"] }
  ]
}
```

Notice that T03 (rate limiting) and T04 (key endpoints) both depend on T02 (key validation), but are independent of each other.

The PM initializes the **Progress Ledger** at `.deep-plan/api-key-auth/progress-ledger.md` using [progress-ledger-template.md](../skills/deep-plan/templates/progress-ledger-template.md):

```markdown
# Swarm Execution Ledger

## 1. Task Execution State Matrix

| Task ID | Module | Dependencies | Worker Worktree | Worker Commit | Integrated Commit | Verification | Code Auditor | Challenger | Status | Remediation Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **T01** | M01 | None | — | — | — | — | — | — | **READY_TO_DISPATCH** | 0 |
| **T02** | M02 | T01 | — | — | — | — | — | — | **BLOCKED** | 0 |
| **T03** | M03 | T02 | — | — | — | — | — | — | **BLOCKED** | 0 |
| **T04** | M04 | T02 | — | — | — | — | — | — | **BLOCKED** | 0 |
```

---

## Step 5: Phase 4 — Adversarial Plan Review

Before writing any code, Deep Plan subjects the plan to adversarial review. The PM dispatches the **Plan Challenger** subagent:

```text
Agent: Dispatching Plan Challenger with contract 'plan-challenge'...
```

The Plan Challenger stress-tests the plan against scope drift, unsupported assumptions, unmitigated risks, and verification feasibility. It returns:

```markdown
### Plan Challenge: API Key Authentication
- **Verdict:** REVISE
- **Findings:**
  1. `tasks/T03-rate-limiting-middleware.md`: Does not define a verification test for Redis connection drop. Invariant INV-3 cannot be proven by the declared test command.
- **Required Changes:**
  1. Add a simulated network partition test case to T03 acceptance criteria and verification commands.
- **User Decisions:** None (no boundary-changing architecture fork).
```

The PM updates `tasks/T03-rate-limiting-middleware.md` to include explicit failure simulation in its verification steps. Upon re-evaluating, the Plan Challenger issues a **PASS**:

```markdown
### Plan Challenge: API Key Authentication
- **Verdict:** PASS
- **Findings:** None. All invariants mapped to verifiable acceptance criteria.
- **Required Changes:** None.
```

---

## Step 6: Phase 5 — Finalize and Approve the Plan

The PM validates the DAG for acyclicity, ensures all task files exist, and presents the plan for confirmation:

```text
Agent: Phase 5: Plan Finalization & Approval Gate.
       Plan summary:
       - 4 atomic tasks spanning 4 modules.
       - 3 system invariants protected by explicit verification contracts.
       - Plan Challenger verdict: PASS.

       Collaborative mode active: Please confirm to proceed with execution.
       Options:
       1. (Recommended) Approve and start isolated worker execution.
       2. Request revisions to specific tasks.
       3. Cancel planning.

User: 1
Agent: Plan approved. Transitioning to Swarm Execution.
```

---

## Step 7: Swarm Execution — Worker Dispatch in an Isolated Worktree

Execution strictly follows the DAG. Only tasks with status `READY_TO_DISPATCH` are scheduled.

T01 has no prerequisites. The PM marks T01 as `IN_PROGRESS` in the ledger, creates an isolated git worktree, and dispatches the **Worker Implementer**:

```bash
git worktree add .worktrees/T01 -b task/T01-key-schema
```

The PM provides the Worker with the invocation envelope:
- Tier 3 Task Card: `.deep-plan/api-key-auth/tasks/T01-key-schema-migration.md`
- Verification Mode: `migration`
- Verification Commands: `npm run migrate:up && npm run test:migration`

The Worker writes the migration file in the isolated worktree, executes the verification commands, commits the change, and reports back:

```markdown
### Worker Execution Summary: T01
- **Status:** COMPLETED
- **Commit SHA:** `a7b3c91`
- **Files Modified:** `src/db/migrations/20260919_api_keys.sql`, `tests/migrations/api_keys.test.js`
- **Verification Mode:** `migration`
- **Verification Evidence:** `npm run test:migration` returned exit code 0 (schema validated, rollback verified).
- **Notes:** Added index on `key_hash` as mandated by M01 contract.
```

---

## Step 8: Multi-Axis Review — Code Auditor and Adversarial Challenger

Before merging `a7b3c91`, the PM transitions T01 to `IN_REVIEW` and runs two independent review roles in parallel:

### 1. Code Auditor Subagent
Audits the worker commit on two separate axes:
- **Standards Axis:** Coding style, repository linting rules, documentation conventions.
- **Spec Axis:** Strict conformance to Tier 3 task requirements without omissions or scope creep.

```markdown
### Code Audit: T01
- **Standards Verdict:** PASS
  - Findings: SQL syntax adheres to project standards.
- **Spec Verdict:** PASS
  - Findings: Table schema and indices match M01 specification exactly.
- **Blocking Findings:** None
```

### 2. Adversarial Challenger Subagent
Probes for silent failures, race conditions, and invariant violations:

```markdown
### Adversarial Challenger Verdict: PASS
- **Task:** T01
- **Invariant Impact:** Preserved. `raw_key` column is omitted; only `key_hash` exists (satisfies INV-1).
- **Vulnerabilities / Silent Failures:** None.
- **Edge Cases Unhandled:** None.
```

Both reviews pass.

---

## Step 9: Integration Gate and Integrated-Tree Verification

The PM does not consider T01 complete simply because the worker's branch passed. The change must be integrated into the parent tree and verified there:

1. **Integrate:** Merge the worker commit into the parent branch:
   ```bash
   git merge --ff-only a7b3c91
   ```
2. **Verify Integrated Tree:** Run repository regression tests on the merged branch:
   ```bash
   npm test
   ```
3. **Record Evidence & Unlock:**
   The PM records the integrated commit SHA `a7b3c91` in `progress-ledger.md`, marks T01 as `COMPLETED`, and evaluates the DAG.
   Because T01 is completed and integrated, **T02 is now unlocked and marked `READY_TO_DISPATCH`**.

```markdown
| Task ID | Status | Integrated Commit | Verification | Code Auditor | Challenger |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **T01** | **COMPLETED** | `a7b3c91` | PASS | PASS | PASS |
| **T02** | **READY_TO_DISPATCH** | — | — | — | — |
```

---

## Step 10: Handling a Session Pause and Resume

Suppose your session runs out of tokens or you need to restart your IDE while working on T02. How does Deep Plan resume without losing context?

When the new session begins, prompt the agent:

```text
User: Continue with the api-key-auth epic.
```

The agent runs the **Resume Protocol**:
1. Reads `.deep-plan/api-key-auth/progress-ledger.md` to inspect the state machine.
2. Reads `dependency-dag.json` and checks git status (`git status --porcelain`, `git log -1`).
3. Confirms T01 is integrated at `a7b3c91`.
4. Identifies that T02 is marked `READY_TO_DISPATCH`.

```text
Agent: Resuming epic 'api-key-auth' from ledger checkpoint.
       Last completed task: T01 (commit a7b3c91 integrated).
       Current ready task: T02 (Key Validator Core).
       Dispatching Worker Implementer for T02...
```

The workflow resumes cleanly without repeating Phase 1-5 planning or re-running T01.

---

## Step 11: Final Epic Verification and Proof Summary

After all tasks (T01 through T04) pass worker verification, Code Auditor review, Adversarial Challenger review, and tree integration, the PM initiates **Final Epic Verification**:

1. Runs full project verification:
   ```bash
   npm run lint
   npm test
   npm run build
   ```
2. Audits implementation against all Tier 1 invariants:
   - **INV-1 Check:** Verified by `tests/auth.test.js` (hash stored; plaintext rejected in logs).
   - **INV-2 Check:** Verified by `tests/revocation.test.js` (immediate 401 on revoked key).
   - **INV-3 Check:** Verified by `tests/rate-limit.test.js` (fallback memory limiter activates when Redis mock times out).
3. If public documentation is affected, invokes the **Documentation Writer** subagent to update API documentation.
4. Cleans up isolated worktrees (`git worktree prune`).
5. Presents the final proof summary to the user:

```text
Agent: Epic 'api-key-auth' is COMPLETED and verified.
       - All 4 tasks completed and integrated into master.
       - Invariant Audit: INV-1, INV-2, INV-3 proven passing.
       - Evidence Trail: Fully preserved in .deep-plan/api-key-auth/
```

---

## What You Learned

In this tutorial, you experienced:
1. **Preflight and Intent Capture:** How Deep Plan captures requirements in `00-intent.md` and isolates material decisions early.
2. **Grounding and Risk Analysis:** Why exploring the codebase and building `02-risk-register.md` precedes architectural decisions.
3. **Three-Tier Architecture:** How Tier 1 invariants, Tier 2 module contracts, and Tier 3 atomic tasks maintain clarity across abstraction levels.
4. **Adversarial Plan Challenge:** How the Plan Challenger spots missing failure tests before implementation begins.
5. **Worktree Isolation and Multi-Axis Reviews:** Why workers develop in isolated worktrees and undergo both Standards/Spec and Adversarial review.
6. **Parent-Tree Integration:** Why code is only complete after integrating and passing tests on the target branch.
7. **Ledger Resiliency:** How the external progress ledger allows seamless resumption after session boundaries.

## Next Steps

- Consult the [How-To Guide](howto-deep-plan.md) for targeted recipes on handling architecture forks, choosing verification modes, and managing bounded remediation.
- Read the [Reference](reference-deep-plan.md) for full schemas of `dependency-dag.json`, ledger states, and subagent invocation contracts.
- Review the [Explanation](explanation-deep-plan.md) to understand the theoretical principles behind Deep Plan's architecture.
