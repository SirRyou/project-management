# Implementer Subagent Prompt (WS-Scoped)

Use this template when dispatching an implementer subagent for a workstream.

---

## Template

```
Subagent (general-purpose):
  description: "Implement WS[n]: [WS name]"
  prompt: |
    You are implementing Workstream [n]: [WS name]

    ## WS Brief

    Read your workstream brief first: [BRIEF_FILE]
    It contains the full WS block from the roadmap: tasks, failure modes,
    security risks, exit criteria, and sad paths.

    ## Context

    [Scene-setting: where this WS fits, what earlier WS produced that you depend on]

    ## Architecture Decisions

    [D-ids that affect this WS, from the roadmap's Architecture Decisions table]

    ## Before You Begin

    If you have questions about:
    - The requirements or acceptance criteria
    - The approach or implementation strategy
    - Dependencies or assumptions
    - Anything unclear in the WS brief

    **Ask them now.** Raise any concerns before starting work.

    ## Your Job

    Once you're clear on requirements:
    1. Implement all tasks in this workstream
    2. Run the exit criteria verification commands listed in the brief
    3. Verify failure modes from the brief are handled
    4. Verify security risks from the brief are addressed
    5. Commit your work
    6. Self-review (see below)
    7. Write report and return status

    Work from: [directory]

    While iterating, run the focused tests for what you're changing; run
    the full suite once before committing.

    ## Failure Modes & Security

    The brief lists failure modes (F-ids) and security risks (S-ids) for
    this WS. Your implementation must address each one. If you cannot
    address a failure mode or security risk, report it as BLOCKED with
    the specific reason.

    ## When You're in Over Your Head

    It is always OK to stop and say "this is too hard for me."

    **STOP and escalate when:**
    - The task requires architectural decisions with multiple valid approaches
    - You need to understand code beyond what was provided
    - You feel uncertain about whether your approach is correct
    - The task involves restructuring existing code in ways the plan didn't anticipate

    Report back with status BLOCKED or NEEDS_CONTEXT.

    ## Before Reporting Back: Self-Review

    **Completeness:**
    - Did I implement all tasks listed in the WS brief?
    - Did I address all failure modes and security risks?
    - Are exit criteria verification commands passing?

    **Quality:**
    - Names clear and accurate?
    - Code clean and maintainable?
    - Followed existing patterns in the codebase?

    **Discipline:**
    - Did I avoid overbuilding (YAGNI)?
    - Did I only build what was requested?
    - Did I stay within this WS scope?

    Fix any issues you find before reporting.

    ## Report Format

    Write your full report to [REPORT_FILE]:
    - What you implemented (tasks completed)
    - Exit criteria verification results (command + output)
    - Failure modes addressed (F-ids)
    - Security risks addressed (S-ids)
    - Files changed
    - Self-review findings (if any)
    - Any issues or concerns

    Then report back with ONLY (under 15 lines):
    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - Commits created (short SHA + subject)
    - One-line test summary (e.g. "14/14 passing, exit criteria verified")
    - Your concerns, if any
    - The report file path

    If BLOCKED or NEEDS_CONTEXT, put the specifics in the final message.
```

## Placeholders

- `[BRIEF_FILE]` — REQUIRED: WS brief extracted from roadmap
- `[REPORT_FILE]` — REQUIRED: where to write the detailed report
- `[directory]` — working directory for implementation
- `[WS name]` — workstream name from roadmap
- `[n]` — workstream number

## Status Handling

- **DONE** → proceed to review
- **DONE_WITH_CONCERNS** → read concerns, address if correctness/scope, note if observation
- **NEEDS_CONTEXT** → provide missing context, re-dispatch
- **BLOCKED** → assess: context problem (re-dispatch), needs more capability (upgrade model), plan wrong (escalate to user)
