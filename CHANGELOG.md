# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
