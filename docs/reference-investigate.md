# Investigate Reference

Investigate is a behavioral skill for AI agents that enforces systematic debugging methodology. It traces from symptom to root cause, designs structural fixes, and promotes learnings to prevent recurrence.

**Related docs:** [Tutorial](tutorial-investigate.md) | [How-To Guide](howto-investigate.md) | [Explanation](explanation-investigate.md)

## Core Concepts

### The Iron Law

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION AND INVARIANT VERIFICATION.**

Speculative patching (e.g. adding quick `try-catch` blocks, local null guards, or bypassing auth) is strictly prohibited. You must trace data flow back to the root cause before editing code.

### Phase Workflow

1. **Root Cause Investigation** — collect symptoms, trace code paths, analyze history, locate prior findings
2. **Systemic Audit & Hypotheses** — codebase-wide search for pattern-based errors, formulate testable hypothesis
3. **Hypothesis Testing** — verify with evidence, iterate, escalate after 3 failures
4. **Structural Resolution** — fix root cause, minimal diff, structural not patch
5. **Verification & Memory Promotion** — regression test, invariant check, promote learnings

## Phase Details

### Phase 1: Root Cause Investigation

Gather diagnostic context before writing hypotheses or code:

1. **Collect Symptoms**: Read error messages, stack traces, and reproduction logs.
2. **Trace Code Paths**: Follow execution and data flow from the symptom back to the source. Use `grep` to locate all references and related call sites.
3. **Analyze History**: Check recent changes:
   ```bash
   git log --oneline -20 -- <affected-files>
   ```
   If a recent commit touched these files, prioritize reviewing that diff.
4. **Locate Prior Findings**: Search repository docs (`STATE.md`, `CLAUDE.md`, or previous debug logs) for known pitfalls in this module. If a match is found, note: *"Prior finding applies: [summary]"*.

### Phase 2: Systemic Audit & Hypotheses

1. **Codebase-Wide Search**: If the bug is a pattern-based error (e.g., resource leak, missing validation, concurrency race), check if the same pattern exists in other files. Do not fix them yet—log them.
2. **Formulate Hypothesis**: Output: **`Root cause hypothesis: [specific, testable claim about what is wrong and why]`**.
   - Must be verifiable with a log, assertion, or unit test.

### Phase 3: Hypothesis Testing

1. **Verify**: Add a temporary assertion, log, or debug breakpoint at the suspected root cause. Run the reproduction scenario.
2. **Iterate**: If the hypothesis is wrong, discard it, gather more trace data, and try again.
3. **Escalation (Strike-Three Rule)**: If 3 hypotheses fail:
   - **STOP.** Do not keep guessing.
   - **Generate Debug Dump**: Write a structured reproduction report to `.agent/debug-dump.json` containing:
     - Verified symptoms & stack traces.
     - Hypotheses tested and why they failed.
     - Active git diff of debug logs/instrumentation.
   - Present the dump to the user and request escalation or human review.

### Phase 4: Structural Resolution

When designing the fix, reject low-effort local patches. Evaluate structural fit:

1. **Structural vs. Patch Analysis**:
   - *Local Patch*: Bypasses symptom for the current test case (e.g., throwing a default fallback on network timeout).
   - *Structural Fix*: Corrects the underlying system vulnerability (e.g., implementing centralized retry middleware, database transaction boundaries, or type safety guards).
2. **Resolution Constraint**: Implement the most robust structural fix possible. If constraints force a local patch, document the accepted technical debt explicitly in the report.
3. **Minimal Diff footprint**: Keep changes focused on the structural issue. Do not perform unrelated refactoring.

### Phase 5: Verification & Memory Promotion

1. **Regression Testing**: Write a regression unit test that:
   - **Fails** without the fix (proving it reproduces the issue).
   - **Passes** with the fix (proving it resolves the issue).
2. **Systemic Invariant Check**: Verify that the fix does not violate any repository invariants or break existing test suites.
3. **Promote Learnings (Prevent Recurrence)**:
   - If the root cause was a systemic pattern or pitfall, add it to the project's global memory file (e.g., `CLAUDE.md`, `.cursorrules`, or `STATE.md`) under a `# Pitfalls & Invariants` section.
4. **Report**: Output the structured debug summary:

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

## Core Rules

- **3-strike rule**: 3 failed hypotheses → STOP, escalate
- **Minimal diff**: fewest files, fewest lines. Don't refactor adjacent code.
- **Regression test**: must fail without fix, pass with fix
- **Verify**: never say "this should fix it." Run the tests. Paste output.
- **Blast radius**: if fix touches >5 files, flag before proceeding

## Red Flags

- "Quick fix for now" — there is no "for now"
- Proposing a fix before tracing data flow — you're guessing
- Each fix reveals a new problem elsewhere — wrong layer, not wrong code
- Circular investigation — same files, same dead end. Escalate.

## Runtime Requirements

| Capability | Required | Purpose |
|------------|----------|---------|
| file-read | Yes | Read source, logs, git history |
| file-write | Yes | Apply fix, write regression test |
| bash | Yes | Run tests, git log, reproduction |
| grep | Yes | Find references, trace code paths |
| question | Yes | 3-strike escalation, blast radius check |
| web-search | No | External pattern research |
| subagent | No | Fresh-eyes review after failed hypotheses |

## Graceful Degradation

If a required capability is missing:
- No bash → report verified hypothesis only, do not apply changes.
- No question → write debug dump to disk, pause execution, and wait for input.

## Debug Report Format

```
DEBUG REPORT
════════════════════════════════════════
Symptom:         [what the user observed]
Root cause:      [what was actually wrong]
Fix:             [what changed, file:line]
Evidence:        [test output showing fix works]
Regression test: [file:line of new test]
Related:         [prior bugs in same area]
Status:          DONE | DONE_WITH_CONCERNS | BLOCKED
════════════════════════════════════════
```
