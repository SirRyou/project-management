# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added a five-phase Deep Plan lifecycle with persisted intent, grounding, and risk evidence.
- Added the Plan Challenger role and plan-review gate before implementation.
- Added task-declared verification modes, explicit dependency readiness, isolated worker integration, resume checkpoints, and bounded remediation states.
- Added the Code Auditor contract with separate Standards and Spec review axes.
- Added agent-facing Codex multi-agent configuration guidance.
- Added PM-owned `execution-state.json` with atomic event updates, guarded task transitions, reviewer fan-in records, integration evidence, and generated ledger projections.
- Added deterministic Deep Plan automation for workspace scaffolding, Tier 3/DAG validation, ledger synchronization, readiness reporting, guarded worktree creation, worker results, reviewer verdicts, and integrated verification.
- Added focused Python tests covering scaffold validation, DAG cycle rejection, worktree safety, incomplete review fan-in, and the completed task lifecycle.

### Changed

- Deep Plan now requires integrated-tree verification before unlocking dependent tasks.
- Audience adaptation changes visible detail only; planning rigor and evidence requirements remain consistent.
- Worker and specialist routing now derives from task metadata and the risk register.
- `progress-ledger.md` is now a generated human-readable projection of the canonical PM execution state; child agents return evidence but do not mutate execution state directly.

### Documentation

- Updated the Deep Plan Diátaxis documentation suite (`tutorial-deep-plan.md`, `howto-deep-plan.md`, `reference-deep-plan.md`, `explanation-deep-plan.md`) to reflect the hardened five-phase planning lifecycle, isolated worktree execution, multi-axis reviews, and ledger resume protocols.

## [3.0.0] - 2026-09-19

### Added

- **3-Tier Hierarchical Planning Architecture** (`skills/deep-plan/`): Replaced monolithic markdown files and awkward append-order layouts with a structured, decoupled 3-tier document hierarchy:
  - **Tier 1 (High-Level):** Epic Overview, Problem Statement, Business Objectives, and System Invariants (`templates/tier1-epic-template.md`).
  - **Tier 2 (Mid-Level):** Architecture Specifications, Component Boundaries, Sequence Diagrams, Interface Contracts, and Schema Migrations (`templates/tier2-module-template.md`).
  - **Tier 3 (Low-Level):** Atomic Worker Execution Cards (`templates/tier3-task-template.md`) specifying exact `path/to/file:line` targets, sad path defenses, and non-vacuous test commands.
  - **Execution DAG & Ledger:** Machine-readable dependency graph (`dependency-dag.json`) and progress matrix (`templates/progress-ledger-template.md`).
- **Swarm Orchestrator & Dual-Review Fan-Out** (`references/swarm-execution.md`):
  - Transitioned PM from code writer to orchestrator executing against `dependency-dag.json`.
  - Dispatches isolated Worker Implementer subagents using TDD (Red $\rightarrow$ Green $\rightarrow$ Refactor).
  - Automatically fans out two parallel reviewer subagents upon task completion: **Spec Compliance Reviewer** and **Adversarial Challenger**.
- **Specialist Agent Catalog & Task-Type Routing Table** (`references/agent-catalog.md`):
  - Catalog of 12 specialist subagent roles across planning, execution, verification, and post-execution.
  - Dynamic routing matrix that auto-assembles team compositions for New Features, Refactors, Bug Fixes, Performance, Security, and Docs/Migrations.
- **Install-Time Subagent Provisioning** (`bin/pm-skills.mjs` & `skills/deep-plan/subagents.json`):
  - `npx @sirryou/skill-library install` now auto-provisions specialist subagents natively into host platforms upon first download:
    - **OpenAI Codex:** Generates official `.toml` custom agent files into `~/.codex/agents/*.toml` (or `.codex/agents/` in workspace mode) with model and reasoning effort parameters.
    - **Google Antigravity:** Generates `.json` subagent manifests into `~/.gemini/antigravity-cli/subagents/` (or `.agents/subagents/`) and workspace discovery rules.
  - Added `--workspace` (`-w`) flag for project-local installation.

### Changed

- **Friction Reduction & Intake Protocol** (`references/intake-and-grounding.md`): Replaced 5 conversational pauses with a single upfront `ask_question` intake modal establishing Autonomy Mode (`Autonomous` vs `Collaborative`) and Epic nature.
- **Codebase Grounding:** Replaced direct file reading in the PM context with an isolated, read-only **Codebase Explorer** subagent that compiles a Grounding Dossier.

### Removed

- Removed obsolete legacy workflow guides and diff bash scripts: `references/scope-analysis.md`, `references/gap-analysis.md`, `references/roadmap-draft.md`, `references/adversarial-review.md`, `references/execution-handoff.md`, `references/quick-path.md`, `references/quality-gates.md`, `script/generate-diff.sh`, and `templates/roadmap-template.md`.

## [2.4.0] - 2026-08-03

### Changed

- **Roadmap template flipped to match the new incremental-write output** (`templates/roadmap-template.md`): The template is now an append-order skeleton matching what Phases 1-4 actually produce, instead of a strict final layout. Consumers (execution handoff, retro) locate sections by heading, not position. All phase blocks demoted to `##` (no H1 breaks): Phase 1 block, `## Phase 2: Gap Analysis`, `## Phase 3: Roadmap`, `## Phase 4: Findings & Amendments`.
- **Progressive-write contract codified** (SKILL.md): Each phase appends its own section in place; earlier phase blocks are not restructured when later phases append.
- **Required-section quality gate** (`quality-gates.md`): Template match now checked **by heading presence**, not physical order. Same required sections apply to Quick Path output.
- **Cross-Cutting Work restored**: Reintroduced as a required section for integration / e2e / multi-sprint tasks; each Work Stream must own its own minimal unit tests.
- **Execution handoff: atomic decomposition + immediate escalation** (`execution-handoff.md`): Controller decomposes oversized Phase 3 tasks into atomic sub-tasks in the brief; implementers report `BLOCKED` immediately on critical/impossible work instead of grinding through a known-bad sprint.
- **Quick Path aligned** (`quick-path.md`): Now emits the canonical H2 heading scheme instead of a divergent inline template, so downstream consumers treat it identically to Full Path output.

### Changed
- **Gap-analysis Focus Rule extended**: Failure handlers must be traced against production state transitions, not just test state — a guard written for test-only state can dead-code the real path.
- **Test non-vacuity** enforced as a quality gate: new tests guarding failure handlers must fail against pre-fix code.
- **UI review adds CSS coverage check**: every `className` must map to a defined CSS rule.
- **Implementer prompt updated**: explicit scope-discipline rule against refactoring adjacent out-of-scope code; execution-handoff adds "adjacent-code refactors" anti-pattern with controller diff-check step.
- **Reference path fixes**: quality-gates and roadmap-draft links corrected to `../templates/roadmap-template.md`.

## [2.3.1] - 2026-08-02

### Added
- **Config-First Outside Voice Activation** (Phase 4): Replaced fragile environment auto-probing with a user-config query at the start of Phase 4 to declare reviewer engines.
- **Sequential review flow with scope feedback**: Configured Eng Review (Pass 2) to run after CTO Review (Pass 1) so it can analyze the technical and dependency impact of high-level CTO recommendations (e.g., prunings or deletions).
- **Manual review fallback**: Added copyable CLI review prompts in chat for the "none" engine selection, allowing users to run manual adversarial checks instead of skipping Phase 4 entirely.
- **Restructuring step to roadmap draft** (Phase 3): Added Step 3.0 to guide the transition from the Phase 2 progressive append layout into the unified, nested layout defined in `templates/roadmap-template.md`.

### Changed
- **UI/UX Review triggering**: Moved the conditional UI/UX review from Phase 5 (Quality Gate) to Phase 4 (Adversarial Review) so UI/UX findings are evaluated and approved in a single unified checkpoint.
- **Reference path updates**: Aligned script paths in handoff documents to point to `skills/deep-plan/script/generate-diff.sh` instead of `script/generate-diff.sh`.

## [2.3.0] - 2026-07-25

### Added

- **Sprint-based execution dispatch**: Replaced Workstream-bound subagent dispatch with Sprint-scoped ordering to preserve task dependency order across multi-sprint roadmaps.
- **Automated diff generation tool** (`skills/deep-plan/script/generate-diff.sh`): Helper script with git ancestor validation (`git merge-base --is-ancestor`) to safely generate raw diff packages for reviewer handoffs.
- **Subagent integrity audit pass**: Added strict verification in `reviewer-prompt.md` and `implementer-prompt.md` to catch anti-patterns like assertion-free tests, symptom masking, and test fixture overfitting.
- **Staging guardrails**: Explicit `git add <file>` requirements in implementer prompts to prevent unintended commits of untracked assets.

### Fixed

- Fixed CLI flag parsing and validation in `generate-diff.sh` to support `--ws-lane` and sprint-only invocations.

## [2.2.1] - 2026-07-20

### Added

- **BLOCKER gap tag** (Phase 2): New tag for items that block execution until resolved (external dependency, env config, access grant).
- **WS-level subagent dispatch**: Execution-handoff rewritten with per-workstream dispatch-review loop instead of per-task.
- **Implementer prompt template** (`implementer-prompt.md`): WS-scoped subagent prompt with failure mode/security reporting.
- **Reviewer prompt template** (`reviewer-prompt.md`): WS-scoped subagent prompt with three-part review (spec compliance, code quality, failure modes & security).
- **Progress ledger** (`.deep-plan/handoff/progress.md`): Durable task tracking that survives context compaction.
- **Artifact layout**: Explicit paths for briefs, diffs, reports, and reviews under `.deep-plan/handoff/`.
- **Pre-flight scan**: Checks for plan contradictions before execution begins.

### Changed

- **Execution path classifier**: Replaced file-count metric with decision-point model (logic sequencing, state/invariant impact, uncertainty/risk, security surface).
- **Execution handoff**: Now includes concrete controller steps for brief extraction and diff generation.
- Updated all docs to reflect new tags, classifier, and handoff workflow.

## [2.1.0] - 2026-07-16

### Added

- **Investigate skill**: Systematic debugging methodology that traces from symptom to root cause, designs structural fixes, and promotes learnings to prevent recurrence.
  - Iron Law: No fixes without root cause investigation and invariant verification.
  - 5-phase workflow: Root Cause Investigation → Systemic Audit & Hypotheses → Hypothesis Testing → Structural Resolution → Verification & Memory Promotion.
  - 3-strike rule: 3 failed hypotheses → STOP and escalate.
  - Minimal diff: fewest files, fewest lines. Don't refactor adjacent code.
  - Regression test required: must fail without fix, pass with fix.
  - Debug report format for structured output.
  - Graceful degradation when capabilities are missing.

- **Comprehensive documentation** following the Diataxis framework:
  - Tutorials for all three skills (tree-of-work, deep-plan, investigate).
  - How-To guides for common workflows.
  - Reference documentation for complete technical descriptions.
  - Explanation documentation for design rationale and trade-offs.
  - All documentation cross-linked for discoverability.

- **Skill routing rules** added to CLAUDE.md for automatic skill invocation.

### Changed

- Updated marketplace.json and plugin.json to include investigate skill.
- Bumped version from 2.0.0 to 2.1.0.

## [2.0.0] - 2026-07-15

### Added

- **Deep Plan skill**: Phased planning with adversarial review for complex features.
  - 5-phase workflow: Understand Scope → Enumerate Gaps → Draft Roadmap → Adversarial Review → Finalize Roadmap.
  - Quick Path (3 steps) for simple epics, Full Path (5 phases) for complex ones.
  - Three-lens gap analysis: Problem-Fit, Resilience, Security.
  - "Outside voice" adversarial review using different model providers.
  - Auto-escalation when complexity exceeds thresholds.
  - Non-linear flow support (jump back, skip phases).
  - Graceful degradation when capabilities are missing.

- **Tree of Work skill**: Focus enforcement and context recovery for agents.
  - Iron Law: One ACTIVE task at all times.
  - Status model: ACTIVE, PARKED, BLOCKED, TODO, DONE.
  - Core rules: ephemeral first, update as you work, park before switching, scope gate, validate before DONE.
  - Context recovery for resuming sessions.
  - Sub-agent delegation protocol.
  - Focus traps and mitigations.
  - Clarification protocol for handling ambiguity.

### Changed

- Initial release of the project management skill library.

## [1.0.0] - 2026-07-14

### Added

- Initial repository setup.
- License (MIT).
- README.md with project overview.
