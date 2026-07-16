# Reference: Gap Analysis (Phase 2)

Guides the agent through Phase 2 (Enumerate Gaps) of the deep-plan workflow, including the generic planning standard fallback.

---

## Phase 2 — Adversarial Gap Enumeration

For each item in scope, run all three lenses. **Run all three lenses in parallel per item** — they're independent analyses.

### Quick-Skip Rule

If an item clearly has no security surface (e.g., pure internal formatting logic, UI-only cosmetic changes, documentation updates), write one line: `No security surface — reason: [why]` and skip Lens 3 for that item. Do NOT skip Lens 1 or Lens 2 — every item needs problem-fit and resilience analysis.

### Focus Rule

Spend proportional effort based on risk level:

- **CRITICAL/HIGH items**: Full three-lens analysis with detailed tables.
- **MEDIUM items**: Condensed analysis — focus on the most likely failure mode and top security risk.
- **LOW items**: One-liner verdict per lens unless something unexpected surfaces.

### 2A. Problem-Fit Check (Lens 1)

```markdown
### Problem-Fit: [Item Name]
- Literal ask: [what was requested]
- Underlying goal: [what actually needs to be true for the user]
- Gap: [does the literal ask fully close that gap? if not, what's missing?]
- Verdict: FIT / PARTIAL FIT (missing: ...) / MISFIT (solves wrong thing)
```

Mark any PARTIAL FIT or MISFIT as requiring a scope conversation before Phase 3 — either add a task, or explicitly note it as accepted debt in the scope brief.

### 2B. Failure Mode Table (Lens 2)

```markdown
### [Item Name] — Failure Modes

| # | Failure Mode | Trigger | Impact |
|---|-------------|---------|--------|
| F1 | [what fails] | [what causes it] | [what breaks] |
```

Name known patterns explicitly (rate limit, timeout, abort race, resource leak, context overflow, retry storm, partial write).

### 2C. Security Risk Table (Lens 3)

For every item that touches external input, auth, cross-tenant/cross-user state, secrets, or third-party calls:

```markdown
### [Item Name] — Security Risks

| # | Risk | Trust Boundary Crossed | Adversarial Trigger | Impact |
|---|------|------------------------|----------------------|--------|
| S1 | [what could be abused/leaked] | [where] | [what a malicious actor would send/do] | [blast radius] |
```

If an item genuinely has no security surface, write one line: `No security surface — reason: [why]`. Don't leave it silently blank.

### 2D. Invariant & Boundary Violation Check

For each invariant and trust boundary from Phase 1, ask:

- Which failure modes (2B) or security risks (2C) could violate/cross it silently — no error, no log, no audit trail?

Mark silent violations as **CRITICAL** — highest-priority tasks.

### 2E. Categorize by Work Stream

Cluster problem-fit gaps, failure modes, and security risks into natural work stream groupings. Don't force it — let items self-organize. Typical clusters: Tool/execution, Lifecycle/async, State/data integrity, Provider/network, Auth/trust-boundary, Type/schema, Scope/UX gaps.

---

## Generic Planning Standard (3-Lens Fallback)

Use this if no project-specific planning standards document is found in Phase 1:

```
LENS 1 — PROBLEM-FIT
Before any failure mode work: is this plan solving the underlying problem, or
just implementing the literal request? Ask: "If I ship exactly what was asked
and nothing more, does the user's actual goal get met?" A request can be
technically satisfied and still miss the point (e.g. "add a retry button" when
the real problem is the request times out silently). Flag any place the plan
optimizes for "answered the question" over "solved the problem."

LENS 2 — RESILIENCE
Engineers naturally design for success. Every task must be interrogated: "What
if this fails? What if it's slow? What if it's called twice? What if the input
is malformed? What if the downstream is down? What if it's interrupted
mid-operation?" If you can't answer these, the task isn't ready to be planned.

LENS 3 — SECURITY
Every task that touches external input, auth, state shared across users/tenants,
or third-party services must be interrogated: "Who can trigger this, and what do
they need to know/have? What happens if the input is adversarial, not just
malformed? Does this expose secrets, PII, or internal state in logs/errors/
responses? Does this cross a trust boundary (user input → command, user input →
query, agent output → executed code)? Is there a permission check, or is it
assumed?" A plan with no security-relevant tasks for anything touching input,
auth, or third-party integration should be treated as incomplete, not clean.
```
