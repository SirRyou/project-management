# Status Classification & Decision-Making

How to classify tasks, discover work, handle ambiguity, and deal with edge cases. This file exists because human input is unpredictable and happy paths don't always exist.

---

## 1. Status Classification Criteria

### The Core Question

Given a situation, which status applies? The answer depends on **two factors**:
- **Have you started?** (yes → PARKED/DONE; no → TODO)
- **Can you continue?** (yes → PARKED; no → BLOCKED)

### Decision Tree

```
Have you started working on this task?
├── No
│   └── It's TODO (backlog)
└── Yes
    └── Can you continue right now?
        ├── No — something external is missing
        │   └── It's BLOCKED
        ├── No — you chose to stop
        │   └── It's PARKED
        └── Is it complete and verified?
            ├── Yes → It's DONE
            └── No → It's ACTIVE or PARKED
```

### Ambiguous Language Mapping

Humans don't speak in status labels. Here's how to interpret common phrases:

| User says | Likely status | Reasoning |
|-----------|---------------|-----------|
| "I'll deal with this later" | PARKED | You chose to stop. You can resume. |
| "We need to do X eventually" | TODO | Never started. Backlog. |
| "I'm waiting on the API team" | BLOCKED | External dependency. You can't continue. |
| "Let's move on to something else" | PARKED | Active choice to pause current work. |
| "This is done" | DONE* | *Only if verified. See DONE criteria below. |
| "I think this works" | ACTIVE → needs verification | Not DONE until confirmed. |
| "Skip this for now" | PARKED or TODO | If started → PARKED. If not started → TODO. |
| "We can't proceed until..." | BLOCKED | External constraint. |
| "I need to think about this" | PARKED | Internal pause, not a blocker. |

### The Internal vs External Distinction

**BLOCKED** is reserved for things **outside your control**:
- Waiting on a human decision ("which design do you prefer?")
- Waiting on an external service ("API key not provided")
- Waiting on another team ("backend team hasn't deployed yet")
- Waiting on a tool ("CI pipeline is down")

**PARKED** is for things **within your control** that you chose to pause:
- "I want to come back to this after I finish the other thing"
- "This needs more thought"
- "I'm switching focus to a higher priority"

**Critical:** A task that depends on another task *you are also doing* is NOT BLOCKED. It's PARKED. You control both tasks. BLOCKED means someone or something else has the ball.

### DONE Criteria

A task is NOT DONE until **all** of these are true:

1. **The code change is made** — the implementation exists
2. **Tests pass** — if the project has tests, they must pass
3. **No regressions** — existing functionality still works
4. **The state file is updated** — `Latest Progress` reflects what was actually done

If any of these fail, the task is still ACTIVE.

**Exception:** If the user explicitly says "this is done, move on" without running tests, mark it DONE but add a note: `DONE (untested — user confirmed)`. Don't argue with the user, but document the gap.

---

## 2. Discovery Behavior

When the skill activates, the agent should **actively look for work**, not wait passively.

### Discovery Sequence

```
1. Is there a state file? → Read it. Resume from ACTIVE task.
2. No state file? → Scan for existing context (roadmaps, TODOs, git history)
3. No legacy docs? → Check git status for uncommitted work
4. No uncommitted work? → Check git log for recent context
5. Nothing found? → Ask the user (see Clarification Protocol)
```

### What to Look For

| Signal | Source | Interpretation |
|--------|--------|----------------|
| Uncommitted changes | `git status` | Someone was working. Check what and why. |
| Recent commits | `git log -5` | What was the last focus? Continue or branch from there. |
| TODO/FIXME comments | `grep -r "TODO\|FIXME\|HACK" src/` | Discovered debt. Add to BRANCHES. |
| Failing tests | `npm test` / `pytest` | Active bug. May need to become ACTIVE task. |
| Open issues | GitHub/issue tracker | Backlog items. Absorb as TODO. |
| Modified but unstaged files | `git diff` | Work in progress. Understand before continuing. |

### Passive vs Active Agents

**Passive (bad):** "I don't see a state file. What would you like me to do?"

**Active (good):** "I found uncommitted changes in `src/auth.ts` and a TODO comment about token refresh. I also see your last commit was about the login flow. Should I continue the auth work, or do you have something else in mind?"

The active agent presents what it found and offers a default, rather than asking an open-ended question.

---

## 3. Clarification Protocol

### When to Ask

Ask the user **only** when one of these is true:

1. **True ambiguity.** Multiple valid interpretations exist and the wrong choice wastes significant work. ("Fix it" with no context about what "it" is.)

2. **Conflicting signals.** State file says one thing, git history says another, user prompt contradicts both. ("ROADMAP.md says Auth is ACTIVE, but you just asked me to work on Billing.")

3. **Destructive action.** The agent is about to do something hard to reverse (delete code, overwrite state, reset progress). Confirm first.

4. **No task discoverable.** No state file, no legacy docs, no git history, vague prompt. The agent genuinely has nothing to work with.

### When NOT to Ask

Don't ask when:

- **The answer is inferable.** Git status shows modified files → continue that work.
- **The choice is low-stakes.** Picking between two TODO items → just pick one, document why.
- **You can make a reasonable default.** No state file → scan legacy docs, absorb what you find, proceed.
- **The user already told you.** They said "help me with the app" → discover what's in progress, continue it.

### How to Ask

Bad (open-ended):
> "What would you like me to do?"

Good (constrained with default):
> "I found two items marked IN_PROGRESS in ROADMAP.md: Billing and Auth. Which should I set as ACTIVE? (I'll default to Billing if you don't specify.)"

The good version:
- Shows what the agent found
- Presents a constrained choice (not open-ended)
- Offers a default so the user can just say "yes" or "the other one"

### The "Guess and Document" Pattern

When the agent makes a reasonable inference without asking, document it in the state file:

```markdown
- **Latest Progress:** Continued auth work based on uncommitted changes in src/auth.ts (no state file found, inferred from git status)
```

This way, if the agent guessed wrong, the user can see *why* it made that choice and correct it.

---

## 4. Edge Cases

### No State File, No Legacy Docs, Empty Git History

The repo is blank. The user said "help me with the app."

**Action:**
1. Ask one question: "What are you building?" or "What should I work on first?"
2. Create the state file with the answer as the ACTIVE task.
3. Don't ask about file format, directory structure, or skill configuration. Just start.

### State File Exists But Is Stale

The state file says "ACTIVE: Fix login bug" but git log shows 20 commits since then, all about billing. The user hasn't updated the state file.

**Action:**
1. Trust git history over the state file for *what actually happened*.
2. Update the state file to reflect current reality.
3. Note the discrepancy: `Latest Progress: Resumed after stale state. Last git activity was billing work.`

### User Contradicts Themselves

User says "focus on Auth" then 5 minutes later "actually, do Billing first."

**Action:**
1. Park Auth (don't delete it).
2. Activate Billing.
3. Don't question the user's priority shift. Just execute the transition.

### Everything Looks DONE

All tasks in the state file are DONE. No TODOs. No BRANCHES.

**Action:**
1. Run `validate` to confirm.
2. Check git status for uncommitted work.
3. If truly nothing left: "All tracked tasks are complete. What would you like to work on next?"
4. Don't invent work. Don't add phantom TODOs.

### Everything Is BLOCKED

All tasks are BLOCKED on external dependencies.

**Action:**
1. Identify the blocker with the shortest path to resolution.
2. Report to user: "All tasks are currently blocked. The closest unblock is [X] — waiting on [Y]. Should I work on something else while we wait?"
3. Don't sit idle. Suggest adjacent work or improvements.

### User Says "This Is Done" But Tests Fail

**Action:**
1. Report the failure: "The tests are failing on [X]. Should I fix them before marking this done, or move on?"
2. If user says "move on" → mark DONE with note: `DONE (user confirmed despite test failures: [brief description])`
3. Add the test failure as a BRANCH item so it's not lost.

### Mid-Task Direction Change

User says "stop working on X, I need you to do Y immediately."

**Action:**
1. Snapshot current work (even if ephemeral, note where you stopped).
2. Park X with reason: "User redirected to Y."
3. Activate Y.
4. Don't finish X first. Don't ask "are you sure?" Just switch.

### Ambiguous Priority

User says "work on whatever is most important." Multiple tasks exist with no priority labels.

**Action:**
1. Pick the task closest to DONE (finish what's almost done first).
2. If tied, pick the one with the most recent activity.
3. Document the choice: `Activated [X] — closest to completion among available tasks.`
4. Don't ask "which one?" when you can make a reasonable choice.

### BLOCKED on Sub-Agent: Idle or Continue?

A parent agent delegates work to a sub-agent. The parent task is now BLOCKED (waiting on sub-agent output). Should the parent idle or pick up another task?

**It depends on whether the sub-agent's output blocks the parent's next step:**

| Situation | Parent action |
|-----------|---------------|
| Parent can't proceed until sub-agent returns (e.g., building a component parent needs to integrate) | Wait, or pick up an **unrelated** TODO task |
| Parent has independent work available (e.g., sub-agent doing frontend, parent can do backend) | Continue on another task |
| No other tasks available | Idle. Don't invent work. |

**Key distinction:** BLOCKED on a sub-agent you control is different from BLOCKED on an external dependency. With a sub-agent, you know it'll finish and you control the timeline. With an external dependency, you don't.

**Context switch safety:** Switching to an unrelated task while waiting for a sub-agent is safe — the sub-agent's state is isolated (see SUBAGENTS.md). Just don't lose track of the sub-agent's completion.

### User Has Only a High-Level ROADMAP (No Detailed State)

The user has a simple checklist, not the full state template:

```markdown
# ROADMAP
- [ ] Auth system
- [ ] Payment integration
- [ ] Dashboard
```

No `Primary Files`. No `Latest Progress`. No `Next Concrete Step`.

**Action:**
1. **Don't force detail.** Absorb the items as-is. Each `- [ ]` becomes a TODO task.
2. **Track completion, not process.** Mark items DONE when the user confirms them. Don't require file paths or progress notes.
3. **Add detail only when needed.** When a task becomes ACTIVE, *then* ask (or infer) the primary files and next step. Don't front-load detail for tasks that haven't started.
4. **The skill adapts to the user's level of organization.** A user with a detailed plan gets detailed tracking. A user with a napkin list gets napkin-level tracking. Both are valid.

**Levels of detail the skill supports:**

| User provides | Skill tracks |
|---------------|--------------|
| Detailed state file (Primary Files, Progress, Next Step) | Full tracking with all fields |
| Simple checklist (task names only) | Completion status per item |
| Single task ("do X") | Ephemeral tracking, no file created |
| No task at all ("help me with the app") | Discovery mode — scan for context, ask if needed |

---

## 5. Scope Boundary: Tracking, Not Planning

This skill **tracks progress**. It does not generate plans.

### What this skill does:
- Track what's ACTIVE, PARKED, BLOCKED, DONE
- Preserve context across sessions and handoffs
- Coordinate sub-agent state isolation
- Detect scope drift and context loss
- Absorb existing plans from the user's documents

### What this skill does NOT do:
- Generate implementation plans from scratch
- Decide what the user should work on
- Break down tasks into sub-tasks (that's the user's or another skill's job)
- Create ROADMAPs or project timelines

### Why this boundary matters:
A user might use `/writing-plans` or `/executing-plans` to create a plan, then use Tree of Work to track whether the plan is getting done. If Tree of Work also generates plans, the two skills conflict. Stay in your lane: **track execution, don't create it.**

### The exception:
If the user asks "break this down for me" and no other planning skill is available, the agent can suggest a breakdown — but record it in the state file as the user's plan, not as the skill's output. The skill adapts to the user's workflow, not the other way around.
