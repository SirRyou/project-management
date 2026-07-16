# Reference: Quality Gates & Self-Check Checklist

This reference document outlines the quality gates required before finalizing the phase roadmap.

---

## 1. High-Level Quality Gates

Before saving and presenting the final roadmap, verify the following:

- [ ] **Scope Alignment**: Every in-scope item has at least one corresponding task.
- [ ] **Gap Mitigations**: All critical/high failure modes and security risks have explicit mitigation tasks.
- [ ] **Machine Verification Commands**: Every task has a machine-executable verification command (e.g. `npm test`, `pytest`, `cargo test`, `git diff`) — no subjective "looks good" text.
- [ ] **Invariant Assertions**: System invariants are explicitly checked before and after execution steps.
- [ ] **Git-Aware Versioning**: The roadmap is updated incrementally in the living `.deep-plan/plan.md` file.
- [ ] **User Agreement**: All adversarial review findings are resolved and confirmed by the user.
