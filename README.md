# Project Management Skills for AI Agents

A collection of agent skills for task tracking, focus enforcement, debugging, and complex feature planning. Designed to work with any AI coding agent.

## Skills

| Skill | Purpose | Use When |
|-------|---------|----------|
| **[tree-of-work](skills/tree-of-work/)** | Focus enforcement and context recovery | Multi-task work, session handoffs, preventing drift |
| **[deep-plan](skills/deep-plan/)** | Security-aware feature planning | Planning features spanning multiple files or work streams |
| **[investigate](skills/investigate/)** | Systematic debugging methodology | Bug reports, errors, regressions, "why is this broken" |

## Installation

### Claude Code (Plugin)

```bash
/plugin marketplace add SirRyou/project-management
/plugin install project-management@project-management
```

### Any Agent (Manual)

```bash
git clone https://github.com/SirRyou/project-management.git
cp -r project-management/skills/* ~/.claude/skills/
```

## Updating

### npx (Recommended)

```bash
# First time install
npx @sirryou/skill-library install

# Check for updates
npx @sirryou/skill-library check

# Update to latest
npx @sirryou/skill-library update
```

### Claude Code (Plugin)

```bash
/plugin uninstall project-management
/plugin install project-management@project-management
```

### Manual

```bash
cd project-management
git pull origin master
cp -r skills/* ~/.claude/skills/
```

### Publishing Updates (Maintainers)

```bash
# Bump version in package.json and plugin.json
npm version patch  # or minor, major
npm publish --access public
```

## Design Philosophy

These are **behavioral skills**, not tools. They tell agents how to think about problems — they don't impose specific file formats, directory structures, or CLI tools.

- **Portable**: Work across any agent runtime (Claude Code, Cursor, Copilot, Codex, Gemini CLI)
- **Declarative**: Define triggers, rules, and workflows in markdown
- **Runtime-agnostic**: Delegate persistence to platform-native tools
- **Composable**: Load references on-demand, not in bulk

Each skill declares what it needs from the runtime (`requires` and `capabilities` in frontmatter) and degrades gracefully when capabilities are missing.

## Skill Details

### Tree of Work

Focus enforcement and context recovery for agents.

**Core rules:**
- One ACTIVE task at all times
- Park before switching tasks
- Scope gate every change outside your current task
- Update progress as you work, not at the end

**Key references:**
- `CLASSIFICATION.md` — PARKED vs BLOCKED decision tree, edge cases
- `TRAPS.md` — Common focus drift traps with concrete mitigations
- `ANTI_PATTERNS.md` — Substitution Test, silent branching, double-active

→ [Full Documentation](skills/tree-of-work/README.md)

### Deep Plan

Phased planning with adversarial review for complex features.

**Workflow:**
1. Understand Scope → 2. Enumerate Gaps (3 lenses) → 3. Draft Roadmap → 4. Adversarial Review → 5. Finalize

**Key features:**
- Quick Path (3 steps) for simple epics, Full Path (5 phases) for complex ones
- "Outside voice" adversarial review using different model providers
- Problem-fit, resilience, and security analysis in parallel
- Auto-escalation when complexity exceeds thresholds

→ [Full Documentation](skills/deep-plan/README.md)

### Investigate

Systematic debugging: trace from symptom to root cause, fix the cause, prove the fix.

**Workflow:**
1. Root Cause Investigation → 2. Pattern Analysis → 3. Hypothesis Testing → 4. Implementation → 5. Verification

**Iron Law:** No fixes without root cause investigation first.

**Key rules:**
- 3-strike rule: if 3 hypotheses fail, escalate
- Minimal diff: fewest files, fewest lines
- Regression test must fail without fix and pass with fix
- Never say "this should fix it" — verify and prove it

→ [Full Documentation](skills/investigate/README.md)

## Project Structure

```
project-management/
├── skills/
│   ├── tree-of-work/           # Focus enforcement
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   └── references/         # Classification, traps, anti-patterns
│   ├── deep-plan/              # Feature planning
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   ├── references/         # Phase-specific guides (9 files)
│   │   └── templates/          # Roadmap template
│   └── investigate/            # Debugging methodology
│       ├── SKILL.md
│       ├── README.md
│       └── runtime-bindings.md # Platform-specific glue template
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── README.md
├── CLAUDE.md
└── LICENSE
```

## Documentation

Comprehensive documentation for each skill follows the [Diataxis framework](https://diataxis.fr/) — four quadrants serving different reader needs:

### Tree of Work
- **[Tutorial](docs/tutorial-tree-of-work.md)** — Walk-through from setup to first working example
- **[How-To Guide](docs/howto-tree-of-work.md)** — Task-oriented instructions for common workflows
- **[Reference](docs/reference-tree-of-work.md)** — Complete technical description of all concepts
- **[Explanation](docs/explanation-tree-of-work.md)** — Design rationale and trade-offs

### Deep Plan
- **[Tutorial](docs/tutorial-deep-plan.md)** — Plan a feature from scratch with adversarial review
- **[How-To Guide](docs/howto-deep-plan.md)** — Task-oriented instructions for planning workflows
- **[Reference](docs/reference-deep-plan.md)** — Complete technical description of all phases
- **[Explanation](docs/explanation-deep-plan.md)** — Design rationale and trade-offs

### Investigate
- **[Tutorial](docs/tutorial-investigate.md)** — Debug a bug from symptom to fix
- **[How-To Guide](docs/howto-investigate.md)** — Task-oriented instructions for debugging workflows
- **[Reference](docs/reference-investigate.md)** — Complete technical description of all phases
- **[Explanation](docs/explanation-investigate.md)** — Design rationale and trade-offs

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

## License

MIT
