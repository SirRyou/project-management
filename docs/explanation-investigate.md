# Investigate: Why It Works This Way

Investigate enforces systematic debugging methodology for AI agents. This document explains the design decisions behind it.

**Related docs:** [Tutorial](tutorial-investigate.md) | [How-To Guide](howto-investigate.md) | [Reference](reference-investigate.md)

## The Problem

AI agents debug poorly. They fix symptoms instead of root causes, apply speculative patches, and skip verification. The result: whack-a-mole bugs that keep coming back.

Common failure modes:
- **Symptom fixing**: Agent adds `try-catch` blocks, null guards, or fallbacks without understanding why the error occurred
- **Speculative patching**: Agent guesses at the fix, applies it, and hopes it works
- **No verification**: Agent says "this should fix it" without running tests
- **No learning**: Agent fixes the same bug pattern repeatedly without promoting learnings

## The Approach

Investigate solves this with three mechanisms:

### 1. Root Cause Investigation First

The Iron Law: **NO FIXES WITHOUT ROOT CAUSE INVESTIGATION.**

Why this matters:
- Fixing symptoms creates whack-a-mole
- Every unrooted fix makes the next bug harder to find
- The agent must trace data flow back to the source before editing code

The investigation phase:
1. Collect symptoms (error messages, stack traces, reproduction logs)
2. Trace code paths (follow execution and data flow)
3. Analyze history (check recent changes)
4. Locate prior findings (search repository docs for known pitfalls)

### 2. Hypothesis-Driven Testing

After investigation, formulate a testable hypothesis:

> **Root cause hypothesis: [specific, testable claim about what is wrong and why]**

Why hypothesis-driven?
- Forces specificity (no vague "something is wrong")
- Enables verification (the hypothesis is testable)
- Prevents speculation (the agent must prove the hypothesis)

### 3. Structural Fixes

When designing the fix, reject low-effort local patches. Evaluate structural fit:

- **Local Patch**: Bypasses symptom for the current test case
- **Structural Fix**: Corrects the underlying system vulnerability

Why structural fixes?
- Patches create technical debt
- Structural fixes prevent recurrence
- The agent should fix the system, not just the symptom

## Trade-offs

### 3-Strike Rule

If 3 hypotheses fail, STOP and escalate. Why 3?

**What we gain:**
- Prevents infinite loops of speculation
- Forces the agent to gather more data
- Enables human intervention when stuck

**What we lose:**
- May escalate too early (some bugs need more than 3 tries)
- May miss the root cause (if the agent gives up too soon)

The bet: 3 strikes is enough for most bugs. If the agent can't find the root cause in 3 tries, it needs more data or human help.

### Minimal Diff

Keep changes focused on the structural issue. Don't refactor adjacent code.

Why minimal diff?
- Keeps diffs reviewable
- Prevents scope creep
- Isolates the fix from noise

What we lose:
- May miss related issues
- May leave technical debt

The bet: fix the bug first, refactor later. Mixing fix and refactor makes both harder.

### Regression Test Required

Write a regression test that:
- **Fails** without the fix (proving it reproduces the issue)
- **Passes** with the fix (proving it resolves the issue)

Why required?
- Proves the fix works
- Prevents regression
- Documents the bug for future reference

### Memory Promotion

If the root cause was a systemic pattern or pitfall, promote it to the project's global memory file.

Why promote?
- Prevents recurrence
- Documents the learning
- Helps future agents avoid the same trap

## Alternatives Considered

### Speculative Patching

Some agents apply quick fixes and hope they work. Investigate rejects this because:
- Speculative patches create whack-a-mole
- Every unrooted fix makes the next bug harder to find
- The agent must understand the system before modifying it

### No Verification

Some agents say "this should fix it" without running tests. Investigate rejects this because:
- "Should fix" is not "does fix"
- Tests prove the fix works
- No verification means no confidence

### No Learning

Some agents fix bugs without promoting learnings. Investigate rejects this because:
- Same bugs recur
- Future agents repeat the same mistakes
- Knowledge is lost between sessions

## Design Principles

1. **Root cause first**: Never fix a symptom without understanding the cause.
2. **Hypothesis-driven**: Formulate a testable hypothesis before writing code.
3. **Structural fixes**: Fix the system, not just the symptom.
4. **Minimal diff**: Keep changes focused. Don't refactor adjacent code.
5. **Prove it works**: Write a regression test. Run it. Paste output.
6. **Promote learnings**: If the root cause was systemic, document it.

## The Debug Report

After fixing, output a structured debug report:

```
DEBUG REPORT
════════════════════════════════════════
Symptom:         [what was observed]
Root cause:      [what was wrong]
Fix Type:        [STRUCTURAL | LOCAL_PATCH (Reason: ...)]
Fix:             [file:line reference and diff summary]
Regression Test: [file:line of the new test]
Global Memory:   [Promoted to CLAUDE.md / N/A]
Status:          DONE | BLOCKED
════════════════════════════════════════
```

Why a structured report?
- Documents the investigation for future reference
- Forces the agent to be specific
- Enables auditing and review

## Red Flags

- "Quick fix for now" — there is no "for now"
- Proposing a fix before tracing data flow — you're guessing
- Each fix reveals a new problem elsewhere — wrong layer, not wrong code
- Circular investigation — same files, same dead end. Escalate.

These red flags indicate the agent is not following the methodology. If you see them, stop and reassess.
