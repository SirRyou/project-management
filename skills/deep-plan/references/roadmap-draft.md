# Reference: Roadmap Draft (Phase 3)

Guides the agent through Phase 3 (Draft Roadmap) of the deep-plan workflow.

---

## What Phase 3 Actually Writes

Per the Progressive Write Rule in SKILL.md, Phase 3 does **not** produce a separate lightweight draft document. It writes full detail directly into the living roadmap file (`.deep-plan/<feature-plan>.md`), following `templates/roadmap-template.md` — Work Streams with Problem-Fit, Failure Modes, Security Risks, full Tasks table, Sad Paths, and Exit Criteria, all filled in at full detail.

The lightweight structure below is **not the draft** — it is a digest you extract *from* the already-full file, used only as compact input for the Phase 4 reviewer prompts (Sections 2 and 3 in `adversarial-review.md`), so the CTO/Eng reviewer isn't handed the entire multi-page document per call.

**Never write only the digest. Never treat the digest as a replacement for the full file.** If the living file doesn't yet have Failure Modes / Security Risks / Exit Criteria filled in per work stream, Phase 3 isn't done yet — go back and fill the real template, don't compress into the shape below instead.

---

## Reviewer Digest (extracted from the full file, for Phase 4 prompts only)

```markdown
## Draft Plan: [Epic/feature Name] — Phase [X]

### Problem-Fit Note
[Extracted from the full file's Problem-Fit sections: PARTIAL FIT / MISFIT items from Phase 2 and how the plan addresses or accepts them as debt]

### Proposed Work Streams

**WS1 — [Name of Work Stream]**
- **Why**: [One sentence, from the full file's WS Objective]
- **Key tasks**:
  - T1: [Description]
  - T2: [Description]
  - T3: [Description]
  ...
- **Highest risk**: [F-id or S-id from the full file] — [One sentence on why this is the highest risk]

**WS2 — [Name of Work Stream]**
...

### Dependency Sketch
- Diagram or text mapping dependencies (e.g., WS1 → WS2 → WS3)
- Explicit task blockers (e.g., T3 blocks T5 because [reason])

### Open Questions
- [List any questions needing resolution before final implementation]

### Confidence Table
| WS | Confidence Level | Reason |
|----|------------------|--------|
| WS1 | High / Medium / Low | [Reason for this rating] |
```

This digest is disposable — it's regenerated from the full file whenever a reviewer prompt needs it, and discarded after. The full file in `.deep-plan/<feature-plan>.md` is the only artifact that persists and that Phase 5 audits.
