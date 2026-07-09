# 2. Async Lifecycles & Resource Ownership

## 2.1 No Zombie Promises

Every stream, interval, timeout, or active loop must:

- Accept an `AbortSignal` (or equivalent) and terminate cleanly when aborted.
- Have abort functions that are **safe to call multiple times** without throwing.

## 2.2 Teardown on Reload or Close

If a renderer reloads or the window closes, the process must cleanly tear down and release all
associated resources: cancel active audio, drop active streams, reset state managers.

## 2.3 Resource Ownership Contract

For every resource (file handle, connection, subscription, timer, stream), define:

| Question              | Answer Required          |
|-----------------------|--------------------------|
| Who creates it?       | Specific module/service  |
| Who disposes it?      | Same or explicit handoff |
| Who retries on error? | Single owner, not both   |
| Who observes failure? | Defined error boundary   |

If ownership is ambiguous, cleanup bugs will follow. Use RAII, `try-with-resources`, `defer`,
or explicit disposal contracts.

## 2.4 Memory Bounds

Active arrays (chat histories, audio queues, log buffers) must have a **capped upper bound**
to prevent heap exhaustion over long sessions.
