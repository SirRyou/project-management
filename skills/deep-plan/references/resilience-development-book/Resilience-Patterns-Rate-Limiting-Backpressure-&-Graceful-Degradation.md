# 11. Resilience Patterns: Rate Limiting, Backpressure & Graceful Degradation

## 11.1 Inbound Rate Limiting

- Implement rate limiting on all public-facing endpoints.
- Use token bucket or sliding window algorithms.
- Return `429 Too Many Requests` with `Retry-After` headers.
- Limit concurrent internal operations (max parallel file writes, max concurrent API calls)
  using semaphores or concurrency pools.

## 11.2 Backpressure Handling

When a system is overwhelmed:

- Queue requests with **bounded queue sizes**.
- Drop low-priority requests rather than crashing.
- Signal upstream systems to slow down.
- Monitor queue depth and latency as early warning signals.

## 11.3 Graceful Degradation

Systems must degrade gracefully, not crash entirely.

- **Isolate failures**: A failure in one module must not bring down unrelated modules.
- **Circuit breakers**: Stop calling a failing dependency after repeated failures; retry after
  a backoff period.
- **Bulkheads**: Partition resources so one runaway process cannot consume everything.

**User-facing behavior during degradation:**

- Show partial data if a secondary source is down.
- Display meaningful error messages, not stack traces or status codes.
- Offer retry options with clear feedback.
- Preserve user input when a submission fails.

## 11.4 Idempotency

Operations that may be retried must be safe to execute multiple times. If an operation is not
naturally idempotent, make it so with idempotency keys, deduplication tokens, or conditional
checks. Executing the same operation twice **must not corrupt state**.

Applies to: IPC commands, save/submit actions, retry buttons, webhook handlers, message queue
consumers, payment/transaction processing.
