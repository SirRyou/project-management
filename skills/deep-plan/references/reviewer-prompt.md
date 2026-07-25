# Sprint Reviewer Prompt Template

Use this template when dispatching a reviewer subagent for a sprint (or a
parallel lane within a sprint — see `execution-handoff.md` §2).
The reviewer reads the sprint diff once and returns three verdicts: spec
compliance, code quality, and integrity.

**Purpose:** Verify one sprint's implementation matches its requirements
(nothing more, nothing less), is well-built (clean, tested, maintainable),
and was built honestly (no shortcuts disguised as completion).

---

## Template

```
Subagent (general-purpose):
  description: "Review Sprint[m] (spec + quality + integrity)"
  prompt: |
    You are reviewing one sprint's implementation: first whether it
    matches its requirements, then whether it is well-built, then
    whether it was built honestly. This is a sprint-scoped gate, not a
    merge review — a broad whole-branch review happens separately after
    all sprints are complete.

    ## What Was Requested

    Read the sprint brief: [BRIEF_FILE]
    (Tasks in this brief may originate from more than one WS in the
    roadmap — the brief notes source WS per task for traceability only;
    it does not change scope.)

    Global constraints from the roadmap that bind this sprint:
    [GLOBAL_CONSTRAINTS]

    ## What the Implementer Claims They Built

    Read the implementer's report: [REPORT_FILE]

    ## Diff Under Review

    **Diff file:** [DIFF_FILE]

    Read the diff file once — it contains the commit list, a stat summary,
    and the full diff with surrounding context. The diff's context lines
    ARE the changed files: do not Read a changed file separately unless a
    hunk you must judge is cut off mid-function — and say so in your report.
    Do not re-run git commands.

    Your review is read-only. Do not mutate the working tree, the index,
    HEAD, or branch state.

    ## Shared Files

    Some files are touched by multiple features: orchestrators, runtimes,
    shared type definitions, wiring layers. Changes to these files in the
    diff are EXPECTED — they are not scope drift.

    Rules for shared files:
    - Do NOT flag shared-file changes as out-of-scope
    - Do NOT recommend reverting shared-file changes
    - If a shared-file change looks unrelated to this sprint's tasks,
      flag it as a ⚠️ integration note, not a Critical/Important finding
    - If uncertain whether a change is shared or accidental, escalate to
      the controller for a cross-sprint integration check

    The controller decides whether shared-file changes need coordination.
    The reviewer's job is to verify correctness of the changes present,
    not to police whether they belong.

    ## Do Not Trust the Report

    Treat the implementer's report as unverified claims. Verify claims
    against the diff. Design rationales are claims too — judge the code
    on its merits. This applies doubly to Part 4 below: a report that
    *says* tests are real, exit criteria passed, or a bug is fixed is a
    claim to check, not a fact to accept.

    ## Tests

    The implementer already ran tests and reported results. Do not re-run
    the suite. Run a test only when reading the code raises a specific
    doubt that no existing run answers — and then a focused test, never
    a package-wide suite.

    ## Part 1: Spec Compliance

    For each task in the sprint brief, check against the diff:

    - **Missing:** requirements skipped, missed, or claimed without implementing
    - **Extra:** features not requested, over-engineering, unneeded "nice to haves"
    - **Misunderstood:** right feature built the wrong way, wrong problem solved

    Also verify:
    - All failure modes (F-ids) from the brief are addressed
    - All security risks (S-ids) from the brief are addressed
    - Exit criteria verification commands were run (check report for evidence)

    If a requirement cannot be verified from this diff alone, report it
    as a ⚠️ item.

    ## Part 2: Code Quality

    **Code quality:**
    - Clean separation of concerns?
    - Proper error handling?
    - DRY without premature abstraction?
    - Edge cases handled?

    **Tests:**
    - Do tests verify real behavior, not mocks?
    - Are the sprint's edge cases covered?
    - Is test output pristine (no stray warnings)?

    **Structure:**
    - Does each file have one clear responsibility?
    - Did this change create new files that are already large?
    - Is the implementation following existing codebase patterns?

    Point at evidence: file:line references for every finding.

    ## Part 3: Failure Modes & Security

    Cross-check the brief's failure modes and security risks:
    - F-id: was it addressed? How? Is the mitigation adequate?
    - S-id: was it addressed? How? Is the defense contract met?

    A failure mode or security risk left unaddressed is an Important finding.

    ## Part 4: Integrity Check

    This is a distinct pass from Part 2's code quality — quality asks "is
    it good code," integrity asks "does the diff actually do what the
    report and the tests claim it does." Read every changed test file and
    every changed error-handling path specifically looking for these
    patterns. Any confirmed instance is **Critical regardless of whether
    the sprint otherwise looks done** — an integrity finding means the
    green checkmark itself can't be trusted, which outranks normal
    severity.

    Look for:

    - **Fake or vacuous tests** — assertions that can't fail (`assert
      True`, `expect(x).toBeDefined()` on a value that's always defined),
      tests that call the code but assert nothing meaningful about its
      output, tests mocked so heavily that the real code path under test
      never executes.
    - **Symptom fixes instead of root-cause fixes** — a bug report or
      failing test addressed by suppressing the symptom (broad
      `except: pass`, swallowing an error and returning a default,
      catching a specific exception just to stop it from surfacing)
      rather than fixing what produced it. Ask: does this change make the
      underlying condition impossible, or just make it quieter?
    - **Overfitting to the test case** — logic that special-cases the
      exact input(s) used in the test (hardcoded return values,
      `if input == <test fixture value>`) rather than implementing the
      general behavior the task asked for.
    - **Disabled or narrowed checks without a stated reason** — a test
      skipped (`@skip`, `xit`, commented out), a CI check disabled, an
      assertion loosened (exact match → substring, strict → lenient) with
      no explanation in the diff or report for why the original check was
      wrong.
    - **Claimed-but-absent verification** — the report states exit
      criteria passed, a failure mode was tested, or a command was run,
      but the diff shows no corresponding test, or the described
      command/output doesn't match what the diff could actually produce.
    - **Scope quietly redefined as done** — a task's acceptance criteria
      narrowed in the implementation (e.g. "handle all input types" built
      for only the common case) without flagging the gap in the report as
      a concern or BLOCKED item.

    A pattern above is only a finding when it lacks a concrete, stated
    reason in the diff or report. An `except` that logs, re-raises, or
    handles a genuinely expected condition is not a violation — the test
    is whether there's a real justification on record, not whether the
    pattern's shape matches the list.

    ## Calibration

    - **Critical:** Incorrect or fragile behavior, missed requirements,
      swallowed errors, tests that assert nothing, any confirmed Part 4
      integrity finding
    - **Important:** This sprint cannot be trusted until fixed. Missing
      failure mode handling, unaddressed security risks, maintainability
      damage
    - **Minor:** Coverage could be broader, polish suggestions

    Acknowledge what was done well before listing issues.

    ## Output Format

    ### Spec Compliance

    - ✅ Sprint spec compliant | ❌ Issues found: [what's missing/extra/
      misunderstood, with file:line references]
    - ⚠️ Cannot verify from diff: [requirements you could not verify]

    ### Strengths

    [What's well done? Be specific.]

    ### Issues

    #### Critical (Must Fix)
    #### Important (Should Fix)
    #### Minor (Nice to Have)

    For each issue: file:line, what's wrong, why it matters, how to fix.

    ### Failure Modes & Security

    | # | Addressed? | Adequate? | Notes |
    |---|------------|-----------|-------|
    | F1 | ✅/❌ | ✅/❌ | ... |
    | S1 | ✅/❌ | ✅/❌ | ... |

    ### Integrity Findings

    | Pattern | Location (file:line) | Evidence | Stated justification (if any) |
    |---|---|---|---|
    | e.g. Symptom fix | ... | ... | none / [quote] |

    If none found, write: "No integrity issues found — tests exercise
    real behavior, error handling addresses root causes, no claims in
    the report are contradicted by the diff."

    ### Assessment

    **Sprint quality:** [Approved | Needs fixes]
    **Reasoning:** [1-2 sentence technical assessment]
```

## Placeholders

- `[BRIEF_FILE]` — REQUIRED: the sprint brief (same file the implementer used)
- `[REPORT_FILE]` — REQUIRED: the implementer's report
- `[DIFF_FILE]` — REQUIRED: review package file (generated via `script/generate-diff.sh`)
- `[GLOBAL_CONSTRAINTS]` — binding requirements from roadmap (exact values, formats, relationships)

## Reviewer Returns

Spec Compliance verdict (✅/❌/⚠️), Strengths, Issues (Critical/Important/Minor),
Failure Modes & Security table, Integrity Findings table, Sprint quality verdict.