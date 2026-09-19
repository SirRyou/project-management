# Reference: Intake & Grounding (Phases 1 & 2)

## Phase 1: Upfront User Intake (Single Interaction)

Modern agent harnesses provide built-in interactive tools (e.g. `ask_question`). Rather than halting the agent loop multiple times across phases, the PM executes **one structured intake call** at the very beginning of the planning lifecycle.

### Intake Questions Schema
Trigger `ask_question` with the following parameters:

```json
{
  "questions": [
    {
      "question": "How should the agent team handle technical implementation decisions?",
      "options": [
        "(Recommended) Fully Autonomous: PM & Architects choose best-practice patterns; escalate only irreversible risks (e.g. data loss, external budget, major breaking API change).",
        "Collaborative Architect: Consult me on major architectural forks, technology choices, and trade-offs before proceeding."
      ],
      "is_multi_select": false
    },
    {
      "question": "What is the primary objective and nature of this epic?",
      "options": [
        "New Feature (Additive architecture, new endpoints/schemas)",
        "Refactoring / Modernization (Behavior-preserving, strict invariant and test parity)",
        "Bug Fix / Stabilization (Root-cause remediation and edge-case hardening)",
        "Performance / Concurrency (Throughput, caching, race condition elimination)",
        "Security (Auth flows, trust boundaries, permission models, secret management)",
        "Docs / Migration (API documentation, migration guides, changelog)"
      ],
      "is_multi_select": false
    }
  ]
}
```

### Autonomy Mode Setting
- **Autonomous Mode:** PM and specialists resolve gaps, design contracts, and decompose tasks autonomously. No intermediate chat stops unless an irreversible risk or missing credential is encountered.
- **Collaborative Mode:** PM presents the Tier 1 Epic overview and Tier 2 architecture summary for explicit confirmation before task execution begins.

### Agent Team Assembly
After intake, the PM consults the **Task-Type Routing Table** in [agent-catalog.md](agent-catalog.md) to determine which specialist agents to activate for this epic. For example:
- A **Security** epic activates the Security Architect (planning) and Security Auditor (fan-out reviewer).
- A **Performance** epic swaps the Worker Implementer for the Performance Engineer and adds the Performance Benchmarker to the fan-out.
- A **Bug Fix** epic activates the Researcher to investigate root causes before decomposition.

---

## Phase 2: Codebase Grounding & Context Mapping

Once intake is locked, the PM dispatches the **Codebase Explorer Subagent** (`references/subagents/codebase-explorer.md`) to establish ground truth without loading hundreds of source files into the PM's context.

### Explorer Dispatch Protocol
1. Invoke subagent with role `Codebase Explorer`.
2. Provide:
   - Epic goal and requirements.
   - Target directories or suspected subsystems.
3. Require the subagent to use graph exploration (`codegraph`, `graphify`), AST search, and symbol grep.
4. Explorer returns the **Grounding Dossier** (stack, conventions, blast radius, schemas, knowns vs unknowns).

### Unknowns Resolution Rule
If the Grounding Dossier identifies unknown external library contracts or API limits:
1. Attempt immediate resolution via documentation query (e.g., `Context7` or web search).
2. If unresolvable in the current environment, record it as a dedicated **Spike / Research Task (T00)** in the Tier 3 task list to be resolved before dependent implementation tasks run.
