# Scope Analysis (Phase 1)

## Step 1: Pre-Flight & Context Discovery
1. **Pre-flight Check:** Check git is initialized (`git rev-parse`). If yes, run `git status` and verify upstream alignment; warn the user if uncommitted changes or divergence exist. If not, note it and continue.
2. **Project State:** Search root for existing planning files (`STATE.md`, `ROADMAP.md`, `CLAUDE.md`). Extract current project status and existing feature dependencies. If the files conflict, ask the user — never guess precedence.
3. **Codebase Discovery:** Delegate to a subagent with `explore`/search capabilities to scan the codebase, avoiding direct file reading in the main agent's context window. Require the subagent to return:
   - **Relevant files** (paths + one-line purpose)
   - **Schemas** (DB/state shapes that constrain changes)
   - **Patterns** (conventions new code must follow)
   - **Tests** (existing coverage that could break)
   - **Unverified unknowns** (library/API behavior not confirmable from the repo)
4. **Discovery Record:** Keep the codebase findings and any unknowns in memory (or a temporary scratchpad). Do not write them to the file yet — the file is initialized in a single clean write in Step 3, including a `## Research Backlog` section for the unknowns.

---

## Step 2: Synthesize Scope Brief
Synthesize the brief. Under `## IN-SCOPE`, define each item as a distinct, atomic sub-feature or work package (these will serve as the sequential units of analysis for Phase 2). Use the following minimalist structure:

```markdown
# Scope Brief: [Epic Name]

## PROBLEM
[One sentence: the underlying problem being solved, not the literal prompt]

## OBJECTIVE
[One paragraph: what this epic accomplishes]

## IN-SCOPE
* [item] - rationale

## OUT-OF-SCOPE
* [item] - rationale (deferred, out of bounds)

## BLOCKERS
* [item] - must resolve before execution

## SYSTEM INVARIANTS & TRUST BOUNDARIES
* [invariant/boundary] - area of concern (e.g. database transactions, auth rules)

## ASSUMPTIONS
* [assumption] - project risk if wrong
```

---

## Step 3: Stop & Confirm
1. **Hard Stop:** Present the text of the Scope Brief in the chat.
2. **Blocker first:** If BLOCKERS is non-empty, call it out on its own line before the rest of the brief:
   > This can't proceed until [X] is resolved. Options: resolve it now, proceed as accepted debt (moved to OUT-OF-SCOPE), or stop here.
   Get an explicit answer on the blocker before the general confirmation.
3. Ask: `"Scope brief ready. Confirm or request changes?"`
4. **Single Clean Write:** Upon explicit user confirmation, write the complete package to `.deep-plan/<epic-name-in-kebab-case>.md` in a single write operation. Order: `Scope Brief`, then `## Codebase Context` (the Step 1 fields), then `## Research Backlog` placeholder (Phase 2 logs `R{n}` items here). This avoids write collisions and ensures a clean, organized layout.

---

## Scope Unlock Trigger
If Phase 2 gap analysis finds critical misfits:
1. Pause the analysis.
2. Update the scope brief with the user to reflect findings (add/remove items).
3. Lock the scope again and resume Phase 2.
