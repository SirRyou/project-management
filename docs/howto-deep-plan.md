# How to Use Deep Plan

Deep Plan guides agents through structured planning for complex features. Here's how to use it effectively.

**Related docs:** [Tutorial](tutorial-deep-plan.md) | [Reference](reference-deep-plan.md) | [Explanation](explanation-deep-plan.md)

## Prerequisites

- An AI coding agent (Claude Code, Cursor, Copilot, Codex, Gemini CLI, etc.)
- A feature to plan that spans multiple files or work streams
- Basic understanding of your project's architecture

## Steps

### 1. Activate the Skill

Deep Plan activates automatically when you say things like:
- "Plan this feature"
- "Design an epic"
- "Architectural planning"
- "Break down this work"
- "Create a roadmap"

Or you can invoke it explicitly by asking the agent to plan a feature.

### 2. Choose Execution Path

The agent will ask about the scope:
- **Quick Path**: linear logic, no state mutations, low uncertainty, no trust-boundary crossings
- **Full Path**: multi-stage dependencies, state mutations, unknowns, or trust-boundary crossings

**Example:**
```
Agent: Is this linear or multi-stage with dependencies?
You: Multi-stage — schema mutation with shared state.
Agent: That's Full Path territory. Starting Phase 1.
```

### 3. Phase 1: Understand Scope

The agent reads your tracking docs and extracts:
- Epic name and status
- Dependencies
- Known gaps

If no tracking doc exists, the agent will ask.

**Example:**
```
Agent: I found ROADMAP.md with "Auth system" as the current epic.
      Dependencies: None
      Known gaps: None
      Ready to proceed to Phase 2.
```

### 4. Phase 2: Enumerate Gaps

The agent analyzes under three lenses:
1. **Problem-Fit**: Does the literal request solve the underlying problem?
2. **Resilience**: What fails when things go wrong?
3. **Security**: What gets abused?

Each gap is tagged: `FIT`, `MISFIT`, `CRITICAL`, or `BLOCKER`.

**Example:**
```
Agent: Gap analysis complete:
      - Problem-Fit: FIT (request matches goal)
      - Resilience: 2 failure modes found (timeout, retry storm)
      - Security: 1 CRITICAL item (missing input validation)
      - Dependency: 1 BLOCKER (waiting on API key from vendor)
      Total: 3 gaps, 1 CRITICAL
```

### 5. Phase 3: Draft Roadmap

The agent constructs a tentative roadmap:
- Work streams with tasks
- Dependencies between tasks
- Exit criteria for each task

**Example:**
```
Agent: Draft roadmap:
      Work Stream 1: Auth middleware (3 tasks)
      Work Stream 2: Input validation (2 tasks)
      Work Stream 3: Error handling (2 tasks)
      Dependencies: WS2 depends on WS1
      Ready for adversarial review.
```

### 6. Phase 4: Adversarial Review

The agent runs the plan by a different model (or same model with fresh context):
- **CTO Review**: Scope, assumptions, sequencing
- **Eng Review**: Technical risks, security, testing gaps

**Example:**
```
Agent: CTO review found 2 issues:
      1. Scope too broad (suggest splitting into 2 epics)
      2. Missing assumption: API rate limits not considered

      Eng review found 3 issues:
      1. Hidden dependency: WS3 needs WS2 to complete first
      2. Testing gap: No integration test plan
      3. Security: Missing CSRF protection

      Amendments compiled. Ready for finalization.
```

### 7. Phase 5: Finalize Roadmap

The agent generates the final roadmap and asks for confirmation.

**Example:**
```
Agent: Final roadmap ready:
      [detailed roadmap]

      A) Approve and start implementation
      B) Modify the roadmap
      C) Cancel
You: A
Agent: Roadmap approved. Starting implementation.
```

## Verification

After each phase, verify:
- Phase 1: Scope is clear and complete
- Phase 2: All gaps identified and tagged
- Phase 3: Roadmap has tasks, dependencies, and exit criteria
- Phase 4: All review findings addressed
- Phase 5: User has explicitly approved the roadmap

## Troubleshooting

### Agent Skips Phase 4

If the agent skips adversarial review:
1. Check if Phase 2 yielded all `FIT`, 0 `CRITICAL`, and <=5 total gaps
2. If yes, skipping is correct (low-risk change)
3. If no, ask the agent to run Phase 4

**Example:**
```
You: Did you run adversarial review?
Agent: Phase 2 yielded all FIT, 0 CRITICAL, and 3 gaps. Skipping Phase 4 per protocol.
You: Run it anyway. I want a second opinion.
Agent: Running adversarial review...
```

### Agent Implements Without Approval

If the agent starts implementing before Phase 5:
1. Remind it of the Iron Law (never implement without approval)
2. Ask it to stop and finalize the roadmap
3. Ask for explicit confirmation

**Example:**
```
You: Stop. You haven't finalized the roadmap.
Agent: You're right. Finalizing roadmap now.
      [roadmap]
      A) Approve and start implementation
      B) Modify the roadmap
      C) Cancel
```

### Agent Misses Security Issues

If the agent misses security issues:
1. Ask it to run Lens 3 (Security) again
2. Ask it to check for common patterns (input validation, auth, CSRF)
3. Ask it to add CRITICAL tags

**Example:**
```
You: Did you check for input validation?
Agent: Re-running Lens 3... Found 2 CRITICAL items:
      1. Missing input validation on user input
      2. Missing CSRF protection on form submission
```

### Agent Produces Vague Tasks

If the agent produces vague tasks:
1. Ask it to add specific exit criteria
2. Ask it to add machine-executable verification steps
3. Ask it to add file:line references

**Example:**
```
You: These tasks are vague. Add exit criteria.
Agent: Updated tasks:
      Task 1: "Add JWT validation"
        Exit criteria: Test passes with valid token, fails with invalid token
        Verification: pytest tests/test_auth.py::test_jwt_validation
```
