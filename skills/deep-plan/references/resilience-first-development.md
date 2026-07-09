# Zero-Debt & Resilience-First Development Workflow

> A general-purpose engineering standard for building reliable, secure, and maintainable software —
> designed to prevent technical debt from the first line of code, regardless of domain or stack.
> read only what necessary.

---

## Core Philosophy

Minimize "Tech Depth" for new code. Error handling, cleanup lifecycles, edge-case resilience,
security, and observability must be implemented **simultaneously** with the happy path.
If a feature does not handle its own failures, it is **incomplete** and cannot be merged.

---

## Table of Contents

1. [Failure Handling & Error Recovery](resilience-development-book/Failure-Handling-&-Error-Recovery.md)
2. [Async Lifecycles & Resource Ownership](resilience-development-book/Async-Lifecycles-&-Resource-Ownership.md)
3. [Type Safety & Schema Validation](resilience-development-book/Type-Safety-&-Schema-Validation.md)
4. [State Integrity & Concurrency](resilience-development-book/State-Integrity-&-Concurrency.md)
5. [Data Persistence & Configuration](resilience-development-book/Data-Persistence-&-Configuration.md)
6. [Backward Compatibility & Deprecation](resilience-development-book/Backward-Compatibility-&-Deprecation.md)
7. [Third-Party Isolation & Dependency Governance](resilience-development-book/Third-Party-Isolation-&-Dependency-Governance.md)
8. [Security by Default](resilience-development-book/Security-by-Default.md)
9. [Performance Budgets](resilience-development-book/Performance-Budgets.md)
10. [Observability: Logging, Metrics & Tracing](resilience-development-book/Observability-Logging-Metrics-&-Tracing.md)
11. [Resilience Patterns: Rate Limiting, Backpressure & Graceful Degradation](resilience-development-book/Resilience-Patterns-Rate-Limiting-Backpressure-&-Graceful-Degradation.md)
12. [AI / LLM Guardrails](resilience-development-book/AI-LLM-Guardrails.md)
13. [Testing Requirements](resilience-development-book/Testing-Requirements.md)
14. [Code Complexity Budget](resilience-development-book/Code-Complexity-Budget.md)
15. [Accessibility](resilience-development-book/Accessibility.md)
16. [Feature Flags & Safe Rollouts](resilience-development-book/Feature-Flags-&-Safe-Rollouts.md)
17. [Documentation & Architecture Decisions](resilience-development-book/Documentation-&-Architecture-Decisions.md)
18. [Pre-Merge Checklist](resilience-development-book/Pre-Merge-Checklist.md)
