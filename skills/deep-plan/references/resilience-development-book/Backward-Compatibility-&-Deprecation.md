# 6. Backward Compatibility & Deprecation

## 6.1 Persistent Config Non-Destruction

When parsing old configs, schemas must **inject safe defaults** for newly introduced keys.
Never wipe an entire config because a new property was added.

## 6.2 IPC / API Contract Stability

Never rename, delete, or modify parameter schemas of active channels/endpoints in a breaking
way. If a breaking change is unavoidable, register a **versioned channel** (e.g., `channel:v2`,
`/v2/`) and keep the prior version active as a legacy fallback for a defined deprecation period.

## 6.3 Schema Evolution Rules

- Additive changes (new optional fields) are generally safe.
- Removing or renaming fields requires a full deprecation cycle.
- Never change the **meaning** of an existing field.

## 6.4 Two-Step Deprecation Lifecycle

To retire any public API, state property, or internal utility:

1. **Deprecate**: Mark with `@deprecated`, log a developer warning, maintain full functional
   behavior internally (often by mapping old contracts to new ones).
2. **Remove**: Delete only after surviving **a minimum of two minor releases** and verifying
   zero active references.
