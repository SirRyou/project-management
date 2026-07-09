# 8. Security by Default

Security is not a later review step. Every feature must be **secure by default**.

## 8.1 Secrets Handling

- **Never** hardcode API keys, tokens, passwords, or credentials.
- Read secrets only from secure providers (OS keychain, vault, encrypted env files).
- **Never** log secrets, auth headers, cookies, or private user data.
- Support secret rotation without downtime.

## 8.2 Input Validation

Treat **every external input** as untrusted. Validate all of:

- IPC payloads
- API request bodies, headers, and query parameters
- File contents (not just filenames)
- CLI arguments
- Environment variables
- Deserialized data (do not trust the shape of decoded JSON/protobuf)

**Reject invalid input early.** Do not partially process and then fail.

## 8.3 Principle of Least Privilege

Request only the minimum permissions required:

- File picker instead of unrestricted filesystem access.
- Minimum OS permissions (camera, location, etc.).
- Read-only access whenever write is not needed.
- Scoped API tokens instead of full-account keys.

## 8.4 Path Traversal Protection

- Never trust file paths supplied by users.
- Normalize and resolve paths before reading or writing.
- Reject paths that escape the intended directory boundary.
- On Windows, account for alternate data streams and UNC paths.

## 8.5 HTML / Markdown Rendering

If rendering user-generated HTML or Markdown:

- Sanitize with a well-tested library (e.g., DOMPurify).
- Escape `<script>`, event handlers, and `javascript:` URIs.
- Use Content Security Policy (CSP) headers where applicable.

## 8.6 Authentication & Authorization

- Enforce authorization checks on **every** request, not just at the gateway.
- Use constant-time comparison for secrets and tokens.
- Log authentication failures (without exposing credentials).
- Implement account lockout or rate limiting on repeated failures.

---
