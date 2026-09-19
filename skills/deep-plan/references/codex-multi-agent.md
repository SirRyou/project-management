# Codex Multi-Agent Configuration Reference

Use this reference when the active runtime is Codex and nested delegation or custom Deep Plan roles are required.

## Inspect the configuration

Check the applicable user configuration at `~/.codex/config.toml` and trusted project configuration at `.codex/config.toml`. Keep personal defaults, provider settings, and authentication in the user configuration. Do not overwrite an existing configuration file.

The installer-generated role definitions remain under `.codex/agents/` for a workspace install or `~/.codex/agents/` for a user install. The `[agents]` table controls session-level multi-agent capability and concurrency; it does not replace the role files.

## Required decision

When nested delegation is needed, verify that the effective configuration permits multi-agent tools:

```toml
[agents]
enabled = true
max_concurrent_threads_per_session = 6
```

Codex currently defaults `agents.enabled` to true, so treat the explicit setting as a clarity and policy check rather than assuming it is always required. Preserve unrelated settings and merge keys into an existing `[agents]` table.

Project configuration is loaded only for trusted projects. Explain that constraint when a project-local configuration is not taking effect.

## Deep Plan policy

Use the generated role file's model, reasoning, sandbox, and developer instructions. Respect `delegation.can_spawn_children` and `delegation.max_child_depth` from `subagents.json`; do not infer nesting capability from the presence of an agent file.

Keep the PM in control of the DAG, integration, review gates, evidence, and ledger. A child agent may assist but cannot mark a task complete independently.

After changing the effective configuration, restart the Codex session before validating nested delegation.

See the [Codex configuration reference](https://developers.openai.com/codex/config-reference/) and [Codex subagents documentation](https://developers.openai.com/codex/subagents/) for the current schema.
