# Deep Plan

Resilient, problem-driven, security-aware feature planning for AI coding agents.

## What Is This Skill?

Deep Plan is a structured planning skill that guides AI agents through a 5-phase workflow for complex software changes. It produces implementation-ready roadmaps that consider security, resilience, and failure modes—not just happy-path implementations.

The skill enforces disciplined planning through:
- **Gap analysis** using multiple lenses (problem-fit, resilience, security)
- **Adversarial review** with "outside voice" principle
- **Scope management** with soft locks and unlock triggers
- **Progress persistence** across sessions

## What Problem Does It Solve?

AI agents often jump straight to implementation without adequate planning. This leads to:

### Blind Spots
Agents implement the literal request without understanding the underlying problem. Deep Plan forces scope analysis first.

### Security Gaps
Trust boundaries and security models are overlooked. Deep Plan includes a dedicated security lens in gap analysis.

### Single-Path Designs
Without adversarial review, plans reflect the agent's training biases. Deep Plan uses "outside voice" (different model providers) to catch blind spots.

### Scope Creep
Plans grow uncontrollably during implementation. Deep Plan uses soft scope locks that unlock only for genuine discoveries.

### Incomplete Resilience
Error handling and failure modes are afterthoughts. Deep Plan includes a dedicated resilience lens.

## Why Use This Skill?

### 1. Problem-Driven Planning
Deep Plan starts with understanding the *why*, not just the *what*:

```
# Without Deep Plan
User: "Add rate limiting"
Agent: *implements rate limiting*

# With Deep Plan
User: "Add rate limiting"
Deep Plan: "What problem are you solving? API abuse? Cost control? Fairness?"
→ Produces solution that addresses root cause
```

### 2. Multi-Lens Analysis
Every gap is analyzed through three lenses:
- **Problem-Fit**: Does this solve the actual problem?
- **Resilience**: What happens when things fail?
- **Security**: What trust boundaries are affected?

### 3. Adversarial Review
Plans are reviewed using the "outside voice" principle:
- Different model providers catch different blind spots
- Automated review paths (CLI, subagent, same-model fallback)
- Weighted scoring prevents false confidence

### 4. Flexible Execution
Choose the right path for your epic:
- **Quick Path**: 3-step workflow for simple epics (≤3 work streams)
- **Full Path**: 5-phase workflow for complex features
- **Auto-Escalation**: Quick path automatically escalates when complexity exceeds thresholds

### 5. Progress Persistence
Resume planning across sessions:
```
.deep-plan/{feature-slug}/
├── plan.md              # Living document (single source of truth)
├── progress.json        # Checkpoint state
└── v{N}-{date}.md       # Versioned snapshots
```

## Quick Start

### Prerequisites

- AI coding agent that supports skill loading
- Git (recommended, for version control)
- CLI agents for adversarial review (optional):
  - `claude`, `codex`, `aider`, `opencode`, `ollama`, etc.

### Installation

1. Copy the skill to your agent's skill directory:
   ```bash
   cp -r deep-plan /path/to/your/agent/skills/
   ```

2. Add `.deep-plan/` to `.gitignore` if planning files are temporary:
   ```bash
   echo ".deep-plan/" >> .gitignore
   ```

### Basic Usage

1. **Load the skill** when planning a complex feature
2. **Phase 1**: Understand scope and requirements
3. **Phase 2**: Enumerate gaps using three lenses
4. **Phase 3**: Draft roadmap
5. **Phase 4**: Adversarial review (if needed)
6. **Phase 5**: Finalize roadmap

## Workflow Phases

### Phase 1: Understand Scope
Understand baseline requirements and context. If scope is unclear, ask user before proceeding.

**Output**: Scope Brief

### Phase 2: Enumerate Gaps
Analyze codebase using three lenses:
- **Problem-Fit Lens**: Does the solution address the root problem?
- **Resilience Lens**: What happens when things fail?
- **Security Lens**: What trust boundaries are affected?

**Output**: Gap Analysis with severity ratings (CRITICAL, HIGH, MEDIUM, LOW)

### Phase 3: Draft Roadmap
Construct lightweight, tentative roadmap with:
- Work packages (independent, deliverable units)
- Dependencies and sequencing
- Verification steps

**Output**: Draft Roadmap

### Phase 4: Adversarial Review
Run adversarial review using "outside voice" principle:

```bash
# Detection order (different training = better review)
command -v claude  && AGENT=claude
command -v codex   && AGENT=codex
command -v aider   && AGENT=aider
command -v opencode && AGENT=opencode
command -v ollama && AGENT=ollama
```

**Review Paths**:
1. CLI found → Use directly (strongest outside voice)
2. No CLI → Subagent with different model
3. No other model → Same-model subagent (with bias warning)

**Output**: Review Results with weighted scoring

### Phase 5: Finalize Roadmap
Generate final, comprehensive roadmap with:
- Quality gates
- Verification steps
- Execution confirmation (user must approve before implementation)

**Output**: Final Roadmap

## Execution Paths

### Quick Path (Simple Epics)
For small changes (≤3 work streams, 0 CRITICAL items expected):
1. Scope Brief
2. Gap Analysis (condensed)
3. Living `plan.md`

**Auto-Escalate Conditions**:
- Phase 2 yields MISFIT or CRITICAL items
- Total scope exceeds 15 tasks

### Full Path (Default)
For complex features:
1. Phase 1: Understand Scope
2. Phase 2: Enumerate Gaps
3. Phase 3: Draft Roadmap
4. Phase 4: Adversarial Review
5. Phase 5: Finalize Roadmap

## Workflow Flexibility

### Early Exit
Skip Phase 4 if:
- Phase 2 yields all FIT verdicts
- 0 CRITICAL items
- ≤5 total gaps

### Jump-Back
Phase 4 → Phase 2 if:
- Review finds scope issues
- New items needed
- Wrong boundaries identified

### Parallel Execution
- Phase 2: All three lenses run in parallel per item
- Phase 4: CTO and Eng review passes run parallel if different reviewers available

## Special Considerations

### UI Projects
If roadmap touches user interfaces or visual components, execute UI review checklist.

### Git Awareness
Before planning:
- Verify git initialized
- Check for uncommitted changes
- Check for branch divergence

### Execution Confirmation
Final roadmap execution is **not automatic**. Don't begin implementation without explicit user confirmation.

## Common Mistakes

1. **Skipping Adversarial Review**: Missing edge cases, single-path designs
2. **Starting Code Work Automatically**: Implementing before user approval
3. **Vague Task Descriptions**: Roadmap items lacking concrete verification steps

## Reference Files

| File | Purpose |
|------|---------|
| `scope-analysis.md` | Scope understanding and lock/unlock triggers |
| `gap-analysis.md` | Multi-lens analysis with quick-skip and focus rules |
| `roadmap-draft.md` | Draft plan template |
| `adversarial-review.md` | Review flow and weighted threshold |
| `quality-gates.md` | Quality verification steps |
| `execution-handoff.md` | Execution confirmation process |
| `ui-review.md` | UI-specific review checklist |
| `quick-path.md` | 3-step workflow for simple epics |

## Contributing

See the [root README](../../README.md) for contribution guidelines.

## License

MIT License
