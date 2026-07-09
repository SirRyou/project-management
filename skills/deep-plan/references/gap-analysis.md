# Reference: Gap Analysis (Step 3)

This reference document guides the agent through Step 3 (Adversarial Gap Enumeration) of the `deep-plan` workflow, including the Generic Planning Standard fallback.

---

## Step 3 — Adversarial Gap Enumeration (Agent)

For each item in scope, run all three lenses. **Run all three lenses in parallel per item** — they're independent analyses and don't depend on each other's output.

### Quick-Skip Rule
If an item clearly has no security surface (e.g., pure internal formatting logic, UI-only cosmetic changes, documentation updates), write one line: `No security surface — reason: [why]` and skip Lens 3 for that item. Do NOT skip Lens 1 or Lens 2 — every item needs problem-fit and resilience analysis.

### Focus Rule
Spend proportional effort based on risk level:
- **CRITICAL/HIGH items**: Full three-lens analysis with detailed tables.
- **MEDIUM items**: Condensed analysis — focus on the most likely failure mode and top security risk.
- **LOW items**: One-liner verdict per lens unless something unexpected surfaces.

### 3A. Problem-Fit Check (Lens 1)

```markdown
### Problem-Fit: [Item Name]
- Literal ask: [what was requested]
- Underlying goal: [what actually needs to be true for the user]
- Gap: [does the literal ask fully close that gap? if not, what's missing?]
- Verdict: FIT / PARTIAL FIT (missing: ...) / MISFIT (solves wrong thing)
```

Mark any PARTIAL FIT or MISFIT as requiring a scope conversation before Step 4 — either add a task, or explicitly note it as accepted debt in the scope brief.

### 3B. Failure Mode Table (Lens 2)

```markdown
### [Item Name] — Failure Modes

| # | Failure Mode | Trigger | Impact | Standard §Ref |
|---|-------------|---------|--------|----------------------|
| F1 | [what fails] | [what causes it] | [what breaks] | §1.3 |
```

Cross-reference the resolved standard from Step 1A. Name known patterns explicitly (rate limit, timeout, abort race, resource leak, context overflow, retry storm, partial write).

### 3C. Security Risk Table (Lens 3)

For every item that touches external input, auth, cross-tenant/cross-user state, secrets, or third-party calls:

```markdown
### [Item Name] — Security Risks

| # | Risk | Trust Boundary Crossed | Adversarial Trigger | Impact | Standard §Ref |
|---|------|------------------------|----------------------|--------|----------------------|
| S1 | [what could be abused/leaked] | [where] | [what a malicious actor would send/do] | [blast radius] | §7.2 |
```

If an item genuinely has no security surface (e.g. pure internal formatting logic), write one line: `No security surface — reason: [why]`. Don't leave it silently blank.

### 3D. Invariant & Boundary Violation Check

For each invariant and trust boundary from Step 2A, ask:
- Which failure modes (3B) or security risks (3C) could violate/cross it silently — no error, no log, no audit trail?

Mark silent violations as **CRITICAL** — highest-priority tasks.

### 3E. Categorize by Work Stream

Cluster problem-fit gaps, failure modes, and security risks into natural work stream groupings. Don't force it — let items self-organize. Typical clusters: Tool/execution, Lifecycle/async, State/data integrity, Provider/network, Auth/trust-boundary, Type/schema, Scope/UX gaps.

---

## Generic Planning Standard (3-Lens Fallback)

Use this planning standard if no project-specific planning standards document is found in Step 1A:

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
