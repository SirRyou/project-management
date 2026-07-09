# 13. Testing Requirements

Every non-trivial feature must define how correctness is **verified**.

## 13.1 Required Test Types

| Test Type          | When Required                               |
|--------------------|---------------------------------------------|
| Unit tests         | All business logic, utilities, parsers      |
| Integration tests  | IPC handlers, API endpoints, DB operations  |
| Regression tests   | Every production bug fix                    |
| Snapshot tests     | UI components with stable output contracts  |
| Concurrency tests  | Any shared mutable state or async flows     |

## 13.2 Mandatory Edge Cases

Tests must cover:

- Timeout behavior
- Cancellation (user-initiated and system-initiated)
- Malformed payload / invalid input
- Empty state (no data, no results, first run)
- Duplicate request handling
- Offline mode / network unavailable
- Concurrent access to shared resources
- Maximum input size (boundary testing)
- Permission denied / unauthorized access

## 13.3 Bug Fix Policy

Every production bug must introduce:

1. A **regression test** that reproduces the bug.
2. An **implementation fix** that resolves it.

Never fix only the code. A fix without a test is incomplete.

## 13.4 Test Quality Standards

- **Deterministic**: No dependence on execution order.
- **Isolated**: No shared mutable state between tests.
- **Fast**: Slow tests discourage running them.
- **Maintained**: Flaky tests must be quarantined and fixed, not ignored.

Use thread sanitizer tools where applicable (`-fsanitize=thread`, `go test -race`).
