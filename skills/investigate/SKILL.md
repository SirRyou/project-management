---
name: investigate
description: >
  Systematic debugging: trace from symptom to root cause, fix the cause,
  prove the fix. Four phases: investigate, analyze, hypothesize, implement.
  NOT for feature work, refactors, or greenfield coding.
triggers:
  - "debug this"
  - "fix this bug"
  - "why is this broken"
  - "investigate this error"
  - "root cause analysis"
  - "it was working yesterday"
  - stack traces
  - 500 errors
  - unexpected behavior
requires:
  - file-read
  - file-write
  - bash
  - grep
  - question
capabilities:
  optional:
    - web-search
    - subagent
---

# Investigate

## Iron Law

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

Fixing symptoms creates whack-a-mole. Every unrooted fix makes the next bug harder to find. Trace to root cause, then fix it.

## Phase 1: Root Cause Investigation

Gather context before forming any hypothesis.

1. **Collect symptoms.** Read error messages, stack traces, reproduction steps. If insufficient, ask the user ONE question at a time.

2. **Read the code.** Trace from symptom back to causes. Use grep to find all references, read to understand the logic.

3. **Check recent changes:**
   ```bash
   git log --oneline -20 -- <affected-files>
   ```
   Regression means the root cause is in the diff.

4. **Reproduce.** Can you trigger the bug deterministically? If not, gather more evidence before proceeding.

5. **Check history.** Search project notes, issue trackers, or prior sessions for investigations on the same files. Recurring bugs in the same area are an architectural smell, not coincidence.

### Prior knowledge

Search for relevant findings from previous work on this codebase:
- Project notes, ADRs, or decision logs
- Issue tracker comments on related files
- Code comments marking known issues (`HACK`, `FIXME`, `WORKAROUND`)

If prior findings exist, note patterns. When a past finding matches the current symptom, surface it: **"Prior finding applies: [summary] (from [source])"**

### Form hypothesis

Output: **"Root cause hypothesis: ..."** — a specific, testable claim about what is wrong and why. Not a guess. Not "it might be." A claim you can confirm or reject with evidence.

---

## Phase 2: Pattern Analysis

Check if this bug matches a known pattern:

| Pattern | Signature | Where to look |
|---------|-----------|---------------|
| Race condition | Intermittent, timing-dependent | Concurrent access to shared state |
| Null propagation | TypeError, Cannot read property of undefined | Missing guards on optional values |
| State corruption | Inconsistent data, partial updates | Transactions, callbacks, event hooks |
| Integration failure | Timeout, unexpected response | External API calls, service boundaries |
| Configuration drift | Works locally, fails in staging/prod | Env vars, feature flags, DB state |
| Stale cache | Shows old data, clears on cache invalidation | Redis, CDN, browser cache, memoization |

Also check:
- Issue tracker for related known bugs
- `git log` for prior fixes in the same area — recurring fixes in the same files are a structural signal

**External research:** If no pattern matches, search for `"{framework} {error type}"` and `"{library} {component} known issues"`. Sanitize first — strip hostnames, IPs, file paths, SQL fragments, customer data from any error text before searching.

---

## Phase 3: Hypothesis Testing

Before writing ANY fix, verify the hypothesis.

1. **Confirm.** Add a temporary log statement, assertion, or debug output at the suspected root cause. Run the reproduction. Does the evidence match the hypothesis?

2. **If wrong:** Search for the sanitized error pattern (`"{component} {error type} {framework version}"`), then return to Phase 1. Gather more evidence. Do not guess.

3. **Three-strike rule:** If three hypotheses fail, **STOP.** Ask the user:
   > Three hypotheses tested, none match. This may be an architectural issue rather than a simple bug.
   > A) Continue investigating — I have a new hypothesis: [describe it]
   > B) Escalate for human review — this needs someone with deeper system knowledge
   > C) Add instrumentation — log the area and catch it on next occurrence

### Red flags

Watch for these during investigation — they signal you're on the wrong track:

- **"Quick fix for now"** — there is no "for now." Fix it right or escalate.
- **Proposing a fix before tracing data flow** — you're guessing, not debugging.
- **Each fix reveals a new problem elsewhere** — wrong layer, not wrong code. Step back.
- **Circular investigation** — same files, same analysis, same dead end. Escalate.

---

## Phase 4: Implementation

Once root cause is confirmed:

1. **Fix the root cause, not the symptom.** The smallest change that eliminates the actual problem.

2. **Minimal diff.** Fewest files touched, fewest lines changed. Do not refactor adjacent code.

3. **Write a regression test that:**
   - **Fails** without the fix (proves the test catches the bug)
   - **Passes** with the fix (proves the fix works)

4. **Run the full test suite.** Paste the output. No regressions allowed.

5. **If the fix touches more than 5 files,** ask the user about blast radius before proceeding.

---

## Phase 5: Verification and Report

**Fresh verification.** Reproduce the original bug scenario and confirm it is fixed. This is not optional.

Run the test suite. Paste the output.

Output a structured report:

```
DEBUG REPORT
════════════════════════════════════════
Symptom:         [what the user observed]
Root cause:      [what was actually wrong]
Fix:             [what changed, with file:line references]
Evidence:        [test output showing fix works]
Regression test: [file:line of the new test]
Related:         [prior bugs in same area, architectural notes]
Status:          DONE | DONE_WITH_CONCERNS | BLOCKED
════════════════════════════════════════
```

### Record findings

If you discovered a non-obvious pattern, pitfall, or insight, record it for future sessions:

- **What**: Brief description of the finding
- **Where**: Affected files (for staleness detection later)
- **Confidence**: 1-10. Verified in code = 8-9. Inference = 4-5. User-stated = 10.
- **Type**: `pattern` (reusable approach), `pitfall` (what NOT to do), `architectural` (structural decision)

Only record genuine discoveries. Test: would this save time in a future session?

---

## Hard Rules

- Three or more failed fix attempts → STOP. Question the architecture, not the hypothesis.
- Never apply a fix you cannot verify.
- Never say "this should fix it." Verify and prove it. Run the tests.
- If a fix touches more than 5 files → flag blast radius before proceeding.

## Completion Status

- **DONE** — root cause found, fix applied, regression test written, all tests pass
- **DONE_WITH_CONCERNS** — fixed but cannot fully verify (intermittent bug, requires staging environment)
- **BLOCKED** — root cause unclear after investigation, escalated for human review

---

## Runtime Bindings

This skill declares what it needs from the host runtime. If a capability is missing, degrade gracefully rather than failing.

### Required

| Capability | Used for | Fallback if missing |
|------------|----------|-------------------|
| file-read | Read source, logs, git history | Cannot investigate without reading code — abort |
| file-write | Apply fix, write regression test | Cannot fix without writing — report findings only |
| bash | Run tests, git log, reproduction | Cannot verify fixes — report hypothesis only |
| grep | Find references, trace code paths | Use read + manual search (slower) |
| question | Escalation at 3-strike, blast radius check | Render decisions as prose, wait for typed reply |

### Optional

| Capability | Used for | Fallback if missing |
|------------|----------|-------------------|
| web-search | External pattern research | Skip — proceed with local analysis only |
| subagent | Fresh-eyes review after failed hypotheses | Proceed with same analysis context, note limitation |
