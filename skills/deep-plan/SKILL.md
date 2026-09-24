---
name: deep-plan
description: >
  Use when planning and executing complex features, multi-file refactors, database schema migrations,
  or architectural changes requiring structured decomposition and multi-agent coordination.
---

# Deep Plan

## Overview

Deep Plan guides complex engineering work through a persisted evidence trail and a five-phase planning lifecycle. Keep user intent, repository facts, risks, architecture, atomic tasks, dependencies, review evidence, and execution state linked. Use the main agent as PM / Orchestrator for planning, integration, and user communication; keep production implementation in worker contexts.

## When to Use

- Changes spanning multiple modules or with complex dependency sequencing.
- Database schema migrations, state mutations, or persistent invariant changes.
- Auth boundaries, permission updates, or security-sensitive workflows.
- High-uncertainty features requiring codebase grounding and adversarial stress-testing.

## When NOT to Use

- Single-file edits, trivial bug fixes, documentation, or styling tweaks. Run a lightweight preflight first; if the work remains simple, use the repository's direct workflow.

## Agent Roles

| Role | Responsibility | Reference |
| :--- | :--- | :--- |
| **PM / Orchestrator** | Coordinates artifacts, DAG, ledger, integration, and user interaction | Main thread |
| **Codebase Explorer** | Maps architecture, dependencies, conventions, and blast radius | [codebase-explorer.md](references/subagents/codebase-explorer.md) |
| **System Architect** | Defines Tier 2 boundaries, contracts, data flow, and schemas | [system-architect.md](references/subagents/system-architect.md) |
| **Task Decomposer** | Creates atomic Tier 3 cards and the dependency DAG | [task-decomposer.md](references/subagents/task-decomposer.md) |
| **Plan Challenger** | Challenges scope, assumptions, risks, dependencies, and verification before execution | [plan-challenger.md](references/subagents/plan-challenger.md) |
| **Worker Implementer** | Executes a ready Tier 3 task in an isolated worktree | [worker-implementer.md](references/subagents/worker-implementer.md) |
| **Code Auditor** | Runs Standards and Spec review axes for code changes | [spec-reviewer.md](references/subagents/spec-reviewer.md) |
| **Adversarial Challenger** | Stress-tests implementation invariants and sad paths | [adversarial-challenger.md](references/subagents/adversarial-challenger.md) |

Use Security Architect, Security Auditor, Performance Engineer, Performance Benchmarker, Researcher, and Documentation Writer when the risk-and-task routing matrix activates them.

## Five-Phase Planning Lifecycle

```mermaid
flowchart TD
    Start(["Start /deep-plan"]) --> P1["1. Intent and entry preflight"]
    P1 --> P2["2. Grounding, gaps, and risks"]
    P2 --> P3["3. Draft Tier 1 -> Tier 2 -> Tier 3"]
    P3 --> P4["4. Adversarial plan review"]
    P4 --> P5["5. Finalize and approve plan"]
    P5 --> P6["Execution workflow"]
    P6 --> Done(["Epic completed and verified"])
```

### Automation CLI Location

The deterministic state machine script is located at `<skill-dir>/script/deep_plan.py` relative to this skill's installation directory. Always execute CLI commands from the target repository root (containing `.deep-plan/`) using `python "<skill-dir>/script/deep_plan.py" <command> <epic-slug> [options]`.

### Phase 1: Intent and Entry Preflight

- Read [intake-and-grounding.md](references/intake-and-grounding.md).
- Infer communication depth from the request; do not ask the user to classify themselves.
- Ask for autonomy mode and task type only when the request does not establish them.
- Build and persist an intent dossier containing goals, behaviors, invariants, outputs, constraints, assumptions, and unresolved decisions.
- After selecting a safe epic slug, initialize the artifact workspace with `python "<skill-dir>/script/deep_plan.py" init <epic-slug>`. Run `validate <epic-slug> --stage scaffold` before writing plan artifacts.
- Treat `.deep-plan/<epic-slug>/execution-state.json` as PM-owned canonical state. Workers and reviewers return evidence; only the PM / Orchestrator mutates state through the automation CLI. `progress-ledger.md` is a generated projection.
- Run a lightweight preflight before committing to the full workflow. If grounding later proves the request simple, present the direct-implementation versus full-plan choice and record the decision.

### Phase 2: Grounding, Gaps, and Risks

- Use repository-provided mapping tools first. If unavailable, dispatch the Codebase Explorer with a thorough file-and-line evidence mandate.
- Persist the Grounding Dossier with stack, architecture, conventions, affected modules, dependencies, and coverage gaps.
- Enumerate unknowns and create a risk register before architecture design.
- Resolve external-library unknowns through documentation research or record explicit research tasks.
- Finalize complexity after grounding using dependency breadth, uncertainty, change risk, verification cost, and coordination cost.

### Phase 3: Tiered Planning

- Read [tiered-planning.md](references/tiered-planning.md).
- The PM / Orchestrator creates `03-tier1-epic.md` in `.deep-plan/<epic-slug>/` before dispatching planning roles. Every dispatch must name the epic slug and provide the exact relative paths below; never tell a fresh subagent only to "read Tier 1" or "read the grounding dossier."
  - Intent: `.deep-plan/<epic-slug>/00-intent.md`
  - Grounding: `.deep-plan/<epic-slug>/01-grounding.md`
  - Risk register: `.deep-plan/<epic-slug>/02-risk-register.md`
  - Tier 1 epic: `.deep-plan/<epic-slug>/03-tier1-epic.md`
  - Tier 2 modules: `.deep-plan/<epic-slug>/modules/`
  - Tier 3 task cards: `.deep-plan/<epic-slug>/tasks/`
  - Dependency DAG: `.deep-plan/<epic-slug>/dependency-dag.json`
  - ID ledger: `.deep-plan/<epic-slug>/tasks/ID-LEDGER.md`
- **Freeze the inter-module contract registry (§6 of `03-tier1-epic.md`) and the ID ledger before dispatching any architect or task decomposer.** A module architect fanned out against a moving contract writes against a snapshot that will drift; the resulting contradictions are invisible to `validate` and surface only at integration. The PM owns both artifacts; neither is authored by a subagent.
- Generate Tier 1 scope and invariants, Tier 2 architecture contracts, Tier 3 atomic tasks, `dependency-dag.json`, and `progress-ledger.md`.
- When fanning out more than one Task Decomposer, give each a **disjoint task-ID range** and forbid renumbering within a range another agent may have referenced. Never let a decomposer glob `tasks/T*.md`.
- Link every tier to the intent dossier, grounding evidence, and relevant risks.
- Treat a task as atomic when it is one independently verifiable behavioral or contract change. File count is a heuristic, not a hard limit.
- Run `python "<skill-dir>/script/deep_plan.py" sync-ledger <epic-slug>` after updating the DAG, then run `python "<skill-dir>/script/deep_plan.py" validate <epic-slug>`. Correct structural errors before plan review.

### Phase 4: Adversarial Plan Review

- Read [plan-review.md](references/plan-review.md) — it owns the canonical challenge checklist. The Plan Challenger may also consult [resilience-first-development.md](references/resilience-first-development.md) for resilience-specific criteria.
- Dispatch the Plan Challenger against scope, assumptions, architecture, risks, dependency readiness, acceptance criteria, and verification feasibility.
- When a boundary-changing architecture fork is found, pause and use the question tool to synchronize the decision with the user. Present a recommendation and concrete tradeoffs.

### Phase 5: Finalize and Approve the Plan

- Run `python "<skill-dir>/script/deep_plan.py" validate <epic-slug>` to validate artifact links, task IDs, dependency references, DAG acyclicity, Tier 3 fields, and ledger initialization.
- In Collaborative Mode, require explicit user approval after the complete Tier 1, Tier 2, and Tier 3 plan.
- In Autonomous Mode, proceed after validation unless a boundary-changing architecture fork requires user synchronization.

## Execution Workflow

- Read [swarm-execution.md](references/swarm-execution.md).
- Read [agent-catalog.md](references/agent-catalog.md) for role routing, [invocation-contracts.md](references/invocation-contracts.md) for child prompts, and [codex-multi-agent.md](references/codex-multi-agent.md) when the active runtime is Codex.
- Read [automation.md](references/automation.md) when scaffolding a workspace, validating a plan, selecting ready tasks, or provisioning a worker worktree.
- Begin every dispatch loop with `python "<skill-dir>/script/deep_plan.py" status <epic-slug>` and `python "<skill-dir>/script/deep_plan.py" ready <epic-slug>`. Create a worker worktree only with `python "<skill-dir>/script/deep_plan.py" worktree-create <epic-slug> <task-id> --parent <parent-ref>` from a clean parent checkout.
- Record worker summaries with `worker-record` from `IN_PROGRESS` or `IN_REMEDIATION`; recording a remediation result clears the prior review round and returns the task to `IN_REVIEW`. Record reviewer verdicts with `review-record` and integration evidence with `integration-record` / `verify-record`. Use `transition` only from the parent PM checkout; never let a child agent edit execution state directly.
- Reopen a `BLOCKED` task only through `unblock <epic> <task-id> --reason ... --evidence ...` after its dependencies are completed and blocker-resolution evidence is stored inside the epic. Tasks with failed reviews, prior worker/integration artifacts, or exhausted remediation remain blocked until a formally revised plan is reviewed.
- Dispatch only tasks whose artifact and contract dependencies are completed and integrated.
- Use per-task worktrees or branches. Parallelize conservatively only when target ownership and integration risk are acceptable.
- Select verification from the task-declared mode. Apply TDD to code tasks; follow repository conventions for documentation and other non-code tasks.
- For code changes, require Code Auditor and Adversarial Challenger review. Add security or performance reviewers from the risk-and-task matrix.
- Integrate approved commits into the parent branch, run verification on the integrated tree, and only then unlock dependents.
- For deletion or migration tasks, require a clean tree and a recorded parity proof for the replaced behavior before the delete. Workers must never `git add`/`commit`/`reset`/`checkout`/`stash` the user's own work; they return to the PM if the tree is dirty. See [swarm-execution.md](references/swarm-execution.md).
- Maintain the ledger state machine and bounded remediation policy. When intentionally pausing, enforce worktree hygiene (ensure active workers commit WIP changes to prevent data loss), then execute `python "<skill-dir>/script/deep_plan.py" pause <epic-slug> --reason <reason>` with repeatable `--task-progress <task-id>:<completed-step>:<total-steps>` for every in-flight task. On session start, execute `python "<skill-dir>/script/deep_plan.py" resume <epic-slug>` for worktree reconciliation and session briefing. Resume from the ledger, DAG, plan artifacts, commit records, and handoff summary after quota exhaustion or session loss.
- Run Documentation Writer after implementation when public APIs, configuration, migrations, or breaking changes require documentation.

### Fan-Out and Fan-In Contract

The PM / Orchestrator owns dispatch, aggregation, integration, and ledger transitions. Child agents provide evidence; they do not unlock dependencies or mark DAG tasks complete.

1. **Fan out execution tasks only when safe:** select every `READY_TO_DISPATCH` task whose dependencies are integrated. Dispatch concurrently only when target ownership is disjoint and integration risk is explicitly acceptable; otherwise serialize. Give each worker its own worktree, task contract, relevant evidence, integration target, verification mode, and output contract.
2. **Fan out review per worker commit:** after a worker submits a commit, transition the task to `IN_REVIEW` and dispatch every reviewer activated by the risk matrix. Code changes require the Code Auditor's Standards and Spec axes plus the Adversarial Challenger; add security or performance reviewers when applicable. Reviewers inspect the exact worker commit and return task-scoped verdicts and findings.
3. **Fan in before integration:** wait until every required reviewer for that task has returned a verdict. Record each verdict and finding in the ledger. A single `PASS` is insufficient; any `FAIL` enters bounded remediation, and an unresolved or exhausted review path blocks the task.
4. **Integrate and verify the convergence point:** only after all required reviews pass, transition to `INTEGRATING`, merge or cherry-pick the approved worker commit into the parent branch, and run affected verification on the integrated tree. Record the integrated commit, verification evidence, reviewer verdicts, invariant impact, and ledger transition.
5. **Unlock only after fan-in is complete:** transition the task to `COMPLETED` only after integrated verification passes. Then recompute the DAG and mark a dependent `READY_TO_DISPATCH` only when all prerequisites are `COMPLETED` and integrated.

For independent `T03` and `T04`, the PM may dispatch both workers concurrently. Each worker receives its own review fan-out and integration gate; only after both integrated results are verified may a task depending on both be dispatched.

## Completion Evidence

Mark a task `COMPLETED` only after recording an evidence bundle containing the integrated commit, task verification, applicable quality checks, reviewer verdicts, invariant impact, and ledger update. Run repository-derived global verification after all tasks complete.

## Anti-Patterns to Avoid

- Do not implement production code in the PM context.
- Do not dispatch a task before every declared artifact and contract dependency is completed and integrated.
- Do not assume a failing or unfinished task will provide a future contract.
- Do not mark a task complete from reviewer PASS alone; integrate and verify the parent tree.
- Do not force red-green TDD onto documentation, configuration, migration, or benchmark tasks when another declared verification mode applies.
- Do not hide inferred invariants, architecture decisions, or risk acceptance; label assumptions and escalate boundary-changing forks.
