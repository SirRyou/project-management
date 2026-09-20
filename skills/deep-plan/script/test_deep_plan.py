from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import deep_plan  # noqa: E402


VALID_TASK = """# Tier 3: T01: Core

## 1. Task Metadata

- **Task ID:** T01
- **Parent Module:** `modules/M01-core.md`
- **Intent Trace:** `00-intent.md#objective`
- **Invariant Trace:** `INV-1`
- **Risk Trace:** `02-risk-register.md#R01`
- **Kind:** implementation
- **Verification Mode:** static-config
- **Prerequisite Tasks:** None
- **Target Files and Symbols:** `src/core.ts#run`
- **Completion Criterion:** The command exits successfully.

## 2. Dependency and Output Contract

- **Required Artifacts or Contracts:** Intent and module contract.
- **Expected Outputs:** A committed implementation.
- **Downstream Consumers:** None

## 3. Implementation Directive

1. Confirm prerequisite artifacts and repository state.

## 4. Sad Paths and Failure Defenses

| Failure / Abuse Vector | Detection Point | Defense / Fallback Action |
| :--- | :--- | :--- |
| Invalid input | Boundary | Reject input. |

## 5. Acceptance and Verification

- **Acceptance Criteria:**
  1. The task has a concrete completion criterion.
- **Verification Command(s):**
  ```bash
  python -c "print('ok')"
  ```
- **Expected Evidence:** Exit code 0.
- **Non-Vacuity or Applicability Note:** The command checks parseable configuration.
- **Quality Checks:** N/A with reason: no project lint configuration exists.
"""

MULTI_STEP_TASK = """# Tier 3: T01: Core

## 1. Task Metadata

- **Task ID:** T01
- **Parent Module:** `modules/M01-core.md`
- **Intent Trace:** `00-intent.md#objective`
- **Invariant Trace:** `INV-1`
- **Risk Trace:** `02-risk-register.md#R01`
- **Kind:** implementation
- **Verification Mode:** static-config
- **Prerequisite Tasks:** None
- **Target Files and Symbols:** `src/core.ts#run`
- **Completion Criterion:** The command exits successfully.

## 2. Dependency and Output Contract

- **Required Artifacts or Contracts:** Intent and module contract.
- **Expected Outputs:** A committed implementation.
- **Downstream Consumers:** None

## 3. Implementation Directive

1. Confirm prerequisite artifacts and repository state.
2. Follow the ordered steps below without assuming unfinished work will supply missing behavior.
3. Preserve linked invariants and document any necessary assumption.

- **Step 1:** Write failing test
- **Step 2:** Implement core functionality
- **Step 3:** Verify passing test and quality checks

## 4. Sad Paths and Failure Defenses

| Failure / Abuse Vector | Detection Point | Defense / Fallback Action |
| :--- | :--- | :--- |
| Invalid input | Boundary | Reject input. |

## 5. Acceptance and Verification

- **Acceptance Criteria:**
  1. The task has a concrete completion criterion.
- **Verification Command(s):**
  ```bash
  python -c "print('ok')"
  ```
- **Expected Evidence:** Exit code 0.
- **Non-Vacuity or Applicability Note:** The command checks parseable configuration.
- **Quality Checks:** N/A with reason: no project lint configuration exists.
"""


class DeepPlanCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / ".deep-plan"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_cli(self, *arguments: str) -> int:
        return deep_plan.main(["--root", str(self.root), *arguments])

    def test_init_creates_valid_scaffold(self) -> None:
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        self.assertEqual(self.run_cli("validate", "example-epic", "--stage", "scaffold"), 0)

    def test_valid_plan_syncs_ledger_and_reports_ready_task(self) -> None:
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        epic = self.root / "example-epic"
        (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
        (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
        (epic / "dependency-dag.json").write_text(json.dumps({
            "epic": "example-epic",
            "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
        }), encoding="utf-8")
        self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
        self.assertEqual(self.run_cli("validate", "example-epic"), 0)
        self.assertEqual(self.run_cli("ready", "example-epic"), 0)

    def test_pm_state_requires_complete_review_fan_in_before_completion(self) -> None:
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        epic = self.root / "example-epic"
        (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
        (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
        (epic / "dependency-dag.json").write_text(json.dumps({
            "epic": "example-epic",
            "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
        }), encoding="utf-8")
        (epic / "reviews").mkdir()
        (epic / "verification").mkdir()
        self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
        self.assertEqual(self.run_cli("transition", "example-epic", "T01", "--to", "IN_PROGRESS"), 0)
        self.assertEqual(self.run_cli("worker-record", "example-epic", "T01", "--commit", "abcdef1", "--evidence", "reviews/worker.md"), 2)
        (epic / "reviews" / "worker.md").write_text("worker evidence\n", encoding="utf-8")
        self.assertEqual(self.run_cli("worker-record", "example-epic", "T01", "--commit", "abcdef1", "--evidence", "reviews/worker.md"), 0)
        self.assertEqual(self.run_cli("transition", "example-epic", "T01", "--to", "INTEGRATING"), 2)
        for axis in ("standards", "spec", "challenger"):
            evidence = epic / "reviews" / f"{axis}.md"
            evidence.write_text(f"{axis} PASS\n", encoding="utf-8")
            self.assertEqual(self.run_cli("review-record", "example-epic", "T01", "--axis", axis, "--verdict", "PASS", "--evidence", f"reviews/{axis}.md"), 0)
        self.assertEqual(self.run_cli("transition", "example-epic", "T01", "--to", "INTEGRATING"), 0)
        self.assertEqual(self.run_cli("integration-record", "example-epic", "T01", "--commit", "abcdef2"), 0)
        (epic / "verification" / "integrated.md").write_text("integrated verification\n", encoding="utf-8")
        self.assertEqual(self.run_cli("verify-record", "example-epic", "T01", "--evidence", "verification/integrated.md"), 0)
        self.assertEqual(self.run_cli("transition", "example-epic", "T01", "--to", "COMPLETED"), 0)
        self.assertEqual(self.run_cli("validate", "example-epic"), 0)

    def test_cycle_fails_validation(self) -> None:
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        epic = self.root / "example-epic"
        (epic / "dependency-dag.json").write_text(json.dumps({
            "epic": "example-epic",
            "tasks": [
                {"id": "T01", "module": "M01", "kind": "implementation", "dependencies": ["T02"]},
                {"id": "T02", "module": "M01", "kind": "implementation", "dependencies": ["T01"]},
            ],
        }), encoding="utf-8")
        self.assertEqual(self.run_cli("validate", "example-epic"), 1)

    def test_worktree_creation_allows_managed_plan_state(self) -> None:
        repository = Path(self.temp_dir.name) / "repo"
        repository.mkdir()
        subprocess.run(["git", "init"], cwd=repository, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "deep-plan@example.test"], cwd=repository, check=True)
        subprocess.run(["git", "config", "user.name", "Deep Plan Test"], cwd=repository, check=True)
        (repository / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=repository, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=repository, check=True, capture_output=True)
        original_root, original_cwd = self.root, Path.cwd()
        self.root = repository / ".deep-plan"
        os.chdir(repository)
        try:
            self.assertEqual(self.run_cli("init", "example-epic"), 0)
            epic = self.root / "example-epic"
            (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
            (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
            (epic / "dependency-dag.json").write_text(json.dumps({
                "epic": "example-epic",
                "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
            }), encoding="utf-8")
            self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
            self.assertEqual(self.run_cli("worktree-create", "example-epic", "T01", "--parent", "HEAD"), 0)
            self.assertTrue((repository / ".worktrees" / "T01-core").is_dir())
            self.assertIn("IN_PROGRESS", (epic / "progress-ledger.md").read_text(encoding="utf-8"))
        finally:
            os.chdir(original_cwd)
            self.root = original_root

    def _setup_git_repo(self) -> Path:
        repository = Path(self.temp_dir.name) / f"repo-{os.getpid()}-{id(self)}"
        repository.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init"], cwd=repository, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "deep-plan@example.test"], cwd=repository, check=True)
        subprocess.run(["git", "config", "user.name", "Deep Plan Test"], cwd=repository, check=True)
        (repository / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=repository, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=repository, check=True, capture_output=True)
        return repository

    def test_pause_generates_handoff_and_records_step_progress(self) -> None:
        repository = self._setup_git_repo()
        original_root, original_cwd = self.root, Path.cwd()
        self.root = repository / ".deep-plan"
        os.chdir(repository)
        try:
            self.assertEqual(self.run_cli("init", "example-epic"), 0)
            epic = self.root / "example-epic"
            (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
            (epic / "tasks" / "T01-core.md").write_text(MULTI_STEP_TASK, encoding="utf-8")
            (epic / "dependency-dag.json").write_text(json.dumps({
                "epic": "example-epic",
                "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
            }), encoding="utf-8")
            self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
            self.assertEqual(self.run_cli("transition", "example-epic", "T01", "--to", "IN_PROGRESS"), 0)

            result = self.run_cli(
                "pause", "example-epic",
                "--reason", "quota",
                "--note", "Waiting for tomorrow",
                "--task-progress", "T01:2:3",
            )
            self.assertEqual(result, 0)

            state = json.loads((epic / "execution-state.json").read_text(encoding="utf-8"))
            self.assertIsNotNone(state.get("pause_state"))
            self.assertEqual(state["pause_state"]["reason"], "quota")
            self.assertEqual(state["pause_state"]["note"], "Waiting for tomorrow")
            self.assertEqual(state["tasks"]["T01"]["step_progress"]["completed_step"], 2)
            self.assertEqual(state["tasks"]["T01"]["step_progress"]["total_steps"], 3)
            self.assertEqual(state["tasks"]["T01"]["step_progress"]["summary"], "Implement core functionality")

            handoff_files = list((epic / "handoff").glob("HANDOFF-*.md"))
            self.assertEqual(len(handoff_files), 1)
            dossier = handoff_files[0].read_text(encoding="utf-8")
            self.assertIn("quota", dossier)
            self.assertIn("Waiting for tomorrow", dossier)
            self.assertIn("T01", dossier)
            self.assertIn("**Last Completed Step:** 2 of 3", dossier)
            self.assertIn("Implement core functionality", dossier)
            self.assertIn("**Next Step:** 3", dossier)
            self.assertIn("Verify passing test and quality checks", dossier)

            ledger_text = (epic / "progress-ledger.md").read_text(encoding="utf-8")
            self.assertIn("## 5. Resume Checkpoint", ledger_text)
            self.assertIn("T01: IN_PROGRESS (Step 2/3)", ledger_text)
            self.assertIn(handoff_files[0].name, ledger_text)
        finally:
            os.chdir(original_cwd)
            self.root = original_root

    def test_pause_rejects_already_paused_epic(self) -> None:
        repository = self._setup_git_repo()
        original_root, original_cwd = self.root, Path.cwd()
        self.root = repository / ".deep-plan"
        os.chdir(repository)
        try:
            self.assertEqual(self.run_cli("init", "example-epic"), 0)
            epic = self.root / "example-epic"
            (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
            (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
            (epic / "dependency-dag.json").write_text(json.dumps({
                "epic": "example-epic",
                "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
            }), encoding="utf-8")
            self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)

            self.assertEqual(self.run_cli("pause", "example-epic", "--reason", "tired"), 0)
            self.assertEqual(self.run_cli("pause", "example-epic", "--reason", "eod"), 2)
        finally:
            os.chdir(original_cwd)
            self.root = original_root

    def test_resume_clears_pause_state_and_records_event(self) -> None:
        repository = self._setup_git_repo()
        original_root, original_cwd = self.root, Path.cwd()
        self.root = repository / ".deep-plan"
        os.chdir(repository)
        try:
            self.assertEqual(self.run_cli("init", "example-epic"), 0)
            epic = self.root / "example-epic"
            (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
            (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
            (epic / "dependency-dag.json").write_text(json.dumps({
                "epic": "example-epic",
                "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
            }), encoding="utf-8")
            self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
            self.assertEqual(self.run_cli("pause", "example-epic", "--reason", "quota"), 0)

            self.assertEqual(self.run_cli("resume", "example-epic"), 0)
            state = json.loads((epic / "execution-state.json").read_text(encoding="utf-8"))
            self.assertIsNone(state.get("pause_state"))
            resumed_events = [e for e in state["events"] if e["action"] == "resumed"]
            self.assertEqual(len(resumed_events), 1)
        finally:
            os.chdir(original_cwd)
            self.root = original_root

    def test_resume_without_prior_pause_still_works(self) -> None:
        repository = self._setup_git_repo()
        original_root, original_cwd = self.root, Path.cwd()
        self.root = repository / ".deep-plan"
        os.chdir(repository)
        try:
            self.assertEqual(self.run_cli("init", "example-epic"), 0)
            epic = self.root / "example-epic"
            (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
            (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
            (epic / "dependency-dag.json").write_text(json.dumps({
                "epic": "example-epic",
                "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
            }), encoding="utf-8")
            self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)

            self.assertEqual(self.run_cli("resume", "example-epic"), 0)
            state = json.loads((epic / "execution-state.json").read_text(encoding="utf-8"))
            resumed_events = [e for e in state["events"] if e["action"] == "resumed"]
            self.assertEqual(len(resumed_events), 1)
        finally:
            os.chdir(original_cwd)
            self.root = original_root

    def test_resume_reconciles_wip_commit_with_incomplete_steps(self) -> None:
        repository = self._setup_git_repo()
        original_root, original_cwd = self.root, Path.cwd()
        self.root = repository / ".deep-plan"
        os.chdir(repository)
        try:
            self.assertEqual(self.run_cli("init", "example-epic"), 0)
            epic = self.root / "example-epic"
            (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
            (epic / "tasks" / "T01-core.md").write_text(MULTI_STEP_TASK, encoding="utf-8")
            (epic / "dependency-dag.json").write_text(json.dumps({
                "epic": "example-epic",
                "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
            }), encoding="utf-8")
            self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
            self.assertEqual(self.run_cli("worktree-create", "example-epic", "T01", "--parent", "HEAD"), 0)

            # Create a WIP commit in the worktree
            worktree_dir = repository / ".worktrees" / "T01-core"
            (worktree_dir / "src").mkdir(parents=True, exist_ok=True)
            (worktree_dir / "src" / "core.ts").write_text("export const x = 1;\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=worktree_dir, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "wip(T01): step 2/3"], cwd=worktree_dir, check=True, capture_output=True)

            # Pause with step progress 2 of 3
            self.assertEqual(self.run_cli("pause", "example-epic", "--reason", "quota", "--task-progress", "T01:2:3"), 0)

            # Check dossier has WIP commit
            handoff_files = list((epic / "handoff").glob("HANDOFF-*.md"))
            self.assertEqual(len(handoff_files), 1)
            dossier_text = handoff_files[0].read_text(encoding="utf-8")
            self.assertIn("WIP Commit:", dossier_text)

            # Resume and capture output
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(self.run_cli("resume", "example-epic"), 0)
            output = buf.getvalue()

            self.assertIn("Worktree exists (with WIP commit) (Step 2/3)", output)
            self.assertIn("Action: Continue from Step 3", output)
            self.assertNotIn("advance to IN_REVIEW", output)
        finally:
            os.chdir(original_cwd)
            self.root = original_root


if __name__ == "__main__":
    unittest.main()
