# 4. State Integrity & Concurrency

## 4.1 Double-Action Prevention

All UI components triggered by async actions must implement **transition state locks**
(e.g., disable button + show spinner) to prevent concurrent executions of the same action.

## 4.2 Optimistic Update Rollbacks

If the UI updates optimistically before a backend write is confirmed, implement a robust
rollback that restores the **exact previous state** if the operation fails.

## 4.3 Stale Async Guard

Use unique transaction tokens, generation counters, or `AbortSignal`s to guarantee that
stale async responses cannot overwrite newer state.

## 4.4 Shared Mutable State

- Protect shared mutable state with locks, channels, atoms, or actors.
- Prefer immutable data structures where possible.
- Document thread-safety guarantees on public APIs.
- Define and document a lock hierarchy to avoid deadlock.

## 4.5 Common Concurrency Pitfalls

- Reading/writing the same object from multiple threads without synchronization.
- Race conditions in check-then-act patterns (`if not exists → create`).
- Deadlocks from inconsistent lock acquisition order.
- Starvation from holding locks during I/O.

## 4.6 Network Fluctuation Handling

If a feature depends on internet connectivity:

- Subscribe to connection status changes.
- Suspend active tasks when offline.
- Run health checks before resuming when connection is restored.
