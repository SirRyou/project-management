# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **skill library for AI coding agents** — a collection of Claude Code skills (SKILL.md files) that provide project management, task tracking, planning, and communication capabilities. Skills are structured markdown files with YAML frontmatter that define triggers, rules, and workflows for agent behavior.

## Repository Structure

```
project-management/
├── .claude-plugin/
│   ├── marketplace.json                    # Marketplace catalog
│   └── plugin.json                         # Plugin manifest
├── skills/
│   ├── tree-of-work/                       # Task tracking skill
│   │   ├── SKILL.md
│   │   ├── scripts/                        # Python CLI tool
│   │   ├── evals/                          # Tests
│   │   └── references/                     # Context-specific guides
│   └── deep-plan/                          # Feature planning skill
│       ├── SKILL.md
│       ├── references/                     # Phase-specific guides
│       └── templates/                      # Roadmap templates
└── .agents/                                # Cavecrew skills (separate)
```

## Key Commands

### Tree of Work (task tracking)

```bash
# Initialize state (auto-absorbs legacy docs like TODO.md, ROADMAP.md, CLAUDE.md)
python skills/tree-of-work/scripts/tree_of_work.py init

# Check current state
python skills/tree-of-work/scripts/tree_of_work.py status
python skills/tree-of-work/scripts/tree_of_work.py status --json

# Validate state file (structure + security)
python skills/tree-of-work/scripts/tree_of_work.py validate

# Snapshot current state to history
python skills/tree-of-work/scripts/tree_of_work.py snapshot -m "message"

# Reset to default template
python skills/tree-of-work/scripts/tree_of_work.py reset

# Override state directory
python skills/tree-of-work/scripts/tree_of_work.py --state-dir PATH <command>
```

### Running Tests

```bash
# Tree of Work evals + integration tests
python skills/tree-of-work/evals/test_runner.py
```

## Architecture & Design Decisions

### Skill File Convention

Every skill is a `SKILL.md` with YAML frontmatter (`name`, `description`, `license`, `metadata`) followed by markdown content defining triggers, rules, workflows, and boundaries. Skills do NOT contain executable code — they are behavioral specifications for agents.

### Tree of Work — Ephemeral-First Design

State tracking starts in-memory and only materializes to disk when complexity triggers fire (branching, task transitions, sub-agent handoff, session end). The state file (`.agent/tree-of-work/current-state.md`) enforces exactly one ACTIVE task at a time.

The Python CLI handles: initialization, validation (including secret detection via Shannon entropy), snapshots, and legacy doc absorption.

Reference files under `skills/tree-of-work/references/` are loaded on-demand only when specific conditions are met — never bulk-load them. Total lines per session target: ~100-150.

### Deep Plan — 5-Phase Workflow

Phases: Understand Scope → Enumerate Gaps → Draft Roadmap → Adversarial Review → Finalize Roadmap. The skill supports quick path (simple epics) vs full path, with auto-escalation triggers. Phase 4 uses an "outside voice" principle — different model providers for adversarial review to catch blind spots.

## Important Constraints

- **Tree of Work**: Only one ACTIVE task at a time. `validate` fails if 2+ are ACTIVE.
- **Tree of Work**: Never commit secrets in state files. The script auto-redacts known patterns and blocks high-entropy strings.
- **Deep Plan**: Never begin implementation without explicit user confirmation after Phase 5.
