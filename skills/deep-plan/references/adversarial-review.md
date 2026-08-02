# Adversarial Review (Phase 4)

Brutal review of draft plan before finalization. Two passes: CTO lens, Eng lens.

---

## 1. Outside Voice Activation (Config-first)

A real outside voice is a reviewer that did **not** draft the plan. Do NOT probe the environment — ask the user once, at the start of Phase 4.

**Ask the user (single question):**

> Which reviewer engines are available? Name them: e.g. "subagents", "claude", "codex", "qwen", "gemini", or "none".

Use the answer verbatim — no detection ladder:
- **Subagents** → Sections 2/3 run fresh-context reviewers using the agent's subagent mechanism.
- **A named CLI** (e.g. `claude`, `codex`, `qwen`) → Section 1b invokes it non-interactively.
- **None** → Section 8: no outside voice, warn and skip.

If the user names more than one, prefer the external CLI for at least one pass. Record the engine actually used in the Review Log (Section 4 step 2).

---

## 1b. External CLI Review

For each pass (CTO in Section 2, Eng in Section 3), build the reviewer prompt as one text block: role instructions + the relevant digest. Invoke the user-declared CLI non-interactively:
1. Write the prompt content to a temporary file (e.g., `.deep-plan/tmp_review_prompt.txt`) to avoid command-line length limits.
2. Check CLI flags using `<cli> --help`. If the CLI fails to execute or is not installed, output a warning and fall back to Section 8.
3. Run the CLI by redirecting/piping the file: e.g., `Get-Content .deep-plan/tmp_review_prompt.txt | <cli>` (on Windows) or `<cli> < .deep-plan/tmp_review_prompt.txt` (on Unix/macOS). Capture stdout as the findings.
4. Delete the temporary file immediately after execution.
5. A different model family is a bonus; a fresh trace is what counts. If the CLI shares the drafter's model family (e.g., `claude` matching Claude, or `gemini` matching Gemini), note it in the Review Log.

---

## 1a. Build the Reviewer Digests (once, before passes)

Extract from the living roadmap file (`.deep-plan/<epic-name-in-kebab-case>.md`) and hold in memory:

### 1. CTO Digest (High-Level Product & Scope Focus)
*Exclude all implementation details, files, folders, and SDK mentions.* Include only:
- **PROBLEM** & **OBJECTIVE**
- **IN-SCOPE / OUT-OF-SCOPE** boundaries
- **Workstreams** (WS name, WS Objective, WS Dependencies, WS Risk/Confidence Summary)

### 2. Eng Digest (Full Technical Detail)
Include all technical details:
- **CTO Digest** contents
- **Codebase Context** (existing relevant files, patterns observed, DB schemas)
- **Architecture Decisions** (ID, decision, rationale, status)
- **Tasks tables** (T1.1, T1.2, dependencies, verification commands)
- **Sad Paths** & **Exit Criteria**

This digest is disposable.

---

## 2. CTO Review (Pass 1)

**Delegation Protocol:**
1. Run the reviewer via the engine declared in Section 1 — fresh-context subagent (Role: `CTO Reviewer`) or the user-named external CLI (Section 1b).
2. Prompt the reviewer with the role instructions below, passing the **CTO Digest**.
3. Keep the findings in memory. Do **NOT** edit the roadmap file.

Same model as the drafter is fine — fresh context defeats self-confirmation bias, not the provider.

**CTO Reviewer Instructions:**
```text
Goal: Prove this plan should NOT exist.
You are rewarded for deleting work. Assume engineering resources are scarce.

You are a skeptical CTO reviewing an engineering phase plan. Your job is NOT to validate it — find every problem-fit, scope, assumption, and prioritization issue before engineering wastes time on the wrong thing.

Questions to answer:
- Which workstream can disappear entirely?
- Which milestone has no measurable business value?
- Which assumption has no evidence?
- What is the smallest plan solving 80% of the problem?
- Which task belongs to a future phase?

Never discuss implementation.

Here is the CTO digest:
[CTO Digest]
```

---

## 3. Eng Review (Pass 2)

**Delegation Protocol:**
1. This pass MUST run after the CTO Review (Pass 1) is complete.
2. If the CTO Review produced any findings (e.g., recommending deleting a workstream, changing scope boundaries, or highlighting assumptions without evidence), append these findings to the **Eng Digest** under a new section `## CTO Scope Findings`.
3. Run the reviewer via the engine declared in Section 1 — fresh-context subagent (Role: `Security & Eng Reviewer`) or the user-named external CLI (Section 1b).
4. Prompt the reviewer with the role instructions below, passing the **Eng Digest** (which now includes the CTO findings).
5. Keep the findings in memory. Do **NOT** edit the roadmap file.

**Eng Reviewer Instructions:**
```text
Goal: Break this implementation.
Assume production traffic. Assume hostile inputs. Assume partial failures.

You are a senior engineer doing technical + security adversarial review. Scope/problem-fit review already done. Your job is to locate architecture, implementation risk, resilience, and security issues.

If the CTO reviewer recommended deleting any workstreams or changing scope boundaries (listed under "CTO Scope Findings" in the digest), analyze the technical implications of those changes (e.g., broken dependencies in remaining tasks, required adjustments to other workstreams).

Find:
- Hidden dependency (including dependencies broken if a CTO-recommended deletion occurs)
- Race condition
- Timeout
- Cancellation
- Retry
- Observability
- Migration
- Rollback
- Testing
- Resource leak
- SDK behavior
- Security

For each finding: name it, cite the specific task, explain the risk, and propose a fix.

Here is the Eng digest (including any high-level recommendations from the CTO review):
[Eng Digest]
```

---

## 3a. Confidence Arbitration (The Judge)
This pass acts as an arbiter to reject weak recommendations and prevent architecture astronautics or speculative over-engineering.

Compile the CTO and Eng findings and run all of them through this filter. Keep decisions in memory. Do **NOT** write to the file.

**Judge Instructions:**
```text
Goal: Reject weak recommendations.

For every reviewer finding, you must run the Confidence Arbitration Filter:
1. Finding: [The reviewer's suggested change/risk]
2. Evidence: [The concrete file path, requirement, API constraint, or DB schema that proves this is a real issue. If none, write "None"]
3. Confidence: [High / Medium / Low (Low if Evidence is "None")]
4. Decision: [Accepted (High confidence) | Rejected (Low confidence) | Needs human decision (Medium confidence)]

Reject speculative improvements, architecture astronautics, future-proofing without evidence, and complexity not proportional to project size.

Evidence the judge cannot confirm from its own memory of the project → Needs Human Decision, not Accepted.
```

---

## 4. Amendment Compilation & Checkpoint (Single Stop)
After the Confidence Arbitration Judge compiles the findings:

Format the Judge's Decisions:

```markdown
## Judge's Decisions & Amendments

### Accepted (Confidence: High)
- **Finding:** [finding]
  - Evidence: [evidence]
  - Change: [change]

### Needs Human Decision (Confidence: Medium)
- **Finding:** [finding]
  - Evidence: [evidence]
  - Options/Change: [change]

### Rejected (Confidence: Low)
- **Finding:** [finding]
  - Reason: [reason/lack of evidence]
```

### Critical Design Questions Rule
If the Judge marks any finding as "Needs Human Decision" or identifies any unresolved architectural contradictions, you **must** extract these as explicit questions:

```markdown
### Critical Design Questions:
1. [Question] - Why: [contrasting view or risk]
```

**STOP. Present this list directly in the chat:**

> Review passes and Confidence Arbitration complete. Proposed amendments and critical design questions compiled:
>
> [Proposed Amendments: Accepted / Needs Human / Rejected]
> [Critical Design Questions]
>
> Please answer the critical questions and choose an option:
> A) Accept all Accepted amendments → Apply them to the tasks and scope in the roadmap file (`.deep-plan/<epic-name-in-kebab-case>.md`) and proceed to Phase 5.
> B) Reject/modify specific findings → Discuss changes with the user, update the list, and write only the approved amendments.

### How to Apply Approved Amendments to the Living File:
Once the amendments are approved by the user:
1. **Targeted Edits:** Use code-editing tools (e.g., `replace_file_content`) to directly modify the affected sections (Scope, Tasks, Sad Paths, Exit Criteria) in the living `.deep-plan/<epic-name-in-kebab-case>.md` file. Do NOT rewrite the entire file from scratch.
2. **Update the Review Log:** Locate the `## Review Log` table at the bottom of the roadmap file (defined in `templates/roadmap-template.md`). Fill in the details of this review pass (model, mode, number of findings, status = "Cleared").
3. **Audit Trail:** Append the finalized `## Judge's Decisions & Amendments` section to the end of the file, providing a permanent record of the review outcomes.

**Important:** Do **NOT** edit or write to the living roadmap file until the user has explicitly answered the critical questions and selected A or approved B. All intermediate findings are held in memory.

---

## 5. (Reserved)

---

## 6. Combined Pass
Removed. Same-context self-review rubber-stamps the draft it just wrote. If no subagent is available, see Section 8.

---

## 7. Conditional — UI/UX Lens
If the roadmap includes UI/frontend/mockup/component work, run the UI review checklist from `references/ui-review.md`. Findings are additive to the amendment list and included in the Section 3a / Section 4 checkpoint. Do **NOT** write to the file.

---

## 8. No Outside Voice

If the user declared "none", or the named engine isn't available, tell the user Phase 4 has no outside voice.
1. Render both the CTO and Eng reviewer prompts directly in the chat inside copyable code blocks (with the digests filled in).
2. Instruct the user: "You can copy these prompts into an external LLM interface of your choice to perform a manual review. Paste the findings back here when finished."
3. If the user decides to skip manual review entirely, record "None (Skipped)" in the Review Log and proceed to Section 4 without findings.
4. Do not fake a combined pass in the current context.
