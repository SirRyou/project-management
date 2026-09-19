# Deep Plan Subagent Definitions

This directory contains the canonical system prompts for Deep Plan specialists.

These files are static role definitions. They are not the per-task dispatch message.

## Prompt layers

- `subagents/*.md`: stable system prompt; role, boundaries, procedure, evidence, and output contract.
- `subagents.json`: role metadata, invocation contract name, and vendor runtime configuration.
- `../invocation-contracts.md`: parent-owned user-prompt shape for each dispatch type.
- `../swarm-execution.md`: orchestration, ordering, retries, and review gates.

The PM must inject task-specific context only as the user prompt when invoking an agent. It must not rewrite or append to the installed system prompt. Keep task paths, acceptance criteria, reviewer findings, and worktree details in the dynamic invocation prompt.

## Nested delegation

Nested delegation is role-scoped. Approved planning and research roles may receive one child level; workers, Code Auditors, and Adversarial Challengers remain non-nesting so the PM retains ownership of the DAG and review gates. The `delegation` object in `subagents.json` is the portable policy; each runtime adapter maps it to native controls.

## Vendor mapping

| Runtime | Static definition | Dynamic parent input |
| --- | --- | --- |
| Claude Code | `.claude/agents/<name>.md` frontmatter plus Markdown body | Agent prompt/user task message |
| Codex | `.codex/agents/<name>.toml` and `developer_instructions` | Agent task prompt |
| Antigravity | `.agents/agents/<name>.md` or native JSON definition | Invocation user prompt |
