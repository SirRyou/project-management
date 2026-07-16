# Investigate

Systematic debugging: trace from symptom to root cause, fix the cause, prove the fix.

## What It Does

Investigate enforces a disciplined debugging methodology that prevents the most common agent failure: fixing symptoms instead of root causes. Every fix must be traced to evidence, verified with tests, and proven to work.

## When to Use

- Bug reports, error messages, stack traces
- "Why is this broken?" or "it was working yesterday"
- 500 errors, unexpected behavior
- Any debugging task

## When NOT to Use

- Feature work, refactors, greenfield coding
- Tasks that don't involve a bug or error

## How It Works

### Phases

1. **Root Cause Investigation** — collect symptoms, read code, check recent changes, reproduce, check history
2. **Pattern Analysis** — match against known patterns (race condition, null propagation, state corruption, integration failure, config drift, stale cache)
3. **Hypothesis Testing** — verify hypothesis with evidence before writing any fix. 3-strike rule: if 3 hypotheses fail, escalate.
4. **Implementation** — fix root cause, minimal diff, regression test that fails without fix and passes with fix
5. **Verification** — fresh reproduction, test suite output, structured debug report

### Iron Law

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

Fixing symptoms creates whack-a-mole. Every unrooted fix makes the next bug harder to find.

## Core Rules

- **3-strike rule**: 3 failed hypotheses → STOP, escalate
- **Minimal diff**: fewest files, fewest lines. Don't refactor adjacent code.
- **Regression test**: must fail without fix, pass with fix
- **Verify**: never say "this should fix it." Run the tests. Paste output.
- **Blast radius**: if fix touches >5 files, flag before proceeding

## Red Flags

- "Quick fix for now" — there is no "for now"
- Proposing a fix before tracing data flow — you're guessing
- Each fix reveals a new problem elsewhere — wrong layer, not wrong code
- Circular investigation — same files, same dead end. Escalate.

## Architecture

```
investigate/
├── SKILL.md                    # Behavioral spec (the skill)
├── README.md                   # This file
└── runtime-bindings.md         # Platform-specific glue template
```

## Runtime Requirements

| Capability | Required | Purpose |
|------------|----------|---------|
| file-read | Yes | Read source, logs, git history |
| file-write | Yes | Apply fix, write regression test |
| bash | Yes | Run tests, git log, reproduction |
| grep | Yes | Find references, trace code paths |
| question | Yes | 3-strike escalation, blast radius check |
| web-search | No | External pattern research |
| subagent | No | Fresh-eyes review after failed hypotheses |

## Triggers

- "debug this"
- "fix this bug"
- "why is this broken"
- "investigate this error"
- "root cause analysis"
- "it was working yesterday"
- stack traces, 500 errors, unexpected behavior

## Debug Report Format

```
DEBUG REPORT
════════════════════════════════════════
Symptom:         [what the user observed]
Root cause:      [what was actually wrong]
Fix:             [what changed, file:line]
Evidence:        [test output showing fix works]
Regression test: [file:line of new test]
Related:         [prior bugs in same area]
Status:          DONE | DONE_WITH_CONCERNS | BLOCKED
════════════════════════════════════════
```

## License

MIT
