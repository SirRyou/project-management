# WS Reviewer Prompt Template

Use this template when dispatching a reviewer subagent for a workstream.
The reviewer reads the WS diff once and returns two verdicts: spec
compliance and code quality.

**Purpose:** Verify one workstream's implementation matches its requirements
(nothing more, nothing less) and is well-built (clean, tested, maintainable)

---

## Template

```
Subagent (general-purpose):
  description: "Review WS[n] (spec + quality)"
  prompt: |
    You are reviewing one workstream's implementation: first whether it
    matches its requirements, then whether it is well-built. This is a
    WS-scoped gate, not a merge review — a broad whole-branch review
    happens separately after all workstreams are complete.

    ## What Was Requested

    Read the WS brief: [BRIEF_FILE]

    Global constraints from the roadmap that bind this WS:
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

    ## Do Not Trust the Report

    Treat the implementer's report as unverified claims. Verify claims
    against the diff. Design rationales are claims too — judge the code
    on its merits.

    ## Tests

    The implementer already ran tests and reported results. Do not re-run
    the suite. Run a test only when reading the code raises a specific
    doubt that no existing run answers — and then a focused test, never
    a package-wide suite.

    ## Part 1: Spec Compliance

    For each task in the WS brief, check against the diff:

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
    - Are the WS's edge cases covered?
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

    ## Calibration

    - **Critical:** Incorrect or fragile behavior, missed requirements,
      swallowed errors, tests that assert nothing
    - **Important:** This WS cannot be trusted until fixed. Missing failure
      mode handling, unaddressed security risks, maintainability damage
    - **Minor:** Coverage could be broader, polish suggestions

    Acknowledge what was done well before listing issues.

    ## Output Format

    ### Spec Compliance

    - ✅ WS spec compliant | ❌ Issues found: [what's missing/extra/misunderstood,
      with file:line references]
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

    ### Assessment

    **WS quality:** [Approved | Needs fixes]
    **Reasoning:** [1-2 sentence technical assessment]
```

## Placeholders

- `[BRIEF_FILE]` — REQUIRED: the WS brief (same file the implementer used)
- `[REPORT_FILE]` — REQUIRED: the implementer's report
- `[DIFF_FILE]` — REQUIRED: review package file (git diff output)
- `[GLOBAL_CONSTRAINTS]` — binding requirements from roadmap (exact values, formats, relationships)

## Reviewer Returns

Spec Compliance verdict (✅/❌/⚠️), Strengths, Issues (Critical/Important/Minor),
Failure Modes & Security table, WS quality verdict.
