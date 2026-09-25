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

    def test_worker_record_accepts_remediation_result_and_reopens_review(self) -> None:
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        epic = self.root / "example-epic"
        (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
        (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
        (epic / "dependency-dag.json").write_text(json.dumps({
            "epic": "example-epic",
            "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
        }), encoding="utf-8")
        self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
        self.assertEqual(self.run_cli("transition", "example-epic", "T01", "--to", "IN_PROGRESS"), 0)
        (epic / "evidence").mkdir()
        (epic / "evidence" / "worker-1.md").write_text("Initial worker result.\n", encoding="utf-8")
        (epic / "evidence" / "review-fail.md").write_text("Review requires remediation.\n", encoding="utf-8")
        (epic / "evidence" / "security-pass.md").write_text("Security review passed.\n", encoding="utf-8")
        (epic / "evidence" / "worker-2.md").write_text("Remediation worker result.\n", encoding="utf-8")
        self.assertEqual(self.run_cli(
            "worker-record", "example-epic", "T01", "--commit", "abcdef1",
            "--evidence", "evidence/worker-1.md", "--required-review", "security-audit",
        ), 0)
        state_path = epic / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["tasks"]["T01"]["required_reviews"] = ["standards", "spec", "challenger", "security-audit"]
        state_path.write_text(json.dumps(state), encoding="utf-8")
        self.assertEqual(self.run_cli(
            "review-record", "example-epic", "T01", "--axis", "standards",
            "--verdict", "FAIL", "--evidence", "evidence/review-fail.md",
        ), 0)
        self.assertEqual(self.run_cli(
            "review-record", "example-epic", "T01", "--axis", "security",
            "--verdict", "PASS", "--evidence", "evidence/security-pass.md",
        ), 0)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["T01"]["reviews"]["security"]["verdict"], "PASS")
        self.assertNotIn("security-audit", state["tasks"]["T01"]["reviews"])
        self.assertEqual(self.run_cli("transition", "example-epic", "T01", "--to", "IN_REMEDIATION"), 0)
        self.assertEqual(self.run_cli(
            "worker-record", "example-epic", "T01", "--commit", "abcdef2",
            "--evidence", "evidence/worker-2.md",
        ), 0)
        state = json.loads((epic / "execution-state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["T01"]["status"], "IN_REVIEW")
        self.assertEqual(state["tasks"]["T01"]["worker_commit"], "abcdef2")
        self.assertIn("security", state["tasks"]["T01"]["required_reviews"])
        self.assertNotIn("security-audit", state["tasks"]["T01"]["required_reviews"])
        self.assertEqual(state["tasks"]["T01"]["reviews"], {})
        self.assertEqual(state["tasks"]["T01"]["remediation_count"], 1)

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

    def test_slugged_prerequisite_citations_still_validate(self) -> None:
        """Task cards may cite prerequisites as `T11-localvadport`.

        The slug is the semantic handle that makes a later renumber detectable
        at the citation site. The validator must extract the bare ID from the
        slugged form so the DAG set-equality check is unaffected.
        """
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        epic = self.root / "example-epic"
        (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
        first = VALID_TASK.replace(
            "- **Prerequisite Tasks:** None",
            "- **Prerequisite Tasks:** None",
        )
        second = VALID_TASK.replace(
            "T01: Core",
            "T02: Dependent",
        ).replace(
            "- **Task ID:** T01",
            "- **Task ID:** T02",
        ).replace(
            "- **Prerequisite Tasks:** None",
            "- **Prerequisite Tasks:** `T01-core`",
        )
        (epic / "tasks" / "T01-core.md").write_text(first, encoding="utf-8")
        (epic / "tasks" / "T02-dependent.md").write_text(second, encoding="utf-8")
        (epic / "dependency-dag.json").write_text(json.dumps({
            "epic": "example-epic",
            "tasks": [
                {"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []},
                {"id": "T02", "module": "M01", "kind": "implementation", "dependencies": ["T01"]},
            ],
        }), encoding="utf-8")
        self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
        self.assertEqual(self.run_cli("validate", "example-epic"), 0)

    def test_slugged_prerequisite_still_fails_on_dag_mismatch(self) -> None:
        """A slug must not mask a genuine dependency mismatch."""
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        epic = self.root / "example-epic"
        (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
        (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
        second = VALID_TASK.replace(
            "T01: Core",
            "T02: Dependent",
        ).replace(
            "- **Task ID:** T01",
            "- **Task ID:** T02",
        ).replace(
            "- **Prerequisite Tasks:** None",
            "- **Prerequisite Tasks:** `T01-core`",
        )
        (epic / "tasks" / "T02-dependent.md").write_text(second, encoding="utf-8")
        (epic / "dependency-dag.json").write_text(json.dumps({
            "epic": "example-epic",
            "tasks": [
                {"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []},
                {"id": "T02", "module": "M01", "kind": "implementation", "dependencies": []},
            ],
        }), encoding="utf-8")
        self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
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
            subprocess.run(["git", "add", ".deep-plan"], cwd=repository, check=True)
            subprocess.run(["git", "commit", "-m", "managed plan baseline"], cwd=repository, check=True, capture_output=True)
            # A tracked managed file produces a porcelain row whose first
            # status column is blank. Keep it modified while the dirty-tree
            # guard evaluates paths.
            state_path = epic / "execution-state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["test_marker"] = "modified"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            worker_artifact = repository / ".worktrees" / "prior-task" / "marker.txt"
            worker_artifact.parent.mkdir(parents=True)
            worker_artifact.write_text("managed worktree artifact\n", encoding="utf-8")
            self.assertFalse(deep_plan._has_unmanaged_changes(repository, epic))
            outside_file = repository / "outside.txt"
            outside_file.write_text("external\n", encoding="utf-8")
            subprocess.run(["git", "add", "outside.txt"], cwd=repository, check=True)
            subprocess.run(["git", "commit", "-m", "outside baseline"], cwd=repository, check=True, capture_output=True)
            outside_file.write_text("modified external\n", encoding="utf-8")
            self.assertTrue(deep_plan._has_unmanaged_changes(repository, epic))
            outside_file.write_text("external\n", encoding="utf-8")
            worktree_marker = repository / ".worktrees" / "tracked-marker.txt"
            worktree_marker.write_text("baseline\n", encoding="utf-8")
            subprocess.run(["git", "add", ".worktrees/tracked-marker.txt"], cwd=repository, check=True)
            subprocess.run(["git", "commit", "-m", "tracked worktree marker"], cwd=repository, check=True, capture_output=True)
            worktree_marker.write_text("modified\n", encoding="utf-8")
            self.assertTrue(deep_plan._has_unmanaged_changes(repository, epic))
            worktree_marker.write_text("baseline\n", encoding="utf-8")
            self.assertFalse(deep_plan._has_unmanaged_changes(repository, epic))
            self.assertEqual(self.run_cli("worktree-create", "example-epic", "T01", "--parent", "HEAD"), 0)
            self.assertTrue((repository / ".worktrees" / "T01-core").is_dir())
            self.assertIn("IN_PROGRESS", (epic / "progress-ledger.md").read_text(encoding="utf-8"))
        finally:
            os.chdir(original_cwd)
            self.root = original_root

    def test_worktrees_root_rejects_redirected_sibling(self) -> None:
        repository = Path(self.temp_dir.name) / "repo-worktree-redirect"
        repository.mkdir()
        redirected = Path(self.temp_dir.name) / "repo-worktree-redirect-escape"
        redirected.mkdir()
        try:
            (repository / ".worktrees").symlink_to(redirected, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"Directory symlinks are unavailable: {error}")

        with self.assertRaises(deep_plan.DeepPlanError):
            deep_plan._worktrees_root(repository)

    def test_unblock_requires_resolution_evidence_and_reopens_blocked_task(self) -> None:
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        epic = self.root / "example-epic"
        (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
        (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
        (epic / "dependency-dag.json").write_text(json.dumps({
            "epic": "example-epic",
            "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
        }), encoding="utf-8")
        self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
        self.assertEqual(self.run_cli("transition", "example-epic", "T01", "--to", "IN_PROGRESS"), 0)
        self.assertEqual(self.run_cli("transition", "example-epic", "T01", "--to", "BLOCKED"), 0)
        (epic / "evidence").mkdir(exist_ok=True)
        (epic / "evidence" / "blocker-resolved.md").write_text("Blocker resolved.\n", encoding="utf-8")

        self.assertEqual(self.run_cli(
            "unblock", "example-epic", "T01",
            "--reason", "The external dependency is now available.",
            "--evidence", "evidence/blocker-resolved.md",
        ), 0)
        state = json.loads((epic / "execution-state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["T01"]["status"], "READY_TO_DISPATCH")
        self.assertEqual(state["tasks"]["T01"]["unblock_evidence"], "evidence/blocker-resolved.md")
        self.assertEqual(state["events"][-1]["action"], "task-unblocked")

    def test_unblock_rejects_failed_review(self) -> None:
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        epic = self.root / "example-epic"
        (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
        (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
        (epic / "dependency-dag.json").write_text(json.dumps({
            "epic": "example-epic",
            "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
        }), encoding="utf-8")
        self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
        state_path = epic / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["tasks"]["T01"].update({
            "status": "BLOCKED",
            "remediation_count": 0,
            "reviews": {"standards": {"verdict": "FAIL", "evidence": "evidence/review.md"}},
        })
        state_path.write_text(json.dumps(state), encoding="utf-8")
        (epic / "evidence").mkdir(exist_ok=True)
        (epic / "evidence" / "plan-revision.md").write_text("Plan revision required.\n", encoding="utf-8")

        self.assertEqual(self.run_cli(
            "unblock", "example-epic", "T01",
            "--reason", "Attempt to reopen exhausted task.",
            "--evidence", "evidence/plan-revision.md",
        ), 2)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["T01"]["status"], "BLOCKED")

    def test_unblock_allows_integrated_task_to_resume_after_environment_blocker(self) -> None:
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        epic = self.root / "example-epic"
        (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
        (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
        (epic / "dependency-dag.json").write_text(json.dumps({
            "epic": "example-epic",
            "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
        }), encoding="utf-8")
        self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
        state_path = epic / "execution-state.json"
        (epic / "evidence").mkdir(exist_ok=True)
        for axis in ("standards", "spec", "challenger"):
            (epic / "evidence" / f"{axis}.md").write_text("PASS\n", encoding="utf-8")
        state = json.loads(state_path.read_text(encoding="utf-8"))
        task = state["tasks"]["T01"]
        task.update({
            "status": "BLOCKED",
            "remediation_count": 1,
            "required_reviews": ["standards", "spec", "challenger"],
            "reviews": {
                "standards": {"verdict": "PASS", "evidence": "evidence/standards.md"},
                "spec": {"verdict": "PASS", "evidence": "evidence/spec.md"},
                "challenger": {"verdict": "PASS", "evidence": "evidence/challenger.md"},
            },
            "worker_commit": "0123456789abcdef",
            "integrated_commit": "fedcba9876543210",
            "worktree": ".worktrees/T01-core",
            "branch": "task/T01-core",
        })
        state_path.write_text(json.dumps(state), encoding="utf-8")
        (epic / "evidence" / "runtime-resolved.md").write_text("Runtime blocker resolved.\n", encoding="utf-8")

        self.assertEqual(self.run_cli(
            "unblock", "example-epic", "T01",
            "--reason", "The integrated verification environment is available again.",
            "--evidence", "evidence/runtime-resolved.md",
        ), 0)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["T01"]["status"], "READY_TO_DISPATCH")

    def test_unblock_rejects_exhausted_remediation_limit(self) -> None:
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        epic = self.root / "example-epic"
        (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
        (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
        (epic / "dependency-dag.json").write_text(json.dumps({
            "epic": "example-epic",
            "tasks": [{"id": "T01", "module": "M01", "kind": "implementation", "dependencies": []}],
        }), encoding="utf-8")
        self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
        state_path = epic / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["tasks"]["T01"].update({"status": "BLOCKED", "remediation_count": deep_plan.DEFAULT_REMEDIATION_LIMIT})
        state_path.write_text(json.dumps(state), encoding="utf-8")
        (epic / "evidence").mkdir(exist_ok=True)
        (epic / "evidence" / "plan-revision.md").write_text("Plan revision required.\n", encoding="utf-8")

        self.assertEqual(self.run_cli(
            "unblock", "example-epic", "T01",
            "--reason", "Attempt to reopen exhausted task.",
            "--evidence", "evidence/plan-revision.md",
        ), 2)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["T01"]["status"], "BLOCKED")

    def test_unblock_rejects_incomplete_dependencies(self) -> None:
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        epic = self.root / "example-epic"
        (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
        (epic / "tasks" / "T00-prerequisite.md").write_text(VALID_TASK.replace("T01", "T00"), encoding="utf-8")
        (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
        (epic / "dependency-dag.json").write_text(json.dumps({
            "epic": "example-epic",
            "tasks": [
                {"id": "T00", "module": "M01", "kind": "implementation", "dependencies": []},
                {"id": "T01", "module": "M01", "kind": "implementation", "dependencies": ["T00"]},
            ],
        }), encoding="utf-8")
        self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
        (epic / "evidence").mkdir(exist_ok=True)
        (epic / "evidence" / "blocker-resolution.md").write_text("External blocker resolved.\n", encoding="utf-8")

        self.assertEqual(self.run_cli(
            "unblock", "example-epic", "T01",
            "--reason", "Attempt to reopen before dependency completion.",
            "--evidence", "evidence/blocker-resolution.md",
        ), 2)
        state = json.loads((epic / "execution-state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["T01"]["status"], "BLOCKED")

    def test_unblock_rejects_dag_changed_without_state_sync(self) -> None:
        self.assertEqual(self.run_cli("init", "example-epic"), 0)
        epic = self.root / "example-epic"
        (epic / "modules" / "M01-core.md").write_text("# Module\n", encoding="utf-8")
        (epic / "tasks" / "T00-prerequisite.md").write_text(VALID_TASK.replace("T01", "T00"), encoding="utf-8")
        (epic / "tasks" / "T01-core.md").write_text(VALID_TASK, encoding="utf-8")
        dag_path = epic / "dependency-dag.json"
        dag_path.write_text(json.dumps({
            "epic": "example-epic",
            "tasks": [
                {"id": "T00", "module": "M01", "kind": "implementation", "dependencies": []},
                {"id": "T01", "module": "M01", "kind": "implementation", "dependencies": ["T00"]},
            ],
        }), encoding="utf-8")
        self.assertEqual(self.run_cli("sync-ledger", "example-epic"), 0)
        state_path = epic / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["tasks"]["T01"]["status"] = "BLOCKED"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        dag = json.loads(dag_path.read_text(encoding="utf-8"))
        dag["tasks"][1]["dependencies"] = []
        dag_path.write_text(json.dumps(dag), encoding="utf-8")
        (epic / "evidence").mkdir(exist_ok=True)
        (epic / "evidence" / "blocker-resolution.md").write_text("External blocker resolved.\n", encoding="utf-8")

        self.assertEqual(self.run_cli(
            "unblock", "example-epic", "T01",
            "--reason", "Attempt to bypass stale prerequisite state.",
            "--evidence", "evidence/blocker-resolution.md",
        ), 2)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["T01"]["status"], "BLOCKED")
        dag["tasks"][1]["dependencies"] = ["T00"]
        dag["tasks"][1]["kind"] = "documentation"
        dag_path.write_text(json.dumps(dag), encoding="utf-8")
        self.assertEqual(self.run_cli("ready", "example-epic"), 2)

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
