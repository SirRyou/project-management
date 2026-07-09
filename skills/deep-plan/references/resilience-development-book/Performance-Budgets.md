# 9. Performance Budgets

A feature that works but gradually degrades performance is **incomplete**.

## 9.1 Define Targets Before Implementation

| Metric                   | Example Target         |
|--------------------------|------------------------|
| Maximum startup cost     | < 200ms cold start     |
| Maximum memory baseline  | < 50MB                 |
| Maximum render latency   | < 16ms per frame       |
| Maximum network requests | < 5 per screen         |
| Maximum bundle size      | < 250KB gzipped        |

## 9.2 Avoid These

- Repeated JSON parsing of the same data.
- Unnecessary re-renders (check dependency arrays).
- Duplicate API requests for the same resource.
- Blocking synchronous work on the UI/main thread.
- Unbounded array operations (`.map`, `.filter`, `.sort`) on large datasets without pagination.

## 9.3 Caching Strategy

- Memoize expensive computations where appropriate.
- Cache with a defined invalidation policy (TTL, event-driven, or LRU).
- Never cache sensitive data in unprotected stores.
- Document cache invalidation rationale.

## 9.4 Lazy Loading & Code Splitting

- Load code and assets on demand, not upfront.
- Use dynamic imports for route-level splitting.
- Defer non-critical resources (analytics, chat widgets, etc.).
