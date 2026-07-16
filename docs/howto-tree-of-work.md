# How to Use Tree of Work

Tree of Work keeps agents focused on one task at a time. Here's how to use it effectively.

**Related docs:** [Tutorial](tutorial-tree-of-work.md) | [Reference](reference-tree-of-work.md) | [Explanation](explanation-tree-of-work.md)

## Prerequisites

- An AI coding agent (Claude Code, Cursor, Copilot, Codex, Gemini CLI, etc.)
- A project with files to work on
- Basic understanding of git (optional but helpful)

## Steps

### 1. Activate the Skill

Tree of Work activates automatically when you say things like:
- "Where was I?"
- "What's next?"
- "I'm lost"
- "Resume"
- "Organize my work"
- "Break down this task"

Or you can invoke it explicitly by asking the agent to track its work.

### 2. Define Your First Task

When the skill activates, it will scan for existing context:
- Uncommitted changes in git
- Recent commits
- TODO/FIXME comments
- Open issues

If it finds work in progress, it will offer to continue that. Otherwise, it will ask what you want to work on.

**Example:**
```
Agent: I found uncommitted changes in src/auth.ts. Should I continue the auth work?
You: Yes, continue that.
Agent: Set ACTIVE task: "Implement auth middleware"
      Next Concrete Step: "Add JWT validation in src/auth.ts:42"
```

### 3. Work on Your Task

As you work, the agent will:
- Update progress after each meaningful change
- Keep the `Next Concrete Step` specific and actionable
- Run the Scope Gate Test before modifying files outside scope

**Example:**
```
Agent: Added JWT validation in src/auth.ts:42-58
      Next Concrete Step: "Add token refresh logic in src/auth.ts:60"
```

### 4. Switch Tasks (If Needed)

If you need to switch tasks:
1. Agent parks the current task with a reason
2. Agent activates the new task
3. Agent records the switch in state

**Example:**
```
You: Actually, I need to fix a bug in the payment flow.
Agent: PARKED "Implement auth middleware" (reason: user redirected to payment bug)
      ACTIVE: "Fix payment bug"
      Next Concrete Step: "Check payment webhook in src/payments.ts:15"
```

### 5. Resume After a Break

When you return to work:
1. Agent checks for prior state
2. Agent reconciles with git status
3. Agent resumes from the last `Next Concrete Step`

**Example:**
```
You: Where was I?
Agent: You were working on "Implement auth middleware"
      Last progress: Added JWT validation
      Next Concrete Step: "Add token refresh logic in src/auth.ts:60"
```

### 6. Complete the Task

When the task is done:
1. Agent verifies tests pass
2. Agent checks for regressions
3. Agent marks the task as DONE
4. Agent updates progress notes

**Example:**
```
Agent: Tests pass. No regressions.
      Marked "Implement auth middleware" as DONE
      Progress: JWT validation and token refresh implemented
```

## Verification

After each task completion, verify:
- Tests pass (if the project has tests)
- No regressions in existing functionality
- Progress notes reflect what was actually done

## Troubleshooting

### Agent Lost Focus

If the agent starts working on unrelated code:
1. Remind it of the current task
2. Ask it to run the Scope Gate Test
3. Ask it to revert any drift

**Example:**
```
You: You're drifting. Run the Scope Gate Test.
Agent: Reverting change to src/utils.ts (not related to auth)
      Logged in backlog: "Fix typo in utils.ts"
```

### Agent Has Multiple Active Tasks

If the agent marks multiple tasks as ACTIVE:
1. Remind it of the Iron Law (one ACTIVE task)
2. Ask it to PARK the extra tasks
3. Ask it to focus on one task

**Example:**
```
You: You have two ACTIVE tasks. Park one.
Agent: PARKED "Fix payment bug" (reason: user requested focus on auth)
      ACTIVE: "Implement auth middleware"
```

### Agent Skipped Verification

If the agent marks a task as DONE without running tests:
1. Ask it to run tests
2. Ask it to check for regressions
3. Ask it to update the status if tests fail

**Example:**
```
You: Did you run tests?
Agent: Running tests... 2 failures
      Marking task as ACTIVE (tests failing)
      Next Concrete Step: "Fix test failures in src/auth.test.ts:15"
```
