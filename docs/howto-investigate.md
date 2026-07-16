# How to Use Investigate

Investigate guides agents through systematic debugging. Here's how to use it effectively.

**Related docs:** [Tutorial](tutorial-investigate.md) | [Reference](reference-investigate.md) | [Explanation](explanation-investigate.md)

## Prerequisites

- An AI coding agent (Claude Code, Cursor, Copilot, Codex, Gemini CLI, etc.)
- A bug or error to investigate
- Access to source code, logs, and git history

## Steps

### 1. Activate the Skill

Investigate activates automatically when you say things like:
- "Debug this"
- "Fix this bug"
- "Why is this broken?"
- "Investigate this error"
- "Root cause analysis"

Or you can invoke it explicitly by asking the agent to investigate a bug.

### 2. Phase 1: Collect Symptoms

The agent gathers diagnostic context:
- Error messages and stack traces
- Reproduction logs
- Recent changes to affected files

**Example:**
```
Agent: Collecting symptoms:
      Error: TypeError: Cannot read property 'id' of undefined
      Stack trace: src/auth.ts:42
      Recent changes: 3 commits in last 24 hours
```

### 3. Phase 2: Formulate Hypothesis

The agent traces code paths and formulates a testable hypothesis:

**Example:**
```
Agent: Root cause hypothesis: The user object is undefined when the
      session expires. The auth middleware doesn't check for expired
      sessions before accessing user.id.
```

### 4. Phase 3: Test Hypothesis

The agent verifies the hypothesis with evidence:
- Adds temporary assertions or logs
- Runs the reproduction scenario
- Checks if the hypothesis holds

**Example:**
```
Agent: Testing hypothesis...
      Added console.log in src/auth.ts:42
      Reproduced: user is undefined when session expires
      Hypothesis confirmed.
```

### 5. Phase 4: Design Fix

The agent designs a structural fix (not a patch):

**Example:**
```
Agent: Structural fix:
      Add session expiry check in src/auth.ts:40-41
      If session expired, redirect to /login
      This prevents the undefined user error at the source
```

### 6. Phase 5: Verify Fix

The agent writes a regression test and verifies the fix:

**Example:**
```
Agent: Regression test written:
      src/auth.test.ts:15-25
      Test fails without fix (reproduces error)
      Test passes with fix (error resolved)

      DEBUG REPORT
      ════════════════════════════════════════
      Symptom:         TypeError: Cannot read property 'id' of undefined
      Root cause:      Missing session expiry check in auth middleware
      Fix:             Added session expiry check in src/auth.ts:40-41
      Regression test: src/auth.test.ts:15-25
      Status:          DONE
      ════════════════════════════════════════
```

## Verification

After each investigation, verify:
- Root cause is identified and documented
- Fix is structural (not a patch)
- Regression test passes
- Debug report is complete

## Troubleshooting

### Agent Fixes Symptoms

If the agent applies a patch instead of a structural fix:
1. Remind it of the Iron Law (no fixes without root cause)
2. Ask it to trace data flow back to the source
3. Ask it to design a structural fix

**Example:**
```
You: That's a patch, not a fix. Trace the data flow.
Agent: You're right. The real issue is in the session management.
      Structural fix: Add session expiry check at the source.
```

### Agent Guesses at Fix

If the agent proposes a fix before investigating:
1. Remind it of the Iron Law (no fixes without investigation)
2. Ask it to collect symptoms first
3. Ask it to formulate a testable hypothesis

**Example:**
```
You: You're guessing. Collect symptoms first.
Agent: Collecting symptoms...
      Error: TypeError in src/auth.ts:42
      Hypothesis: User object is undefined when session expires
```

### Agent Gets Stuck (3-Strike Rule)

If the agent fails 3 hypotheses:
1. It should STOP and escalate
2. It should generate a debug dump
3. It should present the dump to you

**Example:**
```
Agent: 3 hypotheses failed. Generating debug dump.
      [debug dump contents]
      Please review and provide guidance.
```

### Agent Skips Regression Test

If the agent skips the regression test:
1. Ask it to write a test that fails without the fix
2. Ask it to run the test with the fix
3. Ask it to paste the output

**Example:**
```
You: Where's the regression test?
Agent: Writing regression test...
      src/auth.test.ts:15-25
      Test fails without fix: ✓
      Test passes with fix: ✓
```

### Agent Doesn't Promote Learnings

If the agent fixes a systemic issue but doesn't promote learnings:
1. Ask if the root cause was a systemic pattern
2. If yes, ask it to add it to the project's global memory file
3. Ask it to document the learning

**Example:**
```
You: Was this a systemic pattern?
Agent: Yes, it's a common pattern with session handling.
      Adding to CLAUDE.md under "Pitfalls & Invariants":
      "Always check session expiry before accessing user properties."
```
