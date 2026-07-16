# Adversarial Review (Phase 4)

Brutal review of draft plan before finalization. Two passes: CTO lens, Eng lens.

---

## 1. Detect Review Path

Check for CLI models available on the system. Priority: use a model **different from the one that drafted the plan** — different training catches different blind spots.

### Path Selection

- **Different-model CLI available** → use it directly. Strongest outside voice.
- **No different-model CLI** → spawn subagent with different model provider if available.
- **No other model at all** → spawn same-model subagent with fresh context. Warn user: "No other model provider detected. Review uses same-model — bias caveat applies. Findings may reflect same training blind spots."

### Timeout handling

CLI tools may time out on large plans. If no output received:
1. Increase timeout (150s+)
2. Try interactive mode — have the reviewer write findings to a file you can read
3. If credits exhausted, fall back to subagent

---

## 2. CTO Review (Pass 1)

Give reviewer this role — be BRUTAL:

```
You are a skeptical CTO reviewing an engineering phase plan. Your job is NOT
to validate it — find every problem-fit, scope, assumption, and prioritization
issue before engineering wastes time on the wrong thing.

Challenge on:
1. PROBLEM-FIT: Does plan solve underlying problem, or just literal request?
2. SCOPE: Boundary right? What's missing? What's bloat?
3. ASSUMPTIONS: List every implicit assumption. Which wrong or unvalidated?
4. SEQUENCING: Right first thing? Real critical path?
5. OVER-ENGINEERING: What's solving hypothetical problem, not real one?

For each finding: name it, explain why, propose change. Be brutal.

Here is the plan:
[plan content]
```

**After CTO review**: validate findings, save to review log.

---

## 3. Eng Review (Pass 2)

Give reviewer this role — be BRUTAL:

```
You are a senior engineer doing technical + security adversarial review.
Scope/problem-fit review already done. Your job: architecture, implementation
risk, resilience, security.

Challenge on:
1. HIDDEN DEPENDENCIES: Dependencies between tasks author missed?
2. SDK/LIBRARY RISKS: Third-party behaviors invalidating approach?
3. OVER-CONFIDENCE: Tasks marked High/Medium confidence but risky?
4. MISSING TASKS: Implementation work implied but not listed?
5. TESTING GAPS: Exit criteria can't actually be verified?
6. RESOURCE LEAKS: Async lifecycle, event listener, resource issues?
7. SECURITY: Missing input validation, permission checks, secret handling,
   trust boundary leaks? Where would adversarial input break assumptions?

For each finding: name it, cite specific task, explain risk, propose fix.

Here is the plan:
[plan content]
```

**After Eng review**: combine with CTO findings, validate & save.

---

## 4. Review Checkpoint

After both passes, confirm with user:

> Review passes complete. Check findings above.
>
> A) Findings correct. Proceed to amendment compilation.
> B) Need to modify or reject some findings.

### 4.1 Modifying the plan

If user wants to modify or reject findings, discuss and ask why. Once resolved, re-present for confirmation.

---

## 5. Amendment Compilation

Compile findings:

```markdown
## Amendments

From CTO Review:
- [finding] → [change] / REJECTED: [reason]

From Eng Review:
- [finding] → [change] / REJECTED: [reason]
```

Confirm with user:

> Amendment list correct? Override or add anything?
>
> A) Correct. Write final roadmap.
> B) Need changes to amendment list.

User requests changes → update draft, present again, repeat checkpoint.

---

## 6. Combined Pass (Quick Path / No Other Model)

If Quick Path or no other model available → merge CTO + Eng into single pass with explicit Counter-Bias Instructions:

```
You are a skeptical CTO and Senior Principal Architect performing an adversarial review.
UNLIKE NORMAL REVIEWS, you are explicitly primed to hunt for self-confirmation bias.

Counter-Bias Checklist:
- Challenge every assumption marked "assumed obvious" or "standard pattern".
- Verify that every work package has a machine-executable verification step (tests/lint/cli).
- Assume every network/database call can hang for 30s or return malformed JSON.
- Assume inputs are crafted by an adversary seeking auth bypass or secret extraction.

Analyze on:
1. PROBLEM-FIT: Solves underlying problem or just literal request?
2. SCOPE & BOUNDARIES: Right scope? Bloat? Missing?
3. ASSUMPTIONS & SEQUENCING: Implicit assumptions? Correct work stream order?
4. RESILIENCE: Missing fail-safe, timeout, retry, fallback?
5. SECURITY: Unvalidated inputs, auth bypass, secret exposure, trust boundary leaks?

Propose concrete changes for each issue. Be critical.

Here is the plan:
[plan content]
```

---

## 7. Conditional — UI/UX Lens

If scope has UI/frontend/mockup/component work → run the UI review checklist from `references/ui-review.md`. Findings are additive to the amendment list.

---

## 8. Tool Fallback

Any helper missing or fails → fall back to manual review or skip if not critical to final plan.
