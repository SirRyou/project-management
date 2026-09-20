from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
