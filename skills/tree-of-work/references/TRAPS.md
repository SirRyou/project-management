# Context Drift Traps

Real-world failure modes that break agent focus, with concrete mitigations.

---

## 1. The "Double Active" Split Brain

### Symptom
Two or more tasks are marked `ACTIVE` simultaneously. The agent jumps between them without formal transitions.

### Why It Happens
The agent discovers a "quick bug" while implementing a main feature. It thinks "this is easy, I'll fix it in place" and modifies the bug files while leaving the main task as ACTIVE.

### Impact
Mental context splits. Bug-fix logic bleeds into the unfinished feature, triggering a chain of errors that's hard to untangle.

### Mitigation — Branch Promotion Protocol
If a bug must be fixed immediately, park the main task in writing before touching the bug files:

```markdown
## NOW
- **Task:** Fix webhook timeout
- **Status:** ACTIVE
- **Next Concrete Step:** Add reconnect logic in src/services/stripe.ts

## PARKED / BLOCKED
- **Task:** Integrate Stripe API
  - **Status:** PARKED
  - **Reason:** Timeout bug blocks integration testing
  - **Resume Condition:** "Fix webhook timeout" reaches DONE
```

One ACTIVE task. Always. No exceptions for "quick fixes."

---

## 2. Silent Branching (Hidden Scope Drift)

### Symptom
The agent makes broad code changes outside the current task's scope without recording discoveries in `BRANCHES`. It silently fixes a typo in another file, refactors an unrelated module, or reorganizes imports.

### Why It Happens
LLMs have a built-in tendency to be over-helpful. When they spot a typo in a nearby file or messy code structure, they fix it without asking.

### Impact
The git diff becomes large and scattered. Reviewers (human or coordinator agents) can't tell which changes belong to the task and which are incidental noise.

### Mitigation — The Scope Gate Test
Before making a change outside your `Primary Files`, ask:

> "If I remove this change, does the main task still fail?"

If the answer is no — the task still works without it — that change is scope drift. Revert it, record it in `BRANCHES` as TODO or PARKED, and return to the main task.

```markdown
## BRANCHES
- **Issue:** Typo in auth middleware error message
  - **Parent Task:** Integrate Stripe API
  - **Priority:** Low
  - **Status:** TODO
```

---

## 3. The "Continue Working" Dead End

### Symptom
The `Next Concrete Step` field contains vague, abstract language:

```
Continue implementing websocket
Debug the failing connection
Work on the checkout UI
```

### Why It Happens
The agent is lazy about writing the next step during snapshots, or the context window is under pressure and it shortcuts the state update.

### Impact
When the session hands off to another agent (or resumes after a pause), the successor has no operational direction. It must re-read the entire codebase and logs to figure out "which line did work stop at yesterday?"

### Mitigation — Enforce Mechanical Specificity
The next step must be an action someone (human or agent) can execute without thinking:

**Bad:**
```
Continue implementing webhook
```

**Good:**
```
Add Stripe webhook signature validation in src/routes/webhooks.ts line 25, then run: python scripts/validate_webhook.py
```

**Bad:**
```
Debug the failing connection
```

**Good:**
```
Add exponential backoff (initial 1s, max 30s, factor 2) to the WebSocket reconnect loop in src/utils/socket.ts:42
```

A good `Next Concrete Step` answers: **what file, what line, what change.**
