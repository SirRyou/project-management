# 3. Type Safety & Schema Validation

## 3.1 Zero `any` Policy

Avoid `any` or unguarded `unknown` in function parameters and state interfaces.
Declare proper TypeScript types or use generics. No unsafe type assertions without validation.

## 3.2 Runtime Schema Validation

Validate all incoming configuration objects and external payloads using a schema library
(e.g., Zod, io-ts, JSON Schema) at **runtime boundaries** — IPC handlers, API endpoints,
config loaders — before saving to disk or applying to state.

## 3.3 IPC / Cross-Boundary Typing

All IPC channels and cross-boundary contracts must be:

- Registered in a shared constants file (e.g., `shared/constants.ts`).
- Strictly typed in both the sending and receiving layers (e.g., preload bridge, server handler).

## 3.4 Deterministic Behavior

Avoid hidden global mutable state, time-dependent logic without injected clocks, and
nondeterministic async ordering. Determinism improves debugging, testing, and caching.
