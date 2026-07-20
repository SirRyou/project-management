# Tutorial: Planning a Feature with Deep Plan

In this tutorial, you'll learn how to use Deep Plan to plan a feature that spans multiple files. By the end, you'll have a phased, adversarial-reviewed roadmap ready for implementation.

**Related docs:** [How-To Guide](howto-deep-plan.md) | [Reference](reference-deep-plan.md) | [Explanation](explanation-deep-plan.md)

## What You'll Need

- An AI coding agent (Claude Code, Cursor, Copilot, Codex, Gemini CLI, etc.)
- A feature to plan (we'll use a simple auth system as an example)
- 15 minutes

## Step 1: Set Up Your Project

First, make sure you have a project with some code. If you don't have one, create a simple project:

```bash
mkdir my-app
cd my-app
git init
echo "# My App" > README.md
git add README.md
git commit -m "Initial commit"
```

Now create some files to work with:

```bash
mkdir src
echo 'export function getUser(id) {
  return { id, name: "User" };
}' > src/users.js

echo 'export function login(username, password) {
  return { token: "abc123" };
}' > src/auth.js

git add src/
git commit -m "Add user and auth modules"
```

## Step 2: Activate Deep Plan

Ask your agent to plan a feature:

```
You: Plan an authentication system for this app
Agent: Activating Deep Plan.

      Scope: Authentication system
      Files affected: 4 (src/auth.js, src/users.js, src/middleware.js, src/routes.js)
      Work streams: 3 (auth logic, middleware, routes)

      This is Full Path territory (multi-stage dependencies, state mutations).
      Starting Phase 1: Understand Scope.
```

The agent detected this is a complex feature and chose Full Path.

## Step 3: Phase 1 — Understand Scope

The agent reads your project and extracts the scope:

```
Agent: Phase 1: Understand Scope

      Epic: Authentication system
      Status: Not started
      Dependencies: None
      Known gaps: None

      Scope locked. Ready for Phase 2.
```

## Step 4: Phase 2 — Enumerate Gaps

The agent analyzes under three lenses:

```
Agent: Phase 2: Enumerate Gaps

      Lens 1 — Problem-Fit:
      - Literal ask: "Authentication system"
      - Underlying goal: Secure user access with sessions
      - Gap: Literal ask covers login, but not session management
      - Verdict: PARTIAL_FIT — missing session management

      Lens 2 — Resilience:
      - F1: Token expiry not handled (trigger: time passes, impact: silent auth failure)
      - F2: No retry logic for failed logins (trigger: network error, impact: user locked out)

      Lens 3 — Security:
      - S1: Password stored in plain text (risk: credential leak, defense: hash with bcrypt)
      - S2: No CSRF protection (risk: cross-site request forgery, defense: CSRF tokens)

      Gaps: 2 MISFIT, 2 failure modes, 2 security risks
      Ready for Phase 3.
```

## Step 5: Phase 3 — Draft Roadmap

The agent constructs a tentative roadmap:

```
Agent: Phase 3: Draft Roadmap

      Work Stream 1: Auth Logic (3 tasks)
      - T1: Add password hashing with bcrypt
      - T2: Add token generation and validation
      - T3: Add session management

      Work Stream 2: Middleware (2 tasks)
      - T4: Create auth middleware for protected routes
      - T5: Add CSRF protection middleware

      Work Stream 3: Routes (2 tasks)
      - T6: Create login/logout routes
      - T7: Create protected user routes

      Dependencies: T4 depends on T2, T6 depends on T1

      Ready for adversarial review.
```

## Step 6: Phase 4 — Adversarial Review

The agent runs the plan by a different model:

```
Agent: Phase 4: Adversarial Review

      CTO Review:
      1. Scope too broad — consider splitting into "auth core" and "session management"
      2. Missing assumption: what happens when tokens expire mid-request?
      3. Sequencing: password hashing should come before token generation

      Eng Review:
      1. Hidden dependency: T3 (session management) needs T2 (token validation)
      2. Testing gap: no integration test plan
      3. Security: missing rate limiting on login attempts

      Amendments:
      - Split scope into 2 phases (auth core, then session management)
      - Add token refresh logic to T2
      - Add rate limiting to T6
      - Add integration test plan

      Ready for finalization.
```

## Step 7: Phase 5 — Finalize Roadmap

The agent generates the final roadmap and asks for confirmation:

```
Agent: Phase 5: Finalize Roadmap

      Final Roadmap: Authentication System

      Phase 1: Auth Core (Week 1)
      - T1: Add password hashing with bcrypt
      - T2: Add token generation, validation, and refresh
      - T3: Create login/logout routes with rate limiting
      - T4: Create auth middleware

      Phase 2: Session Management (Week 2)
      - T5: Add session storage and management
      - T6: Add CSRF protection middleware
      - T7: Create protected user routes

      Exit criteria:
      - All tests pass
      - No security vulnerabilities
      - Rate limiting works

      A) Approve and start implementation
      B) Modify the roadmap
      C) Cancel
You: A
Agent: Roadmap approved. Starting implementation.
```

## What You Built

You now have a working Deep Plan setup that:
- Analyzed the feature under three lenses (Problem-Fit, Resilience, Security)
- Identified gaps and risks before implementation
- Created a phased roadmap with dependencies
- Got adversarial review from a different model
- Got explicit user approval before starting

## Next Steps

- Try using Deep Plan on a real feature in your project
- Learn about [Gap Analysis](../docs/reference-deep-plan.md#gap-analysis-details) for deeper analysis
- Read about [Adversarial Review](../docs/reference-deep-plan.md#adversarial-review-details) for better reviews
- Check out the [How-To Guide](../docs/howto-deep-plan.md) for more advanced usage
