import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add script directory to sys.path so we can import helper functions directly
SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.append(str(SCRIPT_DIR))

import tree_of_work

def classify_trigger(prompt: str) -> bool:
    """Simple keyword/pattern-based trigger classifier for Tree of Work skill."""
    p = prompt.lower()
    trigger_words = [
        "where was i", "crashed", "break down", "manageable tasks", 
        "track progress", "delegate", "sub-agent", "losing context", 
        "persist task state", "organize this work", "track which ones are done",
        "switching focus", "don't lose track", "lose track", "roadmap", "todo"
    ]
    if any(tw in p for tw in trigger_words):
        return True
    if "organize" in p or "track" in p:
        return True
    return False

class TestTreeOfWorkEvals(unittest.TestCase):
    def setUp(self):
        self.original_cwd = Path.cwd()
        # Create a temp directory for isolated testing
        self.test_dir = Path(tempfile.mkdtemp(prefix="tow_test_"))
        os.chdir(self.test_dir)
        self.state_dir = self.test_dir / ".agent/tree-of-work"

    def tearDown(self):
        os.chdir(self.original_cwd)
        # Clean up the temp directory
        try:
            shutil.rmtree(self.test_dir)
        except Exception:
            pass

    def test_evals_json_triggers(self):
        """Verify that all prompts in evals.json trigger/don't trigger as expected."""
        evals_path = Path(__file__).resolve().parent / "evals.json"
        with open(evals_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print("\n--- Running Trigger Classification Evals ---")
        passed = 0
        total = len(data["evals"])
        for case in data["evals"]:
            actual = classify_trigger(case["prompt"])
            expected = case["should_trigger"]
            status = "PASS" if actual == expected else "FAIL"
            print(f"Case {case['id']}: [{status}] Prompt: \"{case['prompt'][:50]}...\" | Expected: {expected}, Actual: {actual}")
            self.assertEqual(actual, expected, f"Failed trigger classification on case {case['id']}")
            passed += 1
        print(f"Trigger Classification Evals: {passed}/{total} passed.")

    def test_cli_init_default(self):
        """Verify cmd_init creates correct state from default template when no legacy files exist."""
        tree_of_work.cmd_init(self.state_dir)
        state_file = self.state_dir / "current-state.md"
        self.assertTrue(state_file.exists())
        content = state_file.read_text(encoding="utf-8")
        self.assertIn("**Task:** [TASK-01] Initial Setup", content)
        self.assertIn("**Status:** ACTIVE", content)

    def test_cli_init_with_legacy_files(self):
        """Verify cmd_init absorbs legacy files (onboarding state penyerapan otomatis)."""
        # Create mock legacy files
        (self.test_dir / "ROADMAP.md").write_text(
            "# Roadmap\n\n- Implement billing module [IN_PROGRESS]\n- Add oauth support [TODO]\n", 
            encoding="utf-8"
        )
        (self.test_dir / "TODO.md").write_text(
            "# Todos\n\n- [ ] Clean up temp logs\n- [ ] Write integration tests\n", 
            encoding="utf-8"
        )

        tree_of_work.cmd_init(self.state_dir)
        state_file = self.state_dir / "current-state.md"
        self.assertTrue(state_file.exists())
        content = state_file.read_text(encoding="utf-8")

        # The active status should prioritize ROADMAP.md's active tasks
        self.assertIn("**Task:** [TASK-01] [from: ROADMAP.md] Implement billing module", content)
        # Other items should go to parked list
        self.assertIn("**Task:** [TASK-02] [from: CLAUDE.md] Complete implementation of the orchestrator deconstruction", content)
        self.assertIn("**Task:** [TASK-03] [from: CLAUDE.md] Fix TTS race condition", content)
        self.assertIn("**Task:** [TASK-04] [from: TODO.md] Clean up temp logs", content)
        self.assertIn("**Task:** [TASK-05] [from: TODO.md] Write integration tests", content)

    def test_cli_validate(self):
        """Verify cmd_validate correctly evaluates state file validity."""
        # 1. Valid state
        tree_of_work.cmd_init(self.state_dir)
        self.assertTrue(tree_of_work.cmd_validate(self.state_dir))

        # 2. Invalid state: multiple active tasks
        state_file = self.state_dir / "current-state.md"
        content = state_file.read_text(encoding="utf-8")
        corrupted = content.replace("## PARKED / BLOCKED", "## PARKED / BLOCKED\n- **Status:** ACTIVE")
        state_file.write_text(corrupted, encoding="utf-8")
        self.assertFalse(tree_of_work.cmd_validate(self.state_dir))

    def test_cli_validate_parent_id(self):
        """Verify cmd_validate fails if a branch references an undefined parent task ID."""
        tree_of_work.cmd_init(self.state_dir)
        state_file = self.state_dir / "current-state.md"
        content = state_file.read_text(encoding="utf-8")
        
        # Add a branch referencing an undefined task ID
        corrupted = content.replace(
            "## BRANCHES\n\n(None)", 
            "## BRANCHES\n\n- **Issue:** Mock bug\n  - **Parent Task:** [TASK-99]\n  - **Priority:** High\n  - **Status:** ACTIVE"
        )
        state_file.write_text(corrupted, encoding="utf-8")
        self.assertFalse(tree_of_work.cmd_validate(self.state_dir))

        # Change branch to reference the valid task ID [TASK-01] and it should pass validation
        valid_branch = content.replace(
            "## BRANCHES\n\n(None)", 
            "## BRANCHES\n\n- **Issue:** Mock bug\n  - **Parent Task:** [TASK-01]\n  - **Priority:** High\n  - **Status:** ACTIVE"
        )
        state_file.write_text(valid_branch, encoding="utf-8")
        self.assertTrue(tree_of_work.cmd_validate(self.state_dir))

    def test_cli_entropy_validation(self):
        """Verify shannon entropy and secret patterns are rejected during validation."""
        tree_of_work.cmd_init(self.state_dir)
        state_file = self.state_dir / "current-state.md"
        
        # Add high-entropy random string representing API key
        corrupted = state_file.read_text(encoding="utf-8") + "\nAPI_KEY = \"xK8pQ2wR9zT4yU1vI7oB5eA3sD6fG9hJ12345\""
        state_file.write_text(corrupted, encoding="utf-8")
        self.assertFalse(tree_of_work.cmd_validate(self.state_dir))


if __name__ == "__main__":
    unittest.main()
