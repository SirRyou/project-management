# Tier 3: Atomic Task Specification — T{n}: [Task Name]

> Dispatched to one worker in an isolated worktree. Define one independently verifiable behavioral or contract change.

## 1. Task Metadata

- **Task ID:** T{n}
- **Parent Module:** `modules/M{m}-[name].md`
- **Intent Trace:** `00-intent.md#[section]`
- **Invariant Trace:** `[INV-x]`
- **Risk Trace:** `02-risk-register.md#[risk-id]` or `N/A`
- **Kind:** `research` | `implementation` | `migration` | `documentation` | `benchmark` | `configuration`
- **Verification Mode:** `behavioral-tdd` | `migration` | `static-config` | `documentation` | `benchmark` | `repository-specific`
- **Prerequisite Tasks:** `[T01]` or `None`
- **Target Files and Symbols:** `[explicit paths and functions, schemas, or sections]`
- **Completion Criterion:** `[one observable result]`
- **Plan-Revision Trigger:** `[evidence that must stop execution and return the card to the PM, or N/A with reason]`

## 2. Dependency and Output Contract

- **Required Artifacts or Contracts:** `[what must already exist and be integrated]`
- **Expected Outputs:** `[commit, generated files, migration, docs, measurement, or report]`
- **Downstream Consumers:** `[tasks or modules that consume this result]`

## 3. Implementation Directive

1. Confirm prerequisite artifacts and repository state.
2. Follow the ordered steps below without assuming unfinished work will supply missing behavior.
3. Preserve linked invariants and document any necessary assumption.
4. Stop and return the task to the PM if a prerequisite is absent, the parent contract is ambiguous or false, target ownership conflicts, or the task no longer has one completion criterion. Do not silently widen or re-decompose it.

- **Step 1:** `[path/symbol and action]`
- **Step 2:** `[path/symbol and action]`
- **Step 3:** `[integration or output action]`

## 4. Sad Paths and Failure Defenses

| Failure / Abuse Vector | Detection Point | Defense / Fallback Action |
| :--- | :--- | :--- |
| `[failure]` | `[detection]` | `[defense]` |

## 5. Acceptance and Verification

- **Acceptance Criteria:**
  1. `[criterion]`
  2. `[criterion]`
- **Verification Command(s):**
  ```bash
  [exact command]
  ```
- **Expected Evidence:** `[exit code, output, artifact, measurement, or review result]`
- **Non-Vacuity or Applicability Note:** `[why this verifies behavior, or why another mode applies]`
- **Plan Revision Evidence:** `[N/A, or the evidence returned to the PM if execution must stop]`
- **Quality Checks:** `[lint/typecheck/format/docs checks, or N/A with reason]`
