# Anti-Patterns

Behaviors that undermine workspace organization, security, and Git stability.

## 1. Physical Git Branching Per Micro-Task

**Mistake:** `git checkout -b bug/fix-login-typo` for every small sub-task discovered during work.

**Why it's bad:** Repository pollution, merge conflict loops, CI overhead. If an agent discovers 3-5 small issues in 10 minutes, that's 3-5 new branches cluttering the repo.

**Fix:** Keep all logical branches on the same physical Git branch. Commit according to your project's own conventions — the skill does not prescribe commit message formats or staging rules. See [STATUS_MODEL.md](STATUS_MODEL.md) for soft guidelines.

## 2. Credentials in State Files

**Mistake:** Pasting raw API responses or error messages with tokens/keys into `current-state.md`.

**Why it's bad:** Secrets in Git history are permanent. Requires force-push to clean.

**Fix:** Sanitize before writing:
```markdown
# Bad
- **Latest Progress:** Got error: Invalid key: Bearer eyJhbGciOiJIUzI1NiIs...

# Good
- **Latest Progress:** Got error: Invalid key: Bearer <REDACTED_SECRET>
```

The `validate` and `snapshot` commands auto-redact known patterns and block high-entropy strings.

## 3. Multiple Active Tasks

**Mistake:** Marking 2+ tasks as `ACTIVE` in `NOW`.

**Why it's bad:** Split focus confuses successor agents, breaks dependency tracking.

**Fix:** One ACTIVE task always. PARK the current one before activating a new one.

## 4. Silent Context Drift

**Mistake:** Modifying files without updating `current-state.md`.

**Why it's bad:** Successor agents won't know what changed, leading to duplicate work or overwrites.

**Fix:** Update `Latest Progress` and `Primary Files` as you work. Run `status` at session start.

## 5. The God Object Mutation & Substitution Test Failure

### Symptom
The agent begins refactoring multiple unrelated modules, modifying global state machines, or rewriting utility layers while supposed to be working on a highly localized sub-task. This dramatically expands the final Git diff and blows up the context window.

### Why It Happens
When encountering an edge case, the agent adopts a "God Object" mental model—treating the codebase as a single monolithic entity where everything must be corrected immediately. The agent silently switches context without verifying if the modification is actually critical to the immediate goal.

### The Substitution Test Enforcement
To prevent this trap, the agent **MUST** run the **Substitution Test** before modifying any file outside the original scope or expanding the code changes:

> **The Substitution Test:** *"If this specific code change is entirely omitted or reverted from the final Git diff, does the primary task defined in the `NOW` section still fail?"*

* **If YES (It still fails without this change):** The modification is strictly coupled and necessary. Add the file to `Primary Files` and continue.
* **If NO (The primary task can function or be verified without it):** This is an explicit **Scope Drift Trap**. You must:
  1. Revert or isolate those unrelated changes immediately.
  2. Log the discovered issue under the `## BRANCHES` section as a `TODO` or `PARKED` item.
  3. Return to the primary active focus path.
  