# Reference: Intent, Grounding, Gaps, and Risks

Use this reference for the first two planning phases. Keep the writing imperative and runtime-neutral.

## Phase 1: Intent and Entry Preflight

Infer the user's communication depth from the request. Do not ask the user to classify themselves as technical or casual. Keep the planning rigor constant and adapt only the visible explanation depth, terminology, and implementation detail.

Capture these intent fields:

- Goal and problem statement.
- Desired behaviors and outputs.
- Candidate invariants and acceptance conditions.
- Scope constraints and repository constraints.
- Provisional complexity and uncertainty.
- Autonomy mode: Autonomous or Collaborative.
- Task type when it cannot be inferred reliably.
- Unresolved decisions and assumptions.

Persist the result as `.deep-plan/<epic-slug>/00-intent.md`. Mark inferred invariants and assumptions explicitly. Ask a question only when choosing incorrectly would materially change the plan.

## Question Tool Contract

Use the runtime's structured question tool when available. Keep questions one at a time for material decisions. Present concrete options, a recommended choice, and the tradeoffs. Do not assume a vendor-specific tool name or schema in this skill.

Pause even in Autonomous mode for a boundary-changing architecture fork: module boundaries, data ownership, public contracts, external providers, security trust boundaries, or irreversible migration strategy.

In Collaborative mode, require explicit approval after the complete plan. In Autonomous mode, proceed after plan validation unless a boundary-changing fork requires synchronization.

## Phase 2: Repository Grounding and Context Mapping

Use repository-provided mapping tools first. If the repository has no suitable tool, dispatch the Codebase Explorer with:

- Epic goal and requirements.
- Target directories or suspected subsystems.
- A requirement to return file-and-line evidence for every important conclusion.
- A requirement to record search coverage and unresolved areas.

Persist the result as `.deep-plan/<epic-slug>/01-grounding.md`. Include:

1. Architectural stack and frameworks.
2. Relevant file map and blast radius.
3. Established codebase conventions and verification commands.
4. Dependency and contract map.
5. Known facts versus unverified unknowns.
6. Tooling coverage and remaining gaps.

Create `.deep-plan/<epic-slug>/02-risk-register.md` after grounding and before architecture design. Rank risks by impact and uncertainty. Require Tier 2 architecture to trace each material risk to mitigation, acceptance, or explicit deferral.

Finalize complexity after grounding. Derive it from dependency breadth, uncertainty, change risk, verification cost, and coordination cost. Use the summary level only as a routing aid; retain the evidence behind it.

## Unknown Resolution

Resolve external library or API unknowns through the repository's approved documentation workflow. If an unknown remains material, create a research task in the DAG with a stable research identifier, explicit evidence output, and dependencies for blocked implementation tasks. Do not let workers guess at unresolved external behavior.
