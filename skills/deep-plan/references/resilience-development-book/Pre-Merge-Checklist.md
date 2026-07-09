# 18. Pre-Merge Checklist

Run this before presenting code or opening a pull request.

## Correctness & Resilience

- [ ] **Sad Paths Map**: Failure pathways of this change are documented.
- [ ] **Error Catching**: All network, parsing, and I/O operations are wrapped in `try-catch`.
- [ ] **Recovery Strategy**: Retry, fallback, degrade, and fail paths are defined.
- [ ] **Resource Cleanup**: Every created resource (interval, listener, stream, connection)
      has a corresponding cleanup function.
- [ ] **Race Condition Guard**: Double-action is prevented; stale async responses cannot
      overwrite newer state.
- [ ] **Idempotency**: Retryable operations are safe to execute more than once.

## Type Safety & Data Integrity

- [ ] **Typing**: All variables and parameters are strictly typed; no unguarded `any`.
- [ ] **Schema Validation**: Config and external payloads are validated at runtime boundaries.
- [ ] **Persistence Safety**: Corrupt config/DB fails gracefully to safe defaults with diagnostics.
- [ ] **Migration Script**: Schema changes include a versioned migration.

## Compatibility

- [ ] **Backward Compatibility**: Existing user files, saved states, and IPC endpoints are
      unaffected; missing properties have defaults.
- [ ] **Two-Step Deprecation**: Retired features follow the deprecation grace period — not
      deleted outright.
- [ ] **IPC Contract Stability**: No breaking changes to active channels without versioning.

## Security

- [ ] **Attack Surface**: No new unvalidated inputs, endpoints, or data flows.
- [ ] **Secrets Exposure**: No keys, tokens, or credentials in logs, responses, or client code.
- [ ] **Permission Escalation**: No broader access than necessary.
- [ ] **Injection Risks**: SQL injection, command injection, XSS, path traversal — all mitigated.

## Performance & Reliability

- [ ] **Complexity**: Algorithmic complexity (time and space) is acceptable.
- [ ] **Memory Impact**: No large unbounded allocations or cache growth.
- [ ] **Startup Impact**: Cold start time is not meaningfully increased.
- [ ] **Rate Limiting**: External calls have timeouts, retry budgets, and backoff.
- [ ] **Boundary Isolation**: Raw SDK calls are wrapped in adapters.

## AI / LLM (if applicable)

- [ ] **Timeout & Retry**: LLM/TTS calls have a timeout, retry limit, and backoff.
- [ ] **Fallback Model**: A fallback is defined if the primary model fails.
- [ ] **Token Budget**: Context overflow is handled gracefully via sliding window.
- [ ] **Agent Metadata**: Decisions emit structured reasoning metadata, not raw chain-of-thought.

## Observability & Maintainability

- [ ] **Diagnostics**: System-level errors are logged with structured parameters.
- [ ] **Diagnostics Export**: Log export path exists for crash troubleshooting.
- [ ] **Reduced Motion**: UI animations respect `prefers-reduced-motion`.
- [ ] **Complexity Budget**: No function exceeds ~50 lines or 3 levels of nesting.
- [ ] **Single Responsibility**: Each function does one thing.
- [ ] **Documentation**: Non-obvious decisions are documented; ADR filed if significant.
- [ ] **Tests**: Unit, integration, and edge case tests are present for this change.
- [ ] **Bug Fix Regression**: If fixing a bug, a regression test is included.
