# 1. Failure Handling & Error Recovery

## 1.1 Explicit Failure Modes

For every external service call, API call, system command, or file operation, explicitly identify:

- What happens if it **times out**?
- What happens if it returns an **error status** (e.g., 401, 429, 500)?
- What happens if the **payload structure changes**?

Never assume third-party SDK calls succeed. Wrap all of them in `try-catch`.

## 1.2 Recovery Hierarchy

When an operation fails, follow this order:

1. **Retry** — exponential backoff with jitter; set a maximum retry count.
2. **Fallback** — use an alternative source, method, or cached result.
3. **Degrade** — return partial results with clear user signaling.
4. **Fail** — return a clear, structured error to the caller.

Only retry **idempotent** operations. Distinguish retryable errors (network, 429) from permanent
ones (400, 404).

## 1.3 Error Propagation

- Errors must carry context: what was attempted, why it failed, what the caller can do.
- Use **typed/structured errors**, not raw string messages.
- Never silently swallow errors (`catch {}`, `except: pass`).
- Wrap low-level errors in domain-specific errors before propagation.

## 1.4 User-Facing Error Copy

Always translate system errors into human-readable, character-appropriate copy (e.g., via a shared
`error-copy.ts` or equivalent). Raw technical errors go to **logs only**, never to the UI.
