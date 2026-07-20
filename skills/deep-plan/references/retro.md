# Reference: Post-Execution Retro (Phase 6)

Closes the loop after execution-handoff finishes. Non-blocking — no user confirmation needed, this is a write-and-done step.

---

## When This Runs

Only after execution-handoff.md's Section 6 (Final Review) has completed for every work stream. If the user declined handoff (Section 1, option B) or execution is still in progress, this phase doesn't apply yet.

## What to Compare

Pull from three sources:
- The finalized roadmap (`.deep-plan/<feature-plan>.md`) — Confidence Table, Tasks, Failure Modes, Security Risks
- Every `WS{n}-report.md` — what the implementer actually did, concerns raised
- Every `WS{n}-review.md` — what the reviewer actually found

For each work stream, check:

```markdown
### WS[n] — [Name] Retro

- **Confidence estimate vs reality**: [predicted High/Medium/Low] → [was that accurate? if Low-confidence WS sailed through clean, or a High-confidence WS needed 3 fix cycles, note it]
- **Failure modes that actually fired**: [which F-ids from the roadmap showed up during implementation/review, vs which stayed theoretical]
- **Security risks that actually fired**: [which S-ids were real vs theoretical]
- **Missed entirely**: [anything the reviewer or implementer hit that wasn't in the roadmap's Failure Modes/Security Risks at all — this is the most valuable line, it's a blind spot in Phase 2's analysis]
- **Review cycles needed**: [1 = clean, 2+ = note what the first pass missed]
```

## What NOT to Do

- Don't re-litigate decisions that are already closed (Architecture Decisions, accepted debt from Phase 2) — retro is about calibration, not re-opening scope.
- Don't turn this into a blame log on the implementer/reviewer subagents — the target is the *plan's* prediction accuracy, not execution quality.
- Don't block on this — if the user wants to move on immediately after Final Review, write what you have from the artifacts already on disk and stop; don't chase them for input.

## Output

Write to `.deep-plan/retro.md`:

```markdown
# Retro: [Epic/Feature Name]

## Calibration Summary
- [N] work streams, [M] matched their confidence estimate, [K] didn't
- Most common miss: [pattern, if one emerges — e.g. "async lifecycle issues under-weighted in Confidence"]

## Per-Work-Stream Detail
[the per-WS blocks from above]

## Carry Forward
- [Any pattern worth folding into gap-analysis.md's Focus Rule or Failure Mode naming for next time — e.g. "add 'webhook retry storms' to the named pattern list"]
```

`Carry Forward` is the actual payoff of this phase — it's what should change in how Phase 2 gets approached on the next plan. If nothing carries forward, say so explicitly rather than leaving the section empty.
