# Tree of Work Skill - Test Book

This test book describes the validation strategy, test suites, and trigger evaluation scenarios for the `tree-of-work` skill (v2.0).

---

## 1. Test Architecture Overview

Validation of the `tree-of-work` skill is split into two components:
1. **Trigger Classification Evals:** Programmatic check of prompt trigger heuristics against a curated list of user queries (`evals.json`).
2. **CLI Integration Tests:** Executed via an isolated temporary directory using Python's `unittest` module, testing all CLI commands, validation rules, entropy checks, and onboarding penyerapan otomatis (auto-absorption).

All tests are implemented in [test_runner.py](file:///D:/Project/skill-library/project-management/tree-of-work/evals/test_runner.py).

---

## 2. Trigger Evaluation Scenarios (`evals.json`)

The skill triggers on tasks involving multiple steps, context switching, or sub-agent delegation, and remains inactive (ephemeral/flat) for single-step, trivial, or stateless operations.

| Case ID | User Prompt | Expected Trigger | Rationale |
|:---:|---|:---:|---|
| **1** | *"I've been working on this feature for hours and my session crashed. Where was I? Can you help me figure out what I was doing?"* | **Yes** | Triggered by context recovery / session crash. |
| **2** | *"Let's break down this large refactoring into manageable tasks and track progress as we go."* | **Yes** | Triggered by multi-step project organization. |
| **3** | *"I need to delegate the frontend validation work to a sub-agent while I work on the API. How do we not step on each other?"* | **Yes** | Triggered by sub-agent delegation. |
| **4** | *"what's the quickest way to convert this json file to yaml"* | **No** | Stateless, single-step utility operation. |
| **5** | *"Can you write a Python script that reads a CSV and uploads each row to our postgres database?"* | **No** | Flat code generation task. |
| **6** | *"I keep losing context when my agent sessions timeout. Is there a way to persist task state across sessions?"* | **Yes** | Triggered by context/session persistence. |
| **7** | *"organize this work for me — I have 5 things to do and I need to track which ones are done"* | **Yes** | Triggered by multi-task tracking. |
| **8** | *"fix the typo in the README"* | **No** | Trivial single-line code modification. |
| **9** | *"I'm switching focus to the auth bug — how do I make sure I don't lose track of the payment work I was doing?"* | **Yes** | Triggered by task/focus context switching. |
| **10** | *"write me a fibonacci function in python"* | **No** | Standard stateless snippet request. |

---

## 3. CLI Integration Tests

The integration test suite verifies the functionality of the CLI tool (`tree_of_work.py`) under several environment configurations.

### Test Cases

1. **Default Initialization (`test_cli_init_default`):**
   - Asserts that running `init` creates `.agent/tree-of-work/current-state.md` with default setup state and configures the workspace `.gitignore`.
2. **Legacy State Auto-Absorption (`test_cli_init_with_legacy_files`):**
   - Mocks the presence of legacy tracking documents (`CLAUDE.md`, `ROADMAP.md`, `TODO.md`) in the workspace root.
   - Asserts that the first active/in-progress task is set to `ACTIVE` in `current-state.md` (e.g. `[from: ROADMAP.md]`).
   - Asserts that all other tasks from CLAUDE and TODO are parsed and added to the `## PARKED / BLOCKED` section.
3. **State File Validation (`test_cli_validate`):**
   - Verifies that a well-structured state file parses as `VALID`.
   - Verifies that validation fails if multiple tasks are marked `ACTIVE`.
4. **Security & Entropy Validation (`test_cli_entropy_validation`):**
   - Adds a high-entropy simulated API key to `current-state.md`.
   - Asserts that validation fails with a security alert, blocking potential credentials leakage.

---

## 4. How to Run Evals and Tests

To run the full suite of evals and integration tests, run the following command from the repository root:

```bash
python tree-of-work/evals/test_runner.py
```

Expected output showing successful completion:
```text
......
----------------------------------------------------------------------
Ran 6 tests in 0.270s

OK
```
