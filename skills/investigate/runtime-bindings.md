# Runtime Bindings — Template

This file demonstrates the **runtime bindings** pattern: separating a skill's behavioral spec from the platform it runs on. The SKILL.md is the universal spec. This file wires it to a specific runtime.

## Why separate?

A debugging methodology should work on any platform. If the skill embeds platform-specific tool names, config paths, and telemetry calls, it becomes non-portable and carries legal/reputational risk from the host ecosystem. Separation means:

- The behavioral spec is standalone, portable, and original
- The runtime bindings are thin glue, disposable and replaceable
- Different platforms can share the same skill with different bindings

## Structure

Runtime bindings contain:

1. **Preamble** — platform session setup (branch detection, config loading, feature flags)
2. **Tool mapping** — how generic capabilities (`question`, `file-read`) map to platform-specific tool names
3. **Telemetry** — platform-specific logging (opt-in analytics, session tracking)
4. **State persistence** — how learnings/notes are stored on this platform
5. **Integration hooks** — freeze/scope-lock, continuous checkpointing, etc.

## What does NOT belong here

- The debugging methodology (that's in SKILL.md)
- Generic advice that applies everywhere (iron laws, red flags, report format)
- Anything that would be true on any platform

## Example skeleton

Replace `PLATFORM` with your runtime name:

```markdown
# Investigate — PLATFORM Runtime Bindings

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
