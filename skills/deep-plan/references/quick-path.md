# Deep Plan Quick Path

## Overview

Deep Plan Quick Path is a lightweight, linear workflow to produce resilient, problem-driven, and implementation-ready roadmaps for complex software changes.

## When to Use

Use this skill when ():

- Logic sequencing is linear or independent (<=3 steps).
- Changes are stateless, pure additions, or isolated logic.
- Low uncertainty/risk and high confidence.
- No trust-boundary crossings or security-critical paths.

**When NOT to use:**

- Trivial changes, single-file edits, or simple bug fixes. Use direct implementation instead.
- Complex multi-stage changes, state schema mutations, or low-confidence tasks (use Full Path instead).

---

## The 3-Step Workflow

### Step 1: Define Scope (Human Checkpoint)

1. **Pre-flight Check**: Check if git is initialized. If yes, run `git status --porcelain` to check for uncommitted changes, and check if the current branch is diverged from its upstream. Warn the user if uncommitted changes or branch divergence exist, and recommend stashing, committing, or pulling before proceeding to ensure the plan is based on a clean and up-to-date codebase.
2. **Draft Scope Brief**:
   - **Problem**: What actual problem is being solved (not just the literal request)?
   - **In Scope** / **Out of Scope** items.
   - **Blocker**: "this thing cannot proceed until X is resolved."
   - **Invariants**: System guarantees that must not break.
   - **Trust Boundaries**: Where untrusted data enters or boundaries are crossed.
3. **Checkpoint**: Present the Scope Brief to the user and confirm before proceeding. Do not proceed until approved.

**If the Blocker field is non-empty**, don't fold it into the general checkpoint — call it out on its own line before presenting the rest of the brief:

> This can't proceed until [X] is resolved. Options: resolve it now, proceed treating it as accepted debt (noted in Out of Scope), or stop here.

Get an explicit answer on the blocker specifically before moving to Step 2 — a blocker that only gets a passive nod as part of "yes, the whole brief looks good" isn't actually resolved.

---

### Step 2: Gap Analysis (The 3 Lenses)

Analyze the codebase and requirements under three lenses:

1. **Problem-Fit**: Does the literal request fully solve the underlying problem? If not, identify the gaps.
2. **Resilience**: What happens if operations fail, timeout, run concurrently, or are called twice? List key failure modes.
3. **Security**: How could inputs be abused? Are there missing permission checks or exposed secrets? (Write `No security surface — reason: [why]` if none).

If a new blocker surfaces here that wasn't visible at Step 1 (e.g. gap analysis reveals a missing credential or external dependency), don't silently carry it into the draft — apply the same stop-and-ask from Step 1 before continuing to Step 3.

---

### Step 3: Draft, Review & Finalize Roadmap

1. **Draft Plan**: Outline work streams with high-level tasks, dependencies, and exit criteria.
2. **Adversarial Review**: Run a quick review pass using a different model (or a same-model subagent with a fresh context) to challenge the draft on edge cases, over-engineering, and security gaps.
3. **Final Roadmap**: Write the final roadmap to `.deep-plan/<epic/feature-name>.md` using the template below.

**Iron Law checkpoint**: presenting the Final Roadmap is not the same as approval. Per SKILL.md's Iron Law, do not begin implementation — do not start editing code — until the user has explicitly confirmed the roadmap. Present it and stop; wait for a real reply, not just the act of writing the file.

---

## Final Roadmap Template

write to .deep-plan/

```markdown
# Phase Roadmap: [Epic/Feature Name]

## 1. Scope & Objective
- **Objective**: [Goal]
- **Underlying Problem**: [Core problem solved]
- **In Scope**: [Items]
- **Out of Scope**: [Items]

## 2. Gap Analysis Summary
- **Problem-Fit Gaps**: [List]
- **Key Failure Modes**: [List]
- **Security Risks**: [List]

## 3. Work Streams
### WS1: [Name]
- **Tasks**:
    - T1: [Title] - **Steps**: [Bite-sized] - **Exit Criteria**: [Testable] - **Sad Path**: [Mitigation]
    - T2: ...
  - **Dependencies**: [e.g., T2 depends on T1]

...
```
