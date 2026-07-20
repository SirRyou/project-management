# Reference: Gap Analysis (Phase 2)

Guides the agent through Phase 2 (Adversarial Gap Enumeration) of the deep-plan workflow.

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
- Verdict: [FIT | PARTIAL_FIT | MISFIT] — missing: [description or N/A]
- Invariant Impact: [Preserved | Threatened: state invariant broken]
```

Mark any PARTIAL FIT or MISFIT as requiring a scope conversation before Phase 3 — either add a task, or explicitly note it as accepted debt in the scope brief.

### 2A-bis. Blocker Check (run alongside 2A, every item)

This is a separate axis from the FIT verdict above — an item can be a clean FIT and still be a `BLOCKER`. Ask, per item:

> Can this item actually be executed right now with what's currently accessible — credentials, env vars, a third-party service that needs enabling, infra/DNS that needs provisioning, an access grant that needs approval?

If no:

```markdown
### Blocker: [Item Name]
- Blocked by: [the specific missing dependency/credential/config/access]
- Owner: [who can unblock this, if known, else "unknown"]
```

Tag the item `BLOCKER`. This is independent of and stacks with the 2A verdict, the 2D CRITICAL tag, and any Focus Rule tier — a LOW-risk item can still be a BLOCKER, and a BLOCKER item still gets its full 2A/2B/2C analysis on its own merits.

### 2B. Failure Mode Table (Lens 2)

```markdown
### [Item Name] — Failure Modes

| # | Failure Mode | Trigger | Impact | Machine Exit Verification |
|---|-------------|---------|--------|---------------------------|
| F1 | [what fails] | [what causes it] | [what breaks] | [test case or command to prove fix] |
```

Name known patterns explicitly (rate limit, timeout, abort race, resource leak, context overflow, retry storm, partial write).

If a failure mode's trigger or impact depends on how a specific library/API/service actually behaves and you're not sure — don't write it as settled fact. Resolve it per the Unknown Resolution Rule (SKILL.md): verify externally if it's the kind of thing docs/search would settle, ask the user if it's project-specific, or log it to the Research Backlog if it's not blocking this phase. A Failure Mode row built on an unverified guess is exactly the kind of gap Phase 4/6 tend to catch late — cheaper to flag it here.

### 2C. Security Risk Table (Lens 3)

For every item that touches external input, auth, cross-tenant/cross-user state, secrets, or third-party calls:

```markdown
### [Item Name] — Security Risks

| # | Risk | Trust Boundary Crossed | Adversarial Trigger | Impact | Defense Contract |
|---|------|------------------------|----------------------|--------|------------------|
| S1 | [what could be abused/leaked] | [where] | [what a malicious actor would send/do] | [blast radius] | [exact check/guard condition] |
```

If an item genuinely has no security surface, write one line: `No security surface — reason: [why]`. Don't leave it silently blank.

Same caveat as 2B: if a risk's trust boundary or blast radius depends on an assumption about third-party auth/permission behavior you haven't actually confirmed, resolve it (Unknown Resolution Rule) instead of writing the assumption in as if verified.

### 2D. Invariant & Boundary Violation Check

For each invariant and trust boundary from Phase 1, ask:

- Which failure modes (2B) or security risks (2C) could violate/cross it silently — no error, no log, no audit trail?

Mark silent violations as **CRITICAL** — highest-priority tasks requiring machine-verifiable assertions.

### 2E. Categorize by Work Stream

Cluster problem-fit gaps, failure modes, and security risks into natural work stream groupings. Don't force it — let items self-organize. Typical clusters: Tool/execution, Lifecycle/async, State/data integrity, Provider/network, Auth/trust-boundary, Type/schema, Scope/UX gaps.

### 2F. Blocker Gate (Hard Stop)

Once every item has run through 2A–2E, collect every item tagged `BLOCKER` in 2A-bis. This gate runs regardless of Quick/Full Path — a BLOCKER stops the workflow either way.

**If zero items are tagged BLOCKER** → proceed straight to Phase 3, no pause needed.

**If one or more items are tagged BLOCKER** → stop here. Do not proceed to Phase 3 until this is resolved. Present to the user:

> Phase 2 found [N] blocking item(s) that need something outside this session before planning can safely continue:
>
> - **[Item]** — blocked by: [what's missing]
> - **[Item]** — blocked by: [what's missing]
>
> A) I can resolve this now — [provide the credential/access/config], continue Phase 2
> B) Proceed anyway — treat blocked item(s) as accepted debt, mark out-of-scope or deferred for this roadmap
> C) Stop planning here until resolved elsewhere

Do not silently draft a roadmap in Phase 3 around a BLOCKER hoping it resolves itself by Phase 5 — that's exactly the failure mode this gate exists to catch (discovering the blocker only after review/draft effort is already spent).

If the user picks (A), re-run 2A-bis for the now-unblocked item(s) before continuing. If (B), record the deferral explicitly in the Scope section (Out of Scope, with reason) so it doesn't silently vanish from the roadmap. If (C), halt the skill and return control to the user.

## Generic Planning Standard (3-Lens Fallback)

Use this if no project-specific planning standards document is found in Phase 1:

```text
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
