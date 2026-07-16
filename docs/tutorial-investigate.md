# Tutorial: Debugging with Investigate

In this tutorial, you'll learn how to use Investigate to debug a bug systematically. By the end, you'll have traced the bug to its root cause, fixed it with a structural solution, and written a regression test.

**Related docs:** [How-To Guide](howto-investigate.md) | [Reference](reference-investigate.md) | [Explanation](explanation-investigate.md)

## What You'll Need

- An AI coding agent (Claude Code, Cursor, Copilot, Codex, Gemini CLI, etc.)
- A project with a bug to fix (we'll create one for this tutorial)
- 10 minutes

## Step 1: Create a Bug

First, create a project with a bug:

```bash
mkdir buggy-app
cd buggy-app
git init
echo "# Buggy App" > README.md
git add README.md
git commit -m "Initial commit"
```

Now create a file with a bug:

```bash
mkdir src
echo 'export function divide(a, b) {
  return a / b;
}' > src/math.js

echo 'import { divide } from "./math.js";

console.log(divide(10, 0)); // Bug: division by zero
console.log(divide(10, 2)); // Works fine
' > src/index.js

git add src/
git commit -m "Add math module with division bug"
```

## Step 2: Activate Investigate

Ask your agent to investigate the bug:

```
You: The app crashes when dividing by zero. Investigate this.
Agent: Activating Investigate.

      Collecting symptoms...
      Error: Infinity (not a crash, but incorrect behavior)
      Stack trace: src/math.js:2
      Recent changes: 1 commit (initial implementation)

      Starting Phase 1: Root Cause Investigation.
```

## Step 3: Phase 1 — Collect Symptoms

The agent gathers diagnostic context:

```
Agent: Phase 1: Root Cause Investigation

      Symptoms:
      - divide(10, 0) returns Infinity (should throw error or return null)
      - No error handling for division by zero
      - No validation of input parameters

      Tracing code paths...
      - divide() in src/math.js:2 performs direct division
      - No checks for b === 0

      Analyzing history...
      - 1 commit: initial implementation
      - No prior findings

      Root cause hypothesis: The divide() function doesn't check for
      division by zero before performing the operation.
```

## Step 4: Phase 2 — Formulate Hypothesis

The agent formulates a testable hypothesis:

```
Agent: Phase 2: Systemic Audit & Hypotheses

      Root cause hypothesis: The divide() function returns Infinity
      when b is 0 because JavaScript's division operator doesn't
      throw an error for division by zero.

      Verification: This is verifiable by checking if divide(10, 0)
      returns Infinity.
```

## Step 5: Phase 3 — Test Hypothesis

The agent verifies the hypothesis:

```
Agent: Phase 3: Hypothesis Testing

      Adding verification...
      console.log(divide(10, 0)); // Expected: Infinity
      Result: Infinity ✓

      Hypothesis confirmed: divide(10, 0) returns Infinity.

      Root cause: JavaScript's division operator doesn't throw an
      error for division by zero. The function needs explicit
      validation.
```

## Step 6: Phase 4 — Design Fix

The agent designs a structural fix:

```
Agent: Phase 4: Structural Resolution

      Structural fix: Add input validation to divide() function.
      - Check if b === 0
      - If yes, throw Error("Division by zero")
      - Otherwise, return a / b

      This is a structural fix because:
      - It addresses the root cause (missing validation)
      - It prevents the error at the source
      - It provides a clear error message

      Minimal diff: Only modifying src/math.js:2-4
```

## Step 7: Phase 5 — Verify Fix

The agent writes a regression test and verifies the fix:

```
Agent: Phase 5: Verification & Memory Promotion

      Writing regression test...
      src/math.test.js:1-10
      - Test 1: divide(10, 0) throws Error("Division by zero") ✓
      - Test 2: divide(10, 2) returns 5 ✓
      - Test 3: divide(0, 5) returns 0 ✓

      Running tests...
      All tests pass ✓

      Fix verified: Regression test fails without fix, passes with fix.

      DEBUG REPORT
      ════════════════════════════════════════
      Symptom:         divide(10, 0) returns Infinity
      Root cause:      Missing division by zero validation
      Fix:             Added validation in src/math.js:2-4
      Regression test: src/math.test.js:1-10
      Status:          DONE
      ════════════════════════════════════════
```

## What You Built

You now have a working Investigate setup that:
- Traced the bug to its root cause (missing validation)
- Designed a structural fix (not a patch)
- Wrote a regression test that proves the fix works
- Generated a structured debug report

## Next Steps

- Try using Investigate on a real bug in your project
- Learn about the [3-Strike Rule](../docs/reference-investigate.md#phase-3-hypothesis-testing) for when you get stuck
- Read about [Structural Fixes](../docs/reference-investigate.md#phase-4-structural-resolution) for better solutions
- Check out the [How-To Guide](../docs/howto-investigate.md) for more advanced usage
