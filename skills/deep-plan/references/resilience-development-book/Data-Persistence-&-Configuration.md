# 5. Data Persistence & Configuration

## 5.1 Corrupt Storage Recovery

If local state, databases, or config files fail to parse or are corrupted, the application
**must not crash**. It must:

1. Fall back to predefined safe defaults.
2. Isolate the corrupt file (e.g., rename to `.corrupt`).
3. Log a structured diagnostic alert.

## 5.2 Schema Migrations

Any change to persistent state schemas must be accompanied by an explicit, versioned migration
script specifying how legacy data is safely migrated without data loss.

## 5.3 Configuration as API

Every configuration object must define:

- **Version**: Schema version for forward compatibility.
- **Schema**: Validated structure (Zod, JSON Schema, io-ts, etc.).
- **Defaults**: Sensible values for all optional fields.
- **Migration path**: How to move from prior versions.
- **Validation**: Reject invalid config at startup, not at runtime.
- **Documentation**: What each field does and its valid values.

Never silently ignore unknown config keys — warn or reject. Secrets must not be stored in
config files.
