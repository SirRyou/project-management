# Contributing to Project Management Skills

Thank you for your interest in contributing! This guide will help you get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/project-management.git`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Test with your AI agent
6. Submit a pull request

## Development Setup

No build step required. Skills are behavioral specifications in markdown, not executable code.

### Testing Skills

1. Install the skill in your agent's skill directory
2. Activate the skill using its triggers
3. Verify the agent follows the workflow correctly
4. Test edge cases and error conditions

### Running Evals

```bash
# Tree of Work evals + integration tests
python skills/tree-of-work/evals/test_runner.py
```

## Skill Guidelines

### File Structure

Each skill follows this structure:

```
skills/
├── skill-name/
│   ├── SKILL.md           # Behavioral spec (the skill)
│   ├── README.md          # Skill documentation
│   └── references/        # Context-specific guides (optional)
│       └── *.md
```

### SKILL.md Format

Every skill is a `SKILL.md` with YAML frontmatter followed by markdown content:

```markdown
---
name: skill-name
description: >
  One-line description of what the skill does.
triggers:
  - "trigger phrase 1"
  - "trigger phrase 2"
requires:
  - file-read
  - file-write
  - question
capabilities:
  optional:
    - subagent
    - git
---

# Skill Name

[Content defining triggers, rules, workflows, and boundaries]
```

### Design Principles

1. **Behavioral, not tool-based**: Skills tell agents how to think, not where to write files.
2. **Portable**: Work across any agent runtime (Claude Code, Cursor, Copilot, Codex, Gemini CLI).
3. **Declarative**: Define triggers, rules, and workflows in markdown.
4. **Runtime-agnostic**: Delegate persistence to platform-native tools.
5. **Composable**: Load references on-demand, not in bulk.

### What Belongs in SKILL.md

- The behavioral methodology (iron laws, core rules, workflows)
- Generic advice that applies everywhere
- Triggers and activation conditions
- Status models and decision trees
- Scope boundaries (what the skill does and doesn't do)

### What Does NOT Belong in SKILL.md

- Platform-specific tool names
- Configuration paths
- Telemetry calls
- Anything that would be different on another platform

### Runtime Bindings

If you need platform-specific behavior, create a `runtime-bindings.md` file:

```markdown
# Skill Name — PLATFORM Runtime Bindings

## Tool mapping

| Generic capability | PLATFORM tool name |
|---|---|
| file-read | Read |
| file-write | Write / Edit |
| bash | Bash |
| grep | Grep |
| question | AskUserQuestion (or prose fallback) |

## Telemetry

[PLATFORM-specific analytics logging here]

## State persistence

[How this platform stores learnings, notes, session history]

## Integration hooks

[PLATFORM-specific features: scope lock, checkpoint mode, etc.]
```

## Documentation Guidelines

### Diataxis Framework

All documentation follows the [Diataxis framework](https://diataxis.fr/):

- **Tutorial**: Learning-oriented, walks a newcomer through a working example step-by-step.
- **How-To**: Task-oriented, shows how to accomplish a specific goal (assumes basic familiarity).
- **Reference**: Information-oriented, complete and accurate technical description.
- **Explanation**: Understanding-oriented, explains why things work the way they do.

### Documentation Structure

```
docs/
├── tutorial-*.md          # Tutorials for each skill
├── howto-*.md             # How-To guides for each skill
├── reference-*.md         # Reference docs for each skill
└── explanation-*.md       # Explanation docs for each skill
```

### Writing Style

- Lead with the point. Say what it does, why it matters, and what changes for the builder.
- Be concrete. Name files, functions, line numbers, commands, outputs.
- Tie technical choices to user outcomes.
- Be direct about quality. Bugs matter. Edge cases matter.
- Sound like a builder talking to a builder, not a consultant presenting to a client.
- Never corporate, academic, PR, or hype.
- No em dashes. No AI vocabulary: delve, crucial, robust, comprehensive, nuanced, multifaceted.

## Pull Request Process

1. **Update documentation** if you change behavior.
2. **Test with your AI agent** to verify the skill works as intended.
3. **Update CHANGELOG.md** with your changes.
4. **Submit a pull request** with a clear description of what you changed and why.

### PR Description Template

```markdown
## What

[One sentence: what changed]

## Why

[Why this change was needed]

## How

[How the change works]

## Testing

[How you tested the change]

## Documentation

[What documentation was added/updated]
```

## Code of Conduct

Be kind. Be constructive. Focus on making the skills better for everyone.

## Questions?

Open an issue or start a discussion on GitHub.
