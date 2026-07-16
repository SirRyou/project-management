# Tutorial: Getting Started with Tree of Work

In this tutorial, you'll learn how to use Tree of Work to keep your AI agent focused on one task at a time. By the end, you'll have a working task tracking system that prevents drift and preserves context across sessions.

**Related docs:** [How-To Guide](howto-tree-of-work.md) | [Reference](reference-tree-of-work.md) | [Explanation](explanation-tree-of-work.md)

## What You'll Need

- An AI coding agent (Claude Code, Cursor, Copilot, Codex, Gemini CLI, etc.)
- A project with files to work on
- 10 minutes

## Step 1: Set Up Your Project

First, make sure you have a project with some work to do. If you don't have one, create a simple project:

```bash
mkdir my-project
cd my-project
git init
echo "# My Project" > README.md
git add README.md
git commit -m "Initial commit"
```

Now create a file to work on:

```bash
echo 'function hello() {
  console.log("Hello, world!");
}' > src/index.js
git add src/index.js
git commit -m "Add hello function"
```

## Step 2: Start Working on a Task

Ask your agent to work on a specific task:

```
You: Add a goodbye function to src/index.js
Agent: I'll add a goodbye function to src/index.js.

      [Agent adds the function]

      Task complete. The goodbye function is now available.
```

The agent did the work, but it didn't track it. Let's activate Tree of Work.

## Step 3: Activate Tree of Work

Ask the agent to track its work:

```
You: Track this work with Tree of Work
Agent: Activating Tree of Work.

      ACTIVE task: "Add goodbye function to src/index.js"
      Status: ACTIVE
      Next Concrete Step: "Add goodbye() function after hello() in src/index.js"

      Working on it...
```

Now the agent is tracking the task. Let's see what happens when we switch tasks.

## Step 4: Switch Tasks

Ask the agent to work on something else:

```
You: Actually, I need to fix a bug in the hello function
Agent: PARKED "Add goodbye function to src/index.js"
      Reason: User redirected to bug fix

      ACTIVE: "Fix bug in hello function"
      Next Concrete Step: "Check hello() in src/index.js for issues"

      What's the bug?
```

The agent parked the first task and activated the new one. This is how Tree of Work prevents context splitting.

## Step 5: Resume the Original Task

Ask the agent to go back to the original task:

```
You: Go back to the goodbye function
Agent: PARKED "Fix bug in hello function"
      Reason: User redirected back to goodbye function

      ACTIVE: "Add goodbye function to src/index.js"
      Last progress: [none]
      Next Concrete Step: "Add goodbye() function after hello() in src/index.js"

      Resuming work...
```

The agent remembered where it left off and resumed from the correct step.

## Step 6: Complete the Task

Let the agent finish the task:

```
You: Finish the goodbye function
Agent: Adding goodbye() function...

      [Agent adds the function]

      Tests pass. No regressions.
      Marked "Add goodbye function to src/index.js" as DONE
      Progress: goodbye() function added to src/index.js:8-10
```

The agent verified the work and marked the task as DONE.

## What You Built

You now have a working Tree of Work setup that:
- Tracks one active task at a time
- Prevents context splitting when switching tasks
- Preserves progress across task switches
- Verifies work before marking tasks as DONE

## Next Steps

- Try using Tree of Work on a real project with multiple tasks
- Learn about [Focus Traps](../docs/reference-tree-of-work.md#focus-traps) to avoid common mistakes
- Read about [Context Recovery](../docs/reference-tree-of-work.md#context-recovery) for resuming work after breaks
- Check out the [How-To Guide](../docs/howto-tree-of-work.md) for more advanced usage
