# Project Management Skills for AI Agents

A collection of agent skills for task tracking, context recovery, and complex feature planning. Designed to work with any AI coding agent that supports the [Agent Skills](https://agentskills.io) open standard.

## Overview

| Skill | Purpose | Use When |
|-------|---------|----------|
| **[tree-of-work](skills/tree-of-work/)** | Hierarchical task tracking with context recovery | Managing multiple tasks, resuming sessions, coordinating sub-agents |
| **[deep-plan](skills/deep-plan/)** | Resilient, security-aware feature planning | Planning medium-to-large features, complex architectural decisions |

## Installation

### Claude Code (Plugin)

```bash
# Add the marketplace
/plugin marketplace add SirRyou/project-management

# Install the plugin
/plugin install project-management@project-management
```

Skills are namespaced as `project-management:tree-of-work` and `project-management:deep-plan`.

### Any Agent (Manual)

Clone and copy to your agent's skill directory:

```bash
git clone https://github.com/SirRyou/project-management.git
cp -r project-management/skills/* ~/.claude/skills/
```

Or use `npx skills add` for cross-agent support:

```bash
npx skills add SirRyou/project-management --skill tree-of-work
npx skills add SirRyou/project-management --skill deep-plan
```

## What Are Agent Skills?

Agent skills are structured markdown files (`SKILL.md`) with YAML frontmatter that define behavioral specifications for AI agents. They tell agents **how** to approach problems, not **what** code to write. The format is an [open standard](https://agentskills.io) supported by 30+ agent platforms.

Skills are:
- **Portable**: Work across Claude Code, Cursor, Copilot, Codex, Gemini CLI, and more
- **Declarative**: Define triggers, rules, and workflows in markdown
- **Composable**: Can be combined with other skills
- **Stateful**: Can track state across sessions

## Skill Details

### Tree of Work

Hierarchical task tracking with context recovery and sub-agent coordination.

**Key Features:**
- Ephemeral-first state tracking (in-memory until complexity triggers)
- Automatic legacy doc absorption (ROADMAP.md, TODO.md)
- Sub-agent isolation for parallel work
- Secret detection via entropy analysis
- Single ACTIVE task enforcement

**How to Use:**
- **Agent Invocation (Preferred):** Ask your AI agent to trigger it:
  > *"where was I"* or *"initialize task tracking"*
  The agent will automatically trigger the skill and execute commands.
- **Manual CLI (For Developers):** Run from your project directory:
  ```bash
  # If installed globally / via plugin:
  python ~/.claude/skills/project-management/tree-of-work/scripts/tree_of_work.py status

  # If running inside this cloned repository:
  python skills/tree-of-work/scripts/tree_of_work.py status
  ```

#### Sample State File (`.agent/tree-of-work/current-state.md`)
```markdown
# Agent State Snapshot

## NOW

- **Task:** [TASK-01] Implement oauth authentication
- **Status:** ACTIVE
- **Primary Files:** src/auth.py, src/config.py
- **Latest Progress:** Set up OAuth2 flow and user session tokens.
- **Next Concrete Step:** Add client validation middleware and test token expiration.

## PARKED / BLOCKED

- **Task:** [TASK-02] Setup Postgres database
  - **Status:** PARKED
  - **Reason:** Blocked by infra team provisioning DB credentials.
  - **Resume Condition:** DB credentials available.

## BRANCHES

- **Issue:** Token expiration bug
  - **Parent Task:** [TASK-01]
  - **Priority:** High
  - **Status:** ACTIVE
```

→ [Full Documentation](skills/tree-of-work/README.md)

### Deep Plan

Resilient, problem-driven, security-aware feature planning.

**Key Features:**
- 5-phase workflow (Scope → Gaps → Draft → Review → Finalize)
- Quick path for simple epics, full path for complex features
- Adversarial review with "outside voice" principle
- Progress persistence and plan versioning
- Automatic escalation triggers

**When to Use:**
- Scope: >3 files affected
- Complexity: Multiple independent work streams
- Architecture: Design decisions or trust-boundary updates needed
- Rollout: Phased delivery beneficial

→ [Full Documentation](skills/deep-plan/README.md)

## Project Structure

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
├── README.md
├── CLAUDE.md
├── LICENSE
└── .gitignore
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test with your AI agent
5. Submit a pull request

### Guidelines

- **Skills**: Follow the existing SKILL.md format with YAML frontmatter
- **Documentation**: Update README.md files when adding features
- **Tests**: Add evals for new skill behaviors

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built for the AI agent community. Special thanks to all contributors.
