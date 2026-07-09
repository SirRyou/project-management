# Reference: Roadmap Draft (Step 4)

This reference document guides the agent through Step 4 (Draft Plan) of the `deep-plan` workflow.

---

## Step 4 — Draft Plan (Agent)

Draft a lightweight plan (maximum 2 pages) using the following template. This draft will go to adversarial review in Steps 5–6.

```markdown
## Draft Plan: [Epic Name] — Phase [X]

### Problem-Fit Note
[Describe any PARTIAL FIT / MISFIT items identified in Step 3A and explain how the plan addresses or explicitly accepts them as debt]

### Proposed Work Streams

**WS1 — [Name of Work Stream]**
- **Why**: [One sentence explaining why this work stream is needed]
- **Key tasks**: 
  - T1: [Description]
  - T2: [Description]
  - T3: [Description]
- **Highest risk**: [F-id or S-id] — [One sentence explaining why this is the highest risk]

**WS2 — [Name of Work Stream]**
...

### Dependency Sketch
- Diagram or text mapping dependencies (e.g., WS1 → WS2 → WS3)
- Explicit task blockers (e.g., T3 blocks T5 because [reason])

### Proposed Sprint Order
- **Sprint 1**: WS1 quick wins and core dependencies
- **Sprint 2**: WS2 lifecycle, failure-handling, and security updates
- **Sprint 3**: WS3 higher-risk integrations and polished elements

### Open Questions
- [List any questions needing resolution before final implementation]

### Confidence Table
| WS | Confidence Level | Reason |
|----|------------------|--------|
| WS1 | High / Medium / Low | [Reason for this rating] |
```
