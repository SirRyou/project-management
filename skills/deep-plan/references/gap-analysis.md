# Reference: Gap Analysis (Phase 2)

Guides the agent through Phase 2 (Adversarial Gap Enumeration) of the deep-plan workflow.

---

## Mindset (Read Aloud Before Starting)

You are not filling in a form. You are a skeptical lead engineer reviewing a proposal from someone who hasn’t yet been burned by production. Your job is to find the gaps that silence hides.

Run every item through this filter:

- **What is the invariant?** – What must remain true no matter what? State it explicitly, then ask what would break it.
- **What happens when it fails?** – Not *if* – *when*. Does the system fail loudly (logs, alerts) or silently corrupt state?
- **What if the caller is malicious?** – Treat every input as hostile. What is the trust boundary, and what is the shortest path across it?
- **What don’t I know?** – If a behaviour depends on an external library, API limit, or runtime quirk you can’t verify, name it. Don’t assume.

The goal is not to generate many rows. The goal is to find the one failure mode that would wake you up at 3 a.m.

## Phase 2 — Adversarial Gap Enumeration

## Step 2.1: Execute 3-Lens Analysis Per Item
Run all three lenses for each item listed under `IN-SCOPE` in the approved Phase 1 Scope Brief. **Structure the output sequentially by item**, resolving Lens 1, Lens 2, and Lens 3 inside the same item block before moving to the next item.

**Progressive Write Rule (Active Here):**
After completing the full analysis block (2A–2D) for **each item**, immediately append that block to `.deep-plan/<epic-name-in-kebab-case>.md` under `# Phase 2: Gap Analysis`. Do NOT batch all items in memory and write once.

### Quick-Skip Rule
If an item clearly has no security surface (e.g., pure internal formatting logic, UI-only cosmetic changes, documentation updates), omit the 2C Table entirely and write exactly: `No security surface — reason: [why]`. Do NOT skip Lens 1 or Lens 2 — every item needs problem-fit and resilience analysis.

### Risk Level Assignment (First match wins)

Apply the FIRST matching rule for each item:

| Rule | Tag |
|------|-----|
| Touches authentication, authorization, PII, or permission checks | **CRITICAL** |
| Calls external API, reads/writes filesystem, spawns subprocesses, modifies DB schema | **HIGH** |
| Complex business logic, state mutations (non-auth), multi-step workflows | **MEDIUM** |
| Pure UI styling, doc updates, logging changes, renaming variables | **LOW** |

### Focus Rule
Spend proportional effort based on risk level:
- **CRITICAL/HIGH items**: Full three-lens analysis with detailed tables.
- **MEDIUM items**: Condensed analysis — focus on the most likely failure mode and top security risk.
- **LOW items**: One-liner verdict per lens unless something unexpected surfaces.

---

### [INSERT ITEM NAME HERE] Analysis Block

#### 2A. Problem-Fit Check (Lens 1) & Blocker Check (2A-bis)
* **Root-Cause Enforcement**: You must identify whether a gap is a symptom of a deeper design mismatch (e.g., state desynchronization, bad data modeling, race conditions). The plan **cannot** propose a local bypass (such as masking an exception or throwing in a quick try-catch) unless the root cause is addressed or explicitly marked as accepted technical debt
```markdown
### Problem-Fit & Status: [Item Name]
- Literal ask: [what was requested]
- Underlying goal: [what actually needs to be true for the user]
- Gap: [does the literal ask fully close that gap? if not, what's missing?]
- Verdict: [FIT | PARTIAL_FIT | MISFIT] 
  - If PARTIAL_FIT: propose an **additional task** or **scope adjustment** to close the gap.
  - If MISFIT: flag as needing re-scoping (will trigger 2F gate).
- Invariant Impact: [Preserved | Threatened: state invariant broken]
- Blocker Status: [NONE | BLOCKER - Reason: (missing credential/config/access/infra/dependency)]
- Blocker Owner: [who can unblock this, if known, else "unknown"]
- Unknowns: [list any library behavior, API contract, or limit you couldn't verify]
  → Log each as `R{n}: [question] - Priority: High/Med/Low` in the Research Backlog section at the end of the file.
```
*Note: A LOW-risk item can still be a BLOCKER. The BLOCKER tag stacks independently with any status.*

#### 2B. Failure Mode Table (Lens 2)
```markdown

| #   | Failure Mode | Trigger          | Impact        | Machine Exit Verification           |
| --- | ------------ | ---------------- | ------------- | ----------------------------------- |
| F1  | [what fails] | [what causes it] | [what breaks] | [test case or command to prove fix] |
```
Name known patterns explicitly. If behavior is unverified, flag it and follow the *Unknown Resolution Rule* (see Appendix B). Do not guess.
If a failure trigger depends on unverified external behavior → do NOT guess. Flag it as `Unverified: [what you'd need to check]` and add to Research Backlog.

#### 2C. Security Risk Table (Lens 3)
*(Omit this table and write the one-liner skip reason if the item has no security surface)*

Think like an attacker: “What is the cheapest input I can send to make this system misbehave?”
```markdown

| #   | Risk                          | Trust Boundary Crossed | Adversarial Trigger                    | Impact         | Defense Contract              |
| --- | ----------------------------- | ---------------------- | -------------------------------------- | -------------- | ----------------------------- |
| S1  | [what could be abused/leaked] | [where]                | [what a malicious actor would send/do] | [blast radius] | [exact guard condition, check, or sanitisation] |
```

#### 2D. Invariant & Boundary Violation Check
- Identify which failure modes (2B) or security risks (2C) could violate system invariants or cross trust boundaries *silently* (no logs/errors). 
- Mark these silent violations as **CRITICAL** tasks requiring automated assertions.

---

## Step 2.2: Categorize & Consolidate

### 2E. Categorize by Work Stream
Cluster gaps, failure modes, and security risks into natural work stream groupings (e.g., Tool/execution, Lifecycle/async, State/data integrity, Provider/network, Auth/trust-boundary).

### 2F. Review Gate (Hard Stop)
Once all items are analyzed, collect all items tagged as **BLOCKER** or marked as **MISFIT / PARTIAL_FIT**. 

**If zero BLOCKER, MISFIT, or PARTIAL_FIT items exist** → proceed straight to Phase 3.

**If any items are tagged BLOCKER, MISFIT, or PARTIAL_FIT** → **STOP HERE**. Do not proceed to Phase 3. Present the findings to the user:

> Phase 2 found [N] blocking/misfit item(s) that must be addressed before planning can continue:
>
> - **[Item Name]** — Status: [BLOCKER/MISFIT] | Detail: [what is missing or wrong]
>
> A) I can resolve this now — [provide the credential/clarification/access], re-run analysis.
> B) Proceed anyway — treat as accepted debt, automatically move blocked/misfit items to OUT-OF-SCOPE in the Phase 1 Scope Brief.
> C) Stop planning here until resolved elsewhere.

---

## Appendix B: API/Library Verification Gate
If the plan depends on the contract of a third-party API, library method, or database constraint that is not already explicitly visible in the codebase, you **must** verify it (e.g., via web search, checking `node_modules` code, or running a scratch script).

If verification is impossible in this environment:
1. Flag it as a blocker (`R{n}`) in the Research Backlog.
2. Define a spike/prototyping task as the very first task in that work stream to resolve it before any implementation code is written.
Never proceed under the assumption that a library function "probably supports" a feature.
