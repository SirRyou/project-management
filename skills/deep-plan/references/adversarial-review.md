# Adversarial Review (Phase 4)

Brutal review of draft plan before finalization. Two passes: CTO lens, Eng lens.

---

## 1. Detect Review Path

```bash
command -v claude  && AGENT=claude
command -v codex   && AGENT=codex
command -v agy     && AGENT=agy
command -v aider  && AGENT=aider
command -v opencode && AGENT=opencode
command -v mentat && AGENT=mentat
command -v ollama && AGENT=ollama
```

PowerShell fallback (Windows-native only):

```powershell
Get-Command claude, codex, agy, opencode, ollama -ErrorAction SilentlyContinue
```

Priority: provider **different from plan-drafting model** first.

### Invocation

| CLI | Invocation | Notes |
|:---|:---|:---|
| `claude` | `claude -p "<prompt>"` | Anthropic |
| `codex` | `codex exec "<prompt>"` | OpenAI one-shot |
| `aider` | `aider --model <model-name>` | Multi-provider open-source coding agent supporting OpenAI, Anthropic, and local models. |
| `agy` | `agy -p "<prompt>"` | Google's Antigravity CLI. |
| `opencode` | `opencode run "<prompt>"` | Multi-provider, model via config |
| `mentat` | `mentat <paths-to-files>` | Context-driven multi-file AI coding assistant focused on workspace directory context. |
| `ollama` | `ollama run <model> "<prompt>"` | Orchestrator for serving and running open-weights LLMs locally from the terminal. |

Pipe draft plan inline or as file content within prompt.

### Path Selection

- **CLI found** → ask permission to use directly. Strongest outside voice — different training, different blind spots. dont forget add timed out.
- **No CLI** → spawn subagent with different model override if available.
- **No other model** → spawn same-model subagent (fresh context). **Warn user**: "No other model provider detected. Review uses same-model subagent — bias caveat applies. Findings may reflect same training blind spots."

### Known Issue

- `outside voice` cant read plan -> permission error.
- no output/response in terminal:
  - timed out -> longer timed out, try 150+
  - use interactive mode & tell to write file somewhere so you can read.
  - credit usage empty -> fallback other or subagent.

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

```
ask_question(
  question="Review passes complete. Check findings above.",
  options=[
    "Findings correct. Proceed to amendment compilation.",
    "Need to modify or reject some findings."
  ]
)
```

### 4.1 Modifying the plan

- if user want modify or reject, discuss it and ask why.
- done resolving it? run review checkpoint

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

```
ask_question(
  question="Amendment list correct? Override or add anything?",
  options=[
    "Correct. Write final roadmap.",
    "Need changes to amendment list."
  ]
)
```

User requests changes → update draft, present again, repeat checkpoint.

---

## 6. Combined Pass (Quick Path / NO_OTHER_MODEL)

If Quick Path or no other model available → merge CTO + Eng into single pass:

```
You are a skeptical CTO and Senior Principal Architect reviewing an engineering
phase plan. Uncover every blind spot, problem-fit gap, resilience failure,
and security risk.

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

If scope has UI/frontend/mockup/component work → invoke related UI review skill if available, no? use (`references/emil-design-eng/SKILL.md`). Findings additive to amendment list.

---

## 8. Tool Fallback

Any helper missing or fails → fall back to manual or skip if not critical to final plan.
