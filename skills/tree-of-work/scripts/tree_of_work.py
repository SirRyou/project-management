#!/usr/bin/env python3
"""Tree of Work CLI — hierarchical task tracking with context recovery."""

import argparse
import json
import math
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SECRET_PATTERNS = [
    r"(?i)ghp_[a-zA-Z0-9]{36}",                      # GitHub PAT
    r"(?i)sk_live_[a-zA-Z0-9]{24,}",                  # Stripe Live Key
    r"(?i)eyJhbGciOi[a-zA-Z0-9=_\-\.]+",             # JWT Token
    r"(?i)amzn\.mws\.[a-f0-9]{8}-[a-f0-9]{4}-.*",    # Amazon MWS
    r"(?i)AIza[yI][-_a-zA-Z0-9]{35}",                 # Google API Key
    r"(?i)aws_access_key_id\s*=\s*[A-Z0-9]{20}",      # AWS Access Key
    r"(?i)aws_secret_access_key\s*=\s*[a-zA-Z0-9/+=]{40}",  # AWS Secret
]

DEFAULT_STATE_TEMPLATE = """\
# Agent State Snapshot

## NOW

- **Task:** [TASK-01] Initial Setup
- **Status:** ACTIVE
- **Primary Files:** None
- **Latest Progress:** Started work on the project.
- **Next Concrete Step:** Define tasks and begin implementation.

## PARKED / BLOCKED

(None)

## BRANCHES

(None)

## VALIDATION

- Unit Tests: NOT RUN
- Lint: NOT RUN
- Build: NOT RUN
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def resolve_state_dir() -> Path:
    """Resolve state directory: env var or default."""
    env_path = os.getenv("TREE_OF_WORK_DIR")
    if env_path:
        return Path(env_path)
    return Path(".agent/tree-of-work")


def _read_state(state_dir: Path) -> str:
    """Read current-state.md, exit if missing."""
    path = state_dir / "current-state.md"
    if not path.exists():
        print(
            f"Error: State file not found at {path}. Run 'init' first.",
            file=sys.stderr,
        )
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def _write_state(state_dir: Path, content: str) -> None:
    """Write content to current-state.md."""
    path = state_dir / "current-state.md"
    path.write_text(content, encoding="utf-8")


def calculate_shannon_entropy(data: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not data:
        return 0.0
    length = len(data)
    char_counts: dict[str, int] = {}
    for char in data:
        char_counts[char] = char_counts.get(char, 0) + 1
    entropy = 0.0
    for count in char_counts.values():
        p_x = count / length
        entropy -= p_x * math.log(p_x, 2)
    return entropy


def sanitize_and_check_content(content: str) -> str:
    """Auto-redact known secret patterns, block high-entropy strings."""
    # Tier 1: Auto-redact known patterns
    for pattern in SECRET_PATTERNS:
        content = re.sub(pattern, "<REDACTED_SECRET>", content)

    # Tier 2: Shannon entropy check per word
    lines = content.splitlines()
    for idx, line in enumerate(lines, 1):
        words = re.split(r"[\s\'\"\[\]\(\)=\{\},;]+", line)
        for word in words:
            word = word.strip(".:!?-")
            if len(word) <= 32:
                continue
            if "/" in word or "\\" in word or "://" in word:
                continue
            if re.match(r"^[a-fA-F0-9]+$", word):
                continue
            if word.startswith(("data:image/", "data:application/")):
                continue
            entropy = calculate_shannon_entropy(word)
            if entropy > 4.5:
                redacted = f"{word[:6]}..."
                raise ValueError(
                    f"Security Alert: High-entropy string '{redacted}' on line {idx}. "
                    f"Entropy: {entropy:.2f}, Length: {len(word)}. "
                    f"Sanitize before proceeding."
                )
    return content


def _count_active_tasks(content: str) -> int:
    """Count occurrences of Status: ACTIVE in the file (excluding BRANCHES)."""
    content_no_branches = re.sub(r"## BRANCHES\s*\n.*?(?=\n##|$)", "", content, flags=re.DOTALL)
    return len(re.findall(r"-\s+\*\*Status:\*\*\s+ACTIVE", content_no_branches))


def _absorb_legacy_state() -> str:
    """Scan root directory for legacy state files and git history to generate a tailored state file."""
    project_root = Path.cwd()
    import subprocess

    # 1. Get git info
    last_commit_msg = None
    git_branch = None
    try:
        # Get last commit message
        commit_res = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True,
            check=False
        )
        if commit_res.returncode == 0:
            last_commit_msg = commit_res.stdout.strip()
        
        # Get current branch
        branch_res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=False
        )
        if branch_res.returncode == 0:
            git_branch = branch_res.stdout.strip()
    except Exception:
        pass

    # 2. Scan legacy files
    roadmap_items = []
    claude_items = []
    todo_items = []

    # TODO.md / todo.txt
    for fname in ["TODO.md", "todo.txt"]:
        fpath = project_root / fname
        if fpath.exists():
            try:
                content = fpath.read_text(encoding="utf-8")
                for line in content.splitlines():
                    line = line.strip()
                    # Match "- [ ] task" or "* [ ] task" or "TODO: task"
                    todo_match = re.match(r"^[-\*]\s*\[\s*\]\s*(.+)$", line)
                    if todo_match:
                        todo_items.append((fname, todo_match.group(1).strip()))
                        continue
                    todo_colon_match = re.match(r"^TODO:\s*(.+)$", line, re.IGNORECASE)
                    if todo_colon_match:
                        todo_items.append((fname, todo_colon_match.group(1).strip()))
            except Exception:
                pass

    # CLAUDE.md
    claude_path = project_root / "CLAUDE.md"
    if claude_path.exists():
        try:
            content = claude_path.read_text(encoding="utf-8")
            # Find ## Current Focus or ## Next Steps
            sections = re.findall(
                r"##\s*(?:Current Focus|Next Steps)\s*\n(.*?)(?=\n##|\Z)",
                content,
                re.DOTALL | re.IGNORECASE
            )
            for sec in sections:
                for line in sec.splitlines():
                    line = line.strip()
                    # Clean up list items: "- task", "* task", "1. task" or "- [ ] task"
                    item_match = re.match(r"^(?:[-\*]\s*(?:\[\s*\])?|\d+\.)\s*(.+)$", line)
                    if item_match:
                        claude_items.append(("CLAUDE.md", item_match.group(1).strip()))
        except Exception:
            pass

    # ROADMAP.md / STATUS.md
    for fname in ["ROADMAP.md", "STATUS.md"]:
        fpath = project_root / fname
        if fpath.exists():
            try:
                content = fpath.read_text(encoding="utf-8")
                for line in content.splitlines():
                    line = line.strip()
                    # Lines containing IN_PROGRESS, ACTIVE, In Progress
                    if any(kw in line for kw in ["IN_PROGRESS", "ACTIVE", "In Progress"]):
                        # Try to extract the task name, remove status keywords and markdown list syntax
                        # e.g., "- Implement billing [IN_PROGRESS]" -> "Implement billing"
                        cleaned = line
                        # Remove markdown list markers
                        cleaned = re.sub(r"^(?:[-\*]\s*(?:\[.\])?|\d+\.)\s*", "", cleaned)
                        # Remove status keywords (brackets/parentheses optionally around them)
                        cleaned = re.sub(r"\[?\b(?:IN_PROGRESS|ACTIVE|In Progress)\b\]?", "", cleaned, flags=re.IGNORECASE)
                        cleaned = cleaned.strip(" -:*[]()")
                        if cleaned:
                            roadmap_items.append((fname, cleaned))
            except Exception:
                pass

    # 3. Determine ACTIVE task and PARKED tasks
    active_task = None
    active_source = None
    parked_list = []

    task_id_counter = 1

    # Prioritize active tasks from ROADMAP.md / STATUS.md, then CLAUDE.md
    all_active_candidates = []
    all_active_candidates.extend(roadmap_items)
    all_active_candidates.extend(claude_items)

    if all_active_candidates:
        active_source, active_task_name = all_active_candidates[0]
        prefix = f"[from: {active_source}] " if active_source not in ["Default", "Git Branch"] else ""
        active_task = f"[TASK-{task_id_counter:02d}] {prefix}{active_task_name}"
        task_id_counter += 1
        
        for src, task in all_active_candidates[1:]:
            parked_list.append(f"[TASK-{task_id_counter:02d}] [from: {src}] {task}")
            task_id_counter += 1

    # All legacy todos go to parked list
    for src, task in todo_items:
        parked_list.append(f"[TASK-{task_id_counter:02d}] [from: {src}] {task}")
        task_id_counter += 1

    # If still no active task, use branch name
    if not active_task:
        if git_branch and git_branch not in ["master", "main", "HEAD", "head"]:
            active_task = f"[TASK-{task_id_counter:02d}] Working on branch: {git_branch}"
            active_source = "Git Branch"
        else:
            active_task = f"[TASK-{task_id_counter:02d}] Initial Setup"
            active_source = "Default"
        task_id_counter += 1

    # Format output
    latest_progress = "Started work on the project."
    if last_commit_msg:
        # Limit commit message to single line for formatting
        first_line_commit = last_commit_msg.splitlines()[0] if last_commit_msg else ""
        latest_progress = f"Started work (last git commit: \"{first_line_commit}\")."

    next_step = "Define tasks and begin implementation."
    # Extract task name without [TASK-XX] prefix for next step
    clean_active_name = active_task
    m = re.match(r"^\[[A-Za-z0-9_-]+\]\s*(.+)$", active_task)
    if m:
        clean_active_name = m.group(1)
    if clean_active_name != "Initial Setup":
        next_step = f"Complete implementation of {clean_active_name}."

    state_md = f"""# Agent State Snapshot

## NOW

- **Task:** {active_task}
- **Status:** ACTIVE
- **Primary Files:** None
- **Latest Progress:** {latest_progress}
- **Next Concrete Step:** {next_step}

## PARKED / BLOCKED

"""
    if parked_list:
        for task in parked_list:
            state_md += f"""- **Task:** {task}
  - **Status:** PARKED
  - **Reason:** Legacy item imported during onboarding
  - **Resume Condition:** Select as active focus
"""
    else:
        state_md += "(None)\n"

    state_md += """
## BRANCHES

(None)

## VALIDATION

- Unit Tests: NOT RUN
- Lint: NOT RUN
- Build: NOT RUN
"""
    return state_md


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_init(state_dir: Path) -> None:
    """Initialize state directory, create files, update .gitignore."""
    state_dir.mkdir(parents=True, exist_ok=True)
    history_dir = state_dir / "history"
    subagents_dir = state_dir / "subagents"
    history_dir.mkdir(exist_ok=True)
    subagents_dir.mkdir(exist_ok=True)

    current_state = state_dir / "current-state.md"
    if not current_state.exists():
        # Check if legacy files exist
        project_root = Path.cwd()
        legacy_files = ["TODO.md", "todo.txt", "CLAUDE.md", "ROADMAP.md", "STATUS.md"]
        has_legacy = any((project_root / f).exists() for f in legacy_files)
        
        if has_legacy:
            print("Legacy state files detected. Scanning and absorbing task context...")
            absorbed_state = _absorb_legacy_state()
            _write_state(state_dir, absorbed_state)
            print(f"Initialized with absorbed state: {current_state}")
        else:
            _write_state(state_dir, DEFAULT_STATE_TEMPLATE)
            print(f"Initialized: {current_state}")
    else:
        print(f"Already exists: {current_state}")

    # Update .gitignore
    project_root = Path.cwd()
    gitignore = project_root / ".gitignore"
    try:
        rel = state_dir.relative_to(project_root)
    except ValueError:
        rel = state_dir

    entries = [
        f"{rel.as_posix()}/history/",
        f"{rel.as_posix()}/subagents/",
    ]

    existing = ""
    if gitignore.exists():
        existing = gitignore.read_text(encoding="utf-8")

    to_add = [e for e in entries if e not in existing]
    if to_add:
        with open(gitignore, "a", encoding="utf-8") as f:
            if existing and not existing.endswith("\n"):
                f.write("\n")
            for entry in to_add:
                f.write(f"{entry}\n")
        print(f"Updated {gitignore}")

    print("Tree of Work initialized.")


def cmd_validate(state_dir: Path) -> bool:
    """Validate state file structure and security. Returns True if valid."""
    content = _read_state(state_dir)

    # Security check
    try:
        sanitize_and_check_content(content)
    except ValueError as e:
        print(f"FAIL (Security): {e}", file=sys.stderr)
        return False

    # NOW section exists
    if "## NOW" not in content:
        print("FAIL: Missing '## NOW' section.", file=sys.stderr)
        return False

    # Exactly one ACTIVE task
    active_count = _count_active_tasks(content)
    if active_count > 1:
        print(
            f"FAIL: {active_count} ACTIVE tasks found. Max 1 allowed.",
            file=sys.stderr,
        )
        return False
    if active_count == 0:
        print(
            "WARN: 0 ACTIVE tasks. OK if all work is complete.",
            file=sys.stderr,
        )

    # Extract all task IDs in NOW and PARKED / BLOCKED sections and enforce ID prefix
    task_ids = set()
    task_lines = re.findall(r"-\s+\*\*Task:\*\*\s*(.*)", content)
    for line in task_lines:
        line_stripped = line.strip()
        if not line_stripped or line_stripped == "(None)":
            continue
        # Verify it has a bracketed ID at the start (e.g. [TASK-01])
        m = re.search(r"^\[([A-Za-z0-9_-]+)\]", line_stripped)
        if not m:
            print(
                f"FAIL: Task '{line_stripped}' is missing a bracketed ID prefix (e.g. [TASK-01] or [BUG-02]).",
                file=sys.stderr,
            )
            return False
        task_ids.add(m.group(1))

    # Branches must have Parent Task
    branches_match = re.search(
        r"## BRANCHES\s*\n(.*?)(?=\n##|$)", content, re.DOTALL
    )
    if branches_match:
        items = re.findall(
            r"-\s+\*\*Issue:\*\*.*?(?=-\s+\*\*Issue:\*\*|$)",
            branches_match.group(1),
            re.DOTALL,
        )
        for item in items:
            if "Parent Task" not in item:
                print(
                    "FAIL: Branch missing '**Parent Task:**' reference.",
                    file=sys.stderr,
                )
                return False
            
            # Verify Parent Task reference points to a valid ID
            parent_match = re.search(r"\*\*Parent Task:\*\*\s*(.+)", item)
            if parent_match:
                parent_val = parent_match.group(1).strip()
                # Extract the bracketed ID from parent reference if present
                m = re.search(r"\[([A-Za-z0-9_-]+)\]", parent_val)
                ref_id = m.group(1) if m else parent_val
                
                # If there are defined IDs in the file, enforce that the reference matches one of them
                if task_ids and ref_id not in task_ids:
                    print(
                        f"FAIL: Branch references undefined Parent Task ID '{ref_id}'.",
                        file=sys.stderr,
                    )
                    return False

    print("VALID")
    return True


def cmd_snapshot(state_dir: Path, message: str | None = None) -> None:
    """Create a sanitized timestamped snapshot in history/."""
    content = _read_state(state_dir)

    try:
        sanitized = sanitize_and_check_content(content)
    except ValueError as e:
        print(f"BLOCKED: potential credentials leak.\n{e}", file=sys.stderr)
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_msg = ""
    if message:
        safe_msg = "_" + re.sub(r"[^a-zA-Z0-9_-]", "_", message)[:30]

    history_dir = state_dir / "history"
    history_dir.mkdir(exist_ok=True)

    snapshot_file = history_dir / f"snapshot_{timestamp}{safe_msg}.md"
    snapshot_file.write_text(sanitized, encoding="utf-8")
    print(f"Snapshot: {snapshot_file}")


def cmd_status(state_dir: Path, as_json: bool = False) -> None:
    """Print current state summary."""
    content = _read_state(state_dir)

    now_match = re.search(
        r"## NOW\s*\n(.*?)(?=\n##|$)", content, re.DOTALL
    )
    parked_match = re.search(
        r"## PARKED / BLOCKED\s*\n(.*?)(?=\n##|$)", content, re.DOTALL
    )
    branches_match = re.search(
        r"## BRANCHES\s*\n(.*?)(?=\n##|$)", content, re.DOTALL
    )

    now_text = now_match.group(1).strip() if now_match else "(None)"
    parked_text = parked_match.group(1).strip() if parked_match else "(None)"
    branches_text = branches_match.group(1).strip() if branches_match else "(None)"

    if as_json:
        result = {
            "active_task": now_text,
            "parked_blocked": parked_text,
            "branches": branches_text,
            "active_count": _count_active_tasks(content),
        }
        print(json.dumps(result, indent=2))
    else:
        print("=" * 60)
        print("                 TREE OF WORK STATUS")
        print("=" * 60)
        print("\n[ACTIVE FOCUS]")
        print(now_text)
        print("\n[PARKED / BLOCKED]")
        print(parked_text)
        print("\n[LOGICAL BRANCHES]")
        print(branches_text)
        print("=" * 60)


def cmd_reset(state_dir: Path) -> None:
    """Reset state to default template."""
    _write_state(state_dir, DEFAULT_STATE_TEMPLATE)
    print("State reset to default template.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tree of Work — hierarchical task tracking"
    )
    parser.add_argument("--state-dir", type=str, help="Override state directory")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Initialize state directory and files")
    sub.add_parser("validate", help="Validate state file integrity and security")

    snap = sub.add_parser("snapshot", help="Create timestamped snapshot")
    snap.add_argument("-m", "--message", type=str, help="Snapshot label")

    status_p = sub.add_parser("status", help="Print current state summary")
    status_p.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    sub.add_parser("reset", help="Reset state to default template")

    args = parser.parse_args()

    # Resolve state directory
    state_dir = Path(args.state_dir) if args.state_dir else resolve_state_dir()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "init":
        cmd_init(state_dir)
    elif args.command == "validate":
        ok = cmd_validate(state_dir)
        sys.exit(0 if ok else 1)
    elif args.command == "snapshot":
        cmd_snapshot(state_dir, args.message)
    elif args.command == "status":
        cmd_status(state_dir, as_json=args.json)
    elif args.command == "reset":
        cmd_reset(state_dir)


if __name__ == "__main__":
    main()
