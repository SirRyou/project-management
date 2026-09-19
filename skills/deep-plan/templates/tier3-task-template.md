# Tier 3: Atomic Task Specification — T{n}: [Task Name]

> **Worker Execution Contract**
> Dispatched directly to a Worker Implementer Subagent. 
> Self-contained: requires no outside context beyond this spec and the parent Tier 2 contract.

---

## 1. Task Metadata
- **Task ID:** T{n}
- **Parent Module:** `modules/M{m}-[name].md`
- **Estimated Complexity:** [Low (Junior) | Mid (Mid-level dev)]
- **Prerequisite Tasks (Dependencies):** [e.g. `T01`, or `None`]
- **Target File(s):**
  - Primary: `path/to/file.ts` (Target Line: ~`120-160`)
  - Test: `tests/path/to/test.test.ts`

---

## 2. Implementation Directive (Step-by-Step)
1. **Pre-flight verification:** Confirm prerequisite files exist and current tests pass.
2. **Step 1:** In `path/to/file.ts`, implement function `[FunctionName](args: Type): ReturnType`.
3. **Step 2:** Integrate invariant check `[INV-x]`: verify [condition] before mutating state.
4. **Step 3:** Wire error handling for sad paths as specified below.

---

## 3. Sad Paths & Failure Defenses
*What can fail at runtime, and how the implementation must defend against it:*

| Failure / Abuse Vector | Detection Point | Defense / Fallback Action |
| :--- | :--- | :--- |
| [e.g. Null/Undefined input] | Entry guard in `FunctionName` | Throw structured `ValidationError`, do not execute |
| [e.g. Concurrency collision] | DB transaction / atomic write | Catch lock exception and trigger exponential retry |

---

## 4. Acceptance Criteria & Test Commands (Machine-Verifiable)

### TDD Non-Vacuity Verification
*Every new test guarding this feature must FAIL before code is written, proving it tests real behavior.*

1. **Write Test First:** Create / update test in `tests/path/to/test.test.ts`.
2. **Red Phase (Must Fail):** Run command:
   ```bash
   [exact test command e.g. npm test tests/path/to/test.test.ts]
   ```
   *Expected result: Fails due to missing implementation.*
3. **Green Phase (Must Pass):** Implement code and re-run:
   ```bash
   [exact test command e.g. npm test tests/path/to/test.test.ts]
   ```
   *Expected result: Passes with 0 errors.*
4. **Regression & Quality Gate:**
   ```bash
   [exact lint/typecheck command e.g. npm run lint && npm run typecheck]
   ```
   *Expected result: Clean exit code 0.*
