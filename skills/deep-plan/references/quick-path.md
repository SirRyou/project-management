# Deep Plan Quick Path

## Overview

Deep Plan Quick Path is a lightweight, linear workflow to produce resilient, problem-driven, and implementation-ready roadmaps for complex software changes.

## When to Use

Use this skill when:

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

**Escalation Gate (Hard Rule):**
If the Gap Analysis identifies any `CRITICAL` risk (e.g., auth, permissions, PII), a `MISFIT` status, or if the total work is estimated to exceed 15 tasks, you **must** halt the Quick Path immediately, notify the user, and escalate to the Full Path starting at Phase 2 (Adversarial Gap Enumeration).

---

### Step 3: Draft, Review & Finalize Roadmap

1. **Draft Plan**: Outline work streams with high-level tasks, dependencies, and exit criteria.
2. **Adversarial Review**: Run a quick review pass using a different model (or a same-model subagent with a fresh context) to challenge the draft on edge cases, over-engineering, and security gaps.
3. **Final Roadmap**: Write the final roadmap to `.deep-plan/<epic-name-in-kebab-case>.md` using the canonical headings below — the same H2 heading scheme the Full Path uses, so downstream consumers (execution handoff, quality gates, retro) locate sections the same way whether the plan came from Quick or Full Path.

**Iron Law checkpoint**: presenting the Final Roadmap is not the same as approval. Per SKILL.md's Iron Law, do not begin implementation — do not start editing code — until the user has explicitly confirmed the roadmap. Present it and stop; wait for a real reply, not just the act of writing the file.

---

## Final Roadmap Template

Write to `.deep-plan/<epic-name-in-kebab-case>.md`. Use the same headings the Full Path emits (defined canonically in [roadmap-template.md](../templates/roadmap-template.md)) — Quick Path just fills fewer of them in one pass instead of appending per phase. Every section is `##` (no `#` except the file title).

```markdown
# <Epic/Feature Name>

## PROBLEM
[Underlying problem, not the literal ask]

## OBJECTIVE
[What this epic accomplishes]

## IN-SCOPE
- [item] — rationale

## OUT-OF-SCOPE
- [item] — rationale (deferred)

## BLOCKERS (optional)
- [item] — must resolve before execution

## SYSTEM INVARIANTS & TRUST BOUNDARIES
- [invariant / boundary] — where it's enforced

## Phase 2: Gap Analysis
Per IN-SCOPE item, minimum viable form: Verdict (2A), Failure Modes (2B), Security Risks (2C) or `No security surface — reason: [why]`.

### Problem-Fit & Status: [Item]
- **Verdict:** FIT | PARTIAL_FIT | MISFIT

#### Failure Modes
| # | Failure Mode | Trigger | Impact | Machine Exit Verification |

#### Security Risks
| # | Risk | Trust Boundary | Adversarial Trigger | Impact | Defense Contract |

## Phase 3: Roadmap

### Architecture Decisions
| ID | Decision | Rationale | Affects | Status |

### Work Streams
#### WS1 — <Name>
##### Objective
##### Tasks
| ID | Task | Depends On | Mitigates (F-/S-id) | Risk | Status |
##### Sad Paths
##### Exit Criteria
- [ ] [machine verification command]
##### Unit Tests (per-WS, required)
- [ ] minimal unit test(s) for this WS's own logic

### Cross-Cutting Work (required)
| ID | Task | Work Stream | Depends On | Status |
| X1 | [e2e/integration harness] | WS1, WS2 | WS1-T1 | TODO |

### Dependency Graph
### Implementation Order
### Completion Checklist
```

> Cross-section F-/S-id traceability (Phase 2 -> WS `Mitigates` column) follows the Full Path rule:
> every failure mode and security risk must map to >=1 task. Same quality gates at
> [quality-gates.md](../references/quality-gates.md) apply to Quick Path output.
