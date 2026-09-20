#!/usr/bin/env python3
"""Deterministic workspace and plan checks for the Deep Plan skill.

This tool validates structure and workflow state. It deliberately does not run
task-defined verification commands, dispatch subagents, or merge worker work.
Those operations require PM judgement and explicit authorization.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "templates"
TASK_ID_RE = re.compile(r"^T[0-9]{2,}$")
MODULE_ID_RE = re.compile(r"^M[0-9]{2,}$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
TASK_FILE_RE = re.compile(r"^(T[0-9]{2,})-[a-z0-9][a-z0-9-]*\.md$")
ALLOWED_KINDS = {
    "implementation",
    "migration",
    "research",
    "documentation",
    "benchmark",
    "configuration",
}
ALLOWED_VERIFICATION_MODES = {
    "behavioral-tdd",
    "migration",
    "static-config",
    "documentation",
    "benchmark",
    "repository-specific",
}
ALLOWED_STATUSES = {
    "READY_TO_DISPATCH",
    "IN_PROGRESS",
    "IN_REVIEW",
    "IN_REMEDIATION",
    "INTEGRATING",
    "VERIFIED",
    "COMPLETED",
    "BLOCKED",
    "FAILED",
    "CANCELLED",
}
PAUSE_REASONS = ("quota", "tired", "eod", "blocker", "other")
REQUIRED_ARTIFACTS = (
    "00-intent.md",
    "01-grounding.md",
    "02-risk-register.md",
    "03-tier1-epic.md",
    "dependency-dag.json",
    "progress-ledger.md",
    "execution-state.json",
)
REQUIRED_TASK_FIELDS = (
    "Task ID",
    "Parent Module",
    "Intent Trace",
    "Invariant Trace",
    "Risk Trace",
    "Kind",
    "Verification Mode",
    "Prerequisite Tasks",
    "Target Files and Symbols",
    "Completion Criterion",
)


class DeepPlanError(ValueError):
    """A user-correctable plan or repository state error."""


@dataclass
class LedgerRow:
    task_id: str
    module: str
    dependencies: str
    worktree: str = "—"
    worker_commit: str = "—"
    integrated_commit: str = "—"
    verification: str = "—"
    code_auditor: str = "—"
    challenger: str = "—"
    status: str = "BLOCKED"
    remediation_count: str = "0"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _state_path(epic_dir: Path) -> Path:
    return epic_dir / "execution-state.json"


def _new_state(epic: str) -> dict:
    return {
        "schema_version": 1,
        "epic": epic,
        "state_revision": 0,
        "updated_at": _now(),
        "tasks": {},
        "events": [],
    }


def _atomic_write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _load_state(epic_dir: Path, expected_epic: str) -> tuple[dict, list[str]]:
    try:
        state = json.loads(_state_path(epic_dir).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {}, [f"Invalid execution-state.json: {error}"]
    errors: list[str] = []
    if not isinstance(state, dict):
        return {}, ["execution-state.json must contain an object."]
    if state.get("schema_version") != 1:
        errors.append("execution-state.json schema_version must be 1.")
    if state.get("epic") != expected_epic:
        errors.append(f"Execution state epic must equal '{expected_epic}'.")
    if not isinstance(state.get("state_revision"), int) or state["state_revision"] < 0:
        errors.append("Execution state state_revision must be a non-negative integer.")
    tasks = state.get("tasks")
    if not isinstance(tasks, dict):
        errors.append("Execution state tasks must be an object keyed by task ID.")
        return state, errors
    for task_id, task in tasks.items():
        if not TASK_ID_RE.fullmatch(task_id) or not isinstance(task, dict):
            errors.append(f"Execution state has invalid task entry {task_id!r}.")
            continue
        if task.get("status") not in ALLOWED_STATUSES:
            errors.append(f"Execution state {task_id} has invalid status {task.get('status')!r}.")
        if not isinstance(task.get("dependencies"), list):
            errors.append(f"Execution state {task_id} dependencies must be an array.")
        step_progress = task.get("step_progress")
        if step_progress is not None and not isinstance(step_progress, dict):
            errors.append(f"Execution state {task_id} step_progress must be an object.")
        required_reviews = task.get("required_reviews", [])
        reviews = task.get("reviews", {})
        if not isinstance(required_reviews, list) or not all(isinstance(item, str) for item in required_reviews):
            errors.append(f"Execution state {task_id} required_reviews must be an array of names.")
        if not isinstance(reviews, dict):
            errors.append(f"Execution state {task_id} reviews must be an object.")
        else:
            for axis, review in reviews.items():
                if not isinstance(review, dict) or review.get("verdict") not in {"PASS", "FAIL"}:
                    errors.append(f"Execution state {task_id} review {axis} must have PASS or FAIL verdict.")
                elif not isinstance(review.get("evidence"), str) or not review["evidence"].strip():
                    errors.append(f"Execution state {task_id} review {axis} requires evidence.")
    pause_state = state.get("pause_state")
    if pause_state is not None and not isinstance(pause_state, dict):
        errors.append("Execution state pause_state must be an object or null.")
    if not isinstance(state.get("events"), list):
        errors.append("Execution state events must be an array.")
    return state, errors


def _record_event(state: dict, action: str, task_id: str | None = None, details: dict | None = None) -> None:
    event = {"action": action, "actor": "pm-orchestrator", "timestamp": _now()}
    if task_id:
        event["task_id"] = task_id
    if details:
        event["details"] = details
    state.setdefault("events", []).append(event)
    state["state_revision"] += 1
    state["updated_at"] = event["timestamp"]


def _save_state(state: dict, epic_dir: Path) -> None:
    _atomic_write_json(_state_path(epic_dir), state)


def _state_rows(state: dict) -> dict[str, LedgerRow]:
    rows: dict[str, LedgerRow] = {}
    for task_id, task in state.get("tasks", {}).items():
        reviews = task.get("reviews", {})
        standards = reviews.get("standards", {}).get("verdict")
        spec = reviews.get("spec", {}).get("verdict")
        rows[task_id] = LedgerRow(
            task_id=task_id,
            module=task.get("module", ""),
            dependencies=", ".join(task.get("dependencies", [])) or "None",
            worktree=task.get("worktree") or "—",
            worker_commit=task.get("worker_commit") or "—",
            integrated_commit=task.get("integrated_commit") or "—",
            verification=task.get("verification") or "—",
            code_auditor="PASS" if standards == "PASS" and spec == "PASS" else ("FAIL" if "FAIL" in {standards, spec} else "—"),
            challenger=reviews.get("challenger", {}).get("verdict", "—"),
            status=task.get("status", "BLOCKED"),
            remediation_count=str(task.get("remediation_count", 0)),
        )
    return rows


def _sync_ledger_projection(epic_dir: Path, state: dict, dag: dict) -> None:
    _render_ledger(epic_dir, _state_rows(state), dag["tasks"])


def _clean_cell(value: str) -> str:
    return value.strip().replace("**", "").strip()


def _fail(message: str) -> None:
    raise DeepPlanError(message)


def _epic_dir(root: Path, slug: str) -> Path:
    if not SLUG_RE.fullmatch(slug):
        _fail("Epic slug must use lowercase letters, digits, and single hyphens (1-63 characters).")
    path = (root / slug).resolve()
    if path.parent != root.resolve():
        _fail("Epic slug resolves outside the Deep Plan root.")
    return path


def _read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"Cannot read {path}: {error}")
        return ""


def _read_dag(epic_dir: Path, expected_slug: str) -> tuple[dict, list[str]]:
    errors: list[str] = []
    dag_path = epic_dir / "dependency-dag.json"
    try:
        dag = json.loads(dag_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {}, [f"Invalid dependency-dag.json: {error}"]

    if not isinstance(dag, dict):
        errors.append("dependency-dag.json must contain an object.")
        return dag, errors
    if dag.get("epic") != expected_slug:
        errors.append(f"DAG epic must equal '{expected_slug}'.")
    tasks = dag.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("DAG must contain a non-empty tasks array.")
        return dag, errors

    ids: set[str] = set()
    for index, task in enumerate(tasks):
        label = f"DAG task at index {index}"
        if not isinstance(task, dict):
            errors.append(f"{label} must be an object.")
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str) or not TASK_ID_RE.fullmatch(task_id):
            errors.append(f"{label} has invalid id {task_id!r}.")
            continue
        if task_id in ids:
            errors.append(f"DAG contains duplicate task ID {task_id}.")
        ids.add(task_id)
        module = task.get("module")
        if not isinstance(module, str) or not MODULE_ID_RE.fullmatch(module):
            errors.append(f"{task_id} has invalid module {module!r}.")
        kind = task.get("kind")
        if kind not in ALLOWED_KINDS:
            errors.append(f"{task_id} has invalid kind {kind!r}.")
        dependencies = task.get("dependencies")
        if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
            errors.append(f"{task_id} dependencies must be an array of task IDs.")
        elif len(dependencies) != len(set(dependencies)):
            errors.append(f"{task_id} has duplicate dependencies.")
        if kind == "research" and not isinstance(task.get("research_id"), str):
            errors.append(f"Research task {task_id} requires a research_id.")

    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str):
            continue
        task_id = task["id"]
        for dependency in task.get("dependencies", []):
            if dependency == task_id:
                errors.append(f"{task_id} cannot depend on itself.")
            elif dependency not in ids:
                errors.append(f"{task_id} depends on unknown task {dependency}.")

    if not errors and _has_cycle(tasks):
        errors.append("dependency-dag.json contains a cycle.")
    return dag, errors


def _has_cycle(tasks: Iterable[dict]) -> bool:
    graph = {task["id"]: task["dependencies"] for task in tasks}
    indegree = {task_id: len(dependencies) for task_id, dependencies in graph.items()}
    reverse: dict[str, list[str]] = {task_id: [] for task_id in graph}
    for task_id, dependencies in graph.items():
        for dependency in dependencies:
            reverse[dependency].append(task_id)
    queue = deque(task_id for task_id, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        task_id = queue.popleft()
        visited += 1
        for child in reverse[task_id]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    return visited != len(graph)


def _task_cards(epic_dir: Path) -> dict[str, Path]:
    cards: dict[str, Path] = {}
    tasks_dir = epic_dir / "tasks"
    if not tasks_dir.is_dir():
        return cards
    for path in tasks_dir.glob("*.md"):
        match = TASK_FILE_RE.fullmatch(path.name)
        if match:
            cards[match.group(1)] = path
    return cards


def _field(text: str, label: str) -> str | None:
    match = re.search(rf"^- \*\*{re.escape(label)}:\*\*\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _is_placeholder(value: str) -> bool:
    return not value or "[" in value or "{n}" in value.lower() or value in {"—", "-"}


def _artifact_reference_exists(epic_dir: Path, value: str) -> bool:
    reference = value.split("#", 1)[0].strip("`")
    if not reference or reference == "N/A":
        return True
    return (epic_dir / reference).is_file()


def _validate_task_card(path: Path, task: dict, epic_dir: Path) -> list[str]:
    errors: list[str] = []
    text = _read_text(path, errors)
    task_id = task["id"]
    for heading in ("## 1. Task Metadata", "## 2. Dependency and Output Contract", "## 5. Acceptance and Verification"):
        if heading not in text:
            errors.append(f"{path.name} is missing '{heading}'.")
    values: dict[str, str] = {}
    for label in REQUIRED_TASK_FIELDS:
        value = _field(text, label)
        if value is None or _is_placeholder(value):
            errors.append(f"{path.name} has an unresolved {label} field.")
        else:
            values[label] = value

    if values.get("Task ID") != task_id:
        errors.append(f"{path.name} Task ID must equal {task_id}.")
    module = values.get("Parent Module", "")
    module_match = re.match(r"`?modules/(M[0-9]{2,})-[^`]+\.md`?$", module)
    if not module_match or module_match.group(1) != task["module"]:
        errors.append(f"{path.name} Parent Module must name {task['module']} under modules/.")
    elif not (epic_dir / module.strip("`")).is_file():
        errors.append(f"{path.name} references a missing parent module: {module}.")

    for label in ("Intent Trace", "Risk Trace"):
        value = values.get(label)
        if value and not _artifact_reference_exists(epic_dir, value):
            errors.append(f"{path.name} references a missing artifact in {label}: {value}.")
    if values.get("Kind") != task["kind"]:
        errors.append(f"{path.name} Kind must equal DAG kind {task['kind']}.")
    if values.get("Verification Mode") not in ALLOWED_VERIFICATION_MODES:
        errors.append(f"{path.name} has an invalid Verification Mode.")

    prerequisites = values.get("Prerequisite Tasks", "")
    card_dependencies = [] if prerequisites == "None" else re.findall(r"T[0-9]{2,}", prerequisites)
    if set(card_dependencies) != set(task["dependencies"]):
        errors.append(f"{path.name} Prerequisite Tasks does not match DAG dependencies.")

    acceptance = re.search(r"\*\*Acceptance Criteria:\*\*(.*?)(?=\n- \*\*Verification Command|\Z)", text, re.DOTALL)
    if not acceptance or not re.search(r"^\s*1\.\s+(?!\[)", acceptance.group(1), re.MULTILINE):
        errors.append(f"{path.name} needs at least one concrete acceptance criterion.")
    commands = re.search(r"\*\*Verification Command\(s\):\*\*\s*```(?:[^\n]*)\n(.+?)```", text, re.DOTALL)
    if not commands or _is_placeholder(commands.group(1).strip()):
        errors.append(f"{path.name} needs at least one concrete verification command.")
    return errors


def _ledger_path(epic_dir: Path) -> Path:
    return epic_dir / "progress-ledger.md"


def _parse_ledger(epic_dir: Path) -> tuple[dict[str, LedgerRow], list[str]]:
    errors: list[str] = []
    text = _read_text(_ledger_path(epic_dir), errors)
    rows: dict[str, LedgerRow] = {}
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Task ID | Module | Dependencies |"):
            in_table = True
            continue
        if in_table and not line.startswith("|"):
            break
        if not in_table or re.fullmatch(r"\|[ :|-]+\|", line):
            continue
        cells = [_clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        if len(cells) != 11:
            errors.append("Ledger task matrix row must have 11 columns.")
            continue
        if not TASK_ID_RE.fullmatch(cells[0]):
            errors.append(f"Ledger has invalid task ID {cells[0]!r}.")
            continue
        if cells[0] in rows:
            errors.append(f"Ledger has duplicate row for {cells[0]}.")
            continue
        rows[cells[0]] = LedgerRow(*cells)
    if not in_table:
        errors.append("Ledger is missing the Task Execution State Matrix table.")
    return rows, errors


def _render_ledger(epic_dir: Path, rows: dict[str, LedgerRow], tasks: list[dict]) -> None:
    path = _ledger_path(epic_dir)
    text = path.read_text(encoding="utf-8")
    header = "| Task ID | Module | Dependencies | Worker Worktree | Worker Commit | Integrated Commit | Verification | Code Auditor | Challenger | Status | Remediation Count |"
    header_index = text.find(header)
    if header_index < 0:
        _fail("Ledger is missing the Task Execution State Matrix table.")
    body_start = text.find("\n", header_index) + 1
    cursor = body_start
    while cursor < len(text):
        next_line_end = text.find("\n", cursor)
        if next_line_end < 0:
            next_line_end = len(text)
        if not text[cursor:next_line_end].startswith("|"):
            break
        cursor = next_line_end + 1
    separator = "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    rendered_rows = [header, separator]
    for task in tasks:
        row = rows[task["id"]]
        rendered_rows.append(
            "| " + " | ".join((
                row.task_id, row.module, row.dependencies, row.worktree, row.worker_commit,
                row.integrated_commit, row.verification, row.code_auditor, row.challenger,
                row.status, row.remediation_count,
            )) + " |"
        )
    replacement = "\n".join(rendered_rows) + "\n"
    path.write_text(text[:header_index] + replacement + text[cursor:], encoding="utf-8")


def _default_ledger() -> str:
    return """# Swarm Execution Ledger

> Single source of truth for execution progress. Maintained by the PM / Orchestrator.

## 1. Task Execution State Matrix

| Task ID | Module | Dependencies | Worker Worktree | Worker Commit | Integrated Commit | Verification | Code Auditor | Challenger | Status | Remediation Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |

## 2. State Transition Rules

```text
READY_TO_DISPATCH -> IN_PROGRESS -> IN_REVIEW -> INTEGRATING -> VERIFIED -> COMPLETED
IN_REVIEW -> IN_REMEDIATION -> IN_REVIEW
IN_PROGRESS -> BLOCKED | FAILED
IN_REVIEW -> BLOCKED | FAILED
```

Unlock dependents only after the integrated commit, integrated-tree verification, and ledger update are recorded.

## 3. Review and Integration Evidence

## 4. Active Blockers and Remediation Items

## 5. Resume Checkpoint
"""


def command_init(args: argparse.Namespace) -> int:
    epic_dir = _epic_dir(args.root, args.epic)
    if epic_dir.exists():
        _fail(f"Epic workspace already exists: {epic_dir}")
    epic_dir.mkdir(parents=True)
    for directory in ("modules", "tasks", "research", "handoff"):
        (epic_dir / directory).mkdir()
    for filename, heading in (
        ("00-intent.md", "# Intent Dossier"),
        ("01-grounding.md", "# Grounding Dossier"),
        ("02-risk-register.md", "# Risk Register"),
    ):
        (epic_dir / filename).write_text(f"{heading}\n\nComplete this artifact before plan validation.\n", encoding="utf-8")
    shutil.copyfile(TEMPLATES / "tier1-epic-template.md", epic_dir / "03-tier1-epic.md")
    (epic_dir / "dependency-dag.json").write_text(
        json.dumps({"epic": args.epic, "tasks": []}, indent=2) + "\n", encoding="utf-8"
    )
    (epic_dir / "progress-ledger.md").write_text(_default_ledger(), encoding="utf-8")
    _atomic_write_json(_state_path(epic_dir), _new_state(args.epic))
    print(f"Created Deep Plan workspace: {epic_dir}")
    return 0


def _validate_scaffold(epic_dir: Path) -> list[str]:
    errors = [f"Missing required artifact: {name}" for name in REQUIRED_ARTIFACTS if not (epic_dir / name).is_file()]
    errors.extend(f"Missing required directory: {name}/" for name in ("modules", "tasks", "research", "handoff") if not (epic_dir / name).is_dir())
    return errors


def command_validate(args: argparse.Namespace) -> int:
    epic_dir = _epic_dir(args.root, args.epic)
    errors = _validate_scaffold(epic_dir)
    if args.stage == "scaffold":
        return _report_validation(errors)
    dag, dag_errors = _read_dag(epic_dir, args.epic)
    errors.extend(dag_errors)
    if dag_errors:
        return _report_validation(errors)
    state, state_errors = _load_state(epic_dir, args.epic)
    errors.extend(state_errors)
    if state_errors:
        return _report_validation(errors)
    cards = _task_cards(epic_dir)
    dag_tasks = {task["id"]: task for task in dag["tasks"]}
    state_tasks = state.get("tasks", {})
    for task_id in sorted(set(dag_tasks) - set(state_tasks)):
        errors.append(f"Execution state is missing a task entry for {task_id}; run sync-ledger.")
    for task_id in sorted(set(state_tasks) - set(dag_tasks)):
        errors.append(f"Execution state has an entry for unknown task {task_id}.")
    for task_id in sorted(set(dag_tasks) - set(cards)):
        errors.append(f"DAG task {task_id} is missing a matching Tier 3 task card.")
    for task_id in sorted(set(cards) - set(dag_tasks)):
        errors.append(f"Tier 3 task card {cards[task_id].name} is absent from the DAG.")
    for task_id, task in dag_tasks.items():
        card = cards.get(task_id)
        if card:
            errors.extend(_validate_task_card(card, task, epic_dir))
    ledger_rows, ledger_errors = _parse_ledger(epic_dir)
    errors.extend(ledger_errors)
    for task_id in sorted(set(dag_tasks) - set(ledger_rows)):
        errors.append(f"Ledger is missing a row for {task_id}; run sync-ledger.")
    for task_id in sorted(set(ledger_rows) - set(dag_tasks)):
        errors.append(f"Ledger has a row for unknown task {task_id}.")
    for task_id, row in ledger_rows.items():
        if row.status not in ALLOWED_STATUSES:
            errors.append(f"Ledger row {task_id} has invalid status {row.status!r}.")
        if task_id in state_tasks and row.status != state_tasks[task_id].get("status"):
            errors.append(f"Ledger row {task_id} status does not match execution-state.json.")
        if task_id in dag_tasks and row.module != dag_tasks[task_id]["module"]:
            errors.append(f"Ledger row {task_id} module does not match DAG.")
    return _report_validation(errors)


def _report_validation(errors: list[str]) -> int:
    if errors:
        print("Deep Plan validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Deep Plan validation passed.")
    return 0


def command_sync_ledger(args: argparse.Namespace) -> int:
    epic_dir = _epic_dir(args.root, args.epic)
    dag, errors = _read_dag(epic_dir, args.epic)
    if errors:
        return _report_validation(errors)
    state, state_errors = _load_state(epic_dir, args.epic)
    if state_errors:
        return _report_validation(state_errors)
    existing_tasks = state.get("tasks", {})
    dag_ids = {task["id"] for task in dag["tasks"]}
    removed_tasks = sorted(set(existing_tasks) - dag_ids)
    if removed_tasks:
        _fail("DAG removed tasks already present in execution state: " + ", ".join(removed_tasks))
    tasks: dict[str, dict] = {}
    for task in dag["tasks"]:
        task_id = task["id"]
        if task_id in existing_tasks:
            current = existing_tasks[task_id]
            if current.get("module") != task["module"] or set(current.get("dependencies", [])) != set(task["dependencies"]):
                _fail(f"DAG ownership or dependencies changed for active task {task_id}; review state before syncing.")
            tasks[task_id] = current
        else:
            status = "READY_TO_DISPATCH" if not task["dependencies"] else "BLOCKED"
            tasks[task_id] = {
                "module": task["module"],
                "kind": task["kind"],
                "dependencies": task["dependencies"],
                "status": status,
                "required_reviews": [],
                "reviews": {},
                "remediation_count": 0,
            }
    state["tasks"] = tasks
    _record_event(state, "sync-ledger", details={"task_count": len(tasks)})
    _save_state(state, epic_dir)
    _sync_ledger_projection(epic_dir, state, dag)
    print(f"Synchronized ledger for {args.epic}.")
    return 0


def _ready_task_ids(dag: dict, rows: dict[str, LedgerRow]) -> list[str]:
    ready: list[str] = []
    for task in dag["tasks"]:
        task_id = task["id"]
        row = rows.get(task_id)
        if not row or row.status != "READY_TO_DISPATCH":
            continue
        if all(rows.get(dependency) and rows[dependency].status == "COMPLETED" for dependency in task["dependencies"]):
            ready.append(task_id)
    return ready


def _ready_state_task_ids(dag: dict, state: dict) -> list[str]:
    rows = _state_rows(state)
    return _ready_task_ids(dag, rows)


def command_status(args: argparse.Namespace) -> int:
    epic_dir = _epic_dir(args.root, args.epic)
    dag, dag_errors = _read_dag(epic_dir, args.epic)
    state, state_errors = _load_state(epic_dir, args.epic)
    if dag_errors or state_errors:
        return _report_validation(dag_errors + state_errors)
    rows = _state_rows(state)
    counts = Counter(row.status for row in rows.values())
    print(f"Epic: {args.epic}")
    for status in sorted(counts):
        print(f"{status}: {counts[status]}")
    ready = _ready_state_task_ids(dag, state)
    print("Ready tasks: " + (", ".join(ready) if ready else "None"))
    return 0


def command_ready(args: argparse.Namespace) -> int:
    epic_dir = _epic_dir(args.root, args.epic)
    dag, dag_errors = _read_dag(epic_dir, args.epic)
    state, state_errors = _load_state(epic_dir, args.epic)
    if dag_errors or state_errors:
        return _report_validation(dag_errors + state_errors)
    for task_id in _ready_state_task_ids(dag, state):
        print(task_id)
    return 0


def _git(repo_root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *arguments], text=True, capture_output=True, check=False
    )
    if result.returncode != 0:
        _fail(result.stderr.strip() or f"git {' '.join(arguments)} failed.")
    return result.stdout.strip()


def _git_head(repo_root: Path) -> str:
    return _git(repo_root, "rev-parse", "HEAD")


def _git_branch(repo_root: Path) -> str:
    return _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")


def _has_unmanaged_changes(repo_root: Path, epic_dir: Path) -> bool:
    managed_prefix = epic_dir.relative_to(repo_root).as_posix().rstrip("/") + "/"
    status = _git(repo_root, "status", "--porcelain", "--untracked-files=all")
    for line in status.splitlines():
        path = line[3:].replace("\\", "/")
        paths = [part.strip() for part in path.split(" -> ")]
        if any(not candidate.startswith(managed_prefix) for candidate in paths):
            return True
    return False


def command_worktree_create(args: argparse.Namespace) -> int:
    _assert_pm_checkout()
    epic_dir = _epic_dir(args.root, args.epic)
    dag, dag_errors = _read_dag(epic_dir, args.epic)
    state, state_errors = _load_state(epic_dir, args.epic)
    if dag_errors or state_errors:
        return _report_validation(dag_errors + state_errors)
    task = next((item for item in dag["tasks"] if item["id"] == args.task_id), None)
    if not task:
        _fail(f"Unknown task ID: {args.task_id}")
    if args.task_id not in _ready_state_task_ids(dag, state):
        _fail(f"{args.task_id} is not READY_TO_DISPATCH with completed dependencies.")
    repo_root = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel"))
    if _has_unmanaged_changes(repo_root, epic_dir):
        _fail("Parent repository has changes outside this epic's .deep-plan state; commit or stash them before creating a worker worktree.")
    card = _task_cards(epic_dir).get(args.task_id)
    if not card:
        _fail(f"Missing task card for {args.task_id}.")
    suffix = card.stem.split("-", 1)[1]
    worktree_path = (repo_root / ".worktrees" / card.stem).resolve()
    if not str(worktree_path).startswith(str((repo_root / ".worktrees").resolve())):
        _fail("Worktree path resolves outside .worktrees.")
    if worktree_path.exists():
        _fail(f"Worktree already exists: {worktree_path}")
    branch = f"task/{args.task_id}-{suffix}"
    if subprocess.run(["git", "-C", str(repo_root), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], check=False).returncode == 0:
        _fail(f"Branch already exists: {branch}")
    _git(repo_root, "rev-parse", "--verify", args.parent)
    _git(repo_root, "worktree", "add", "-b", branch, str(worktree_path), args.parent)
    task_state = state["tasks"][args.task_id]
    task_state["worktree"] = str(worktree_path.relative_to(repo_root)).replace("\\", "/")
    task_state["branch"] = branch
    task_state["parent_ref"] = args.parent
    task_state["status"] = "IN_PROGRESS"
    _record_event(state, "worktree-created", args.task_id, {"branch": branch, "parent_ref": args.parent})
    _save_state(state, epic_dir)
    _sync_ledger_projection(epic_dir, state, dag)
    print(f"Created {worktree_path} on {branch} from {args.parent}.")
    return 0


def _assert_pm_checkout() -> Path:
    repo_root = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel"))
    relative = Path.cwd().resolve().relative_to(repo_root).as_posix().split("/")
    if ".worktrees" in relative:
        _fail("Execution-state mutations must run from the parent PM checkout, not a worker worktree.")
    return repo_root


def _evidence_path(epic_dir: Path, value: str) -> str:
    candidate = Path(value)
    path = (candidate if candidate.is_absolute() else epic_dir / candidate).resolve()
    if not path.is_file():
        _fail(f"Evidence file does not exist: {value}")
    try:
        return path.relative_to(epic_dir.resolve()).as_posix()
    except ValueError:
        _fail("Evidence must be stored inside the epic workspace.")


def _load_mutation(args: argparse.Namespace) -> tuple[Path, dict, dict, dict]:
    _assert_pm_checkout()
    epic_dir = _epic_dir(args.root, args.epic)
    dag, dag_errors = _read_dag(epic_dir, args.epic)
    state, state_errors = _load_state(epic_dir, args.epic)
    if dag_errors or state_errors:
        _fail("; ".join(dag_errors + state_errors))
    task = next((item for item in dag["tasks"] if item["id"] == args.task_id), None)
    if not task:
        _fail(f"Unknown task ID: {args.task_id}")
    if args.task_id not in state["tasks"]:
        _fail(f"Execution state has no task entry for {args.task_id}; run sync-ledger.")
    return epic_dir, dag, state, task


def _persist_mutation(epic_dir: Path, dag: dict, state: dict) -> None:
    _save_state(state, epic_dir)
    _sync_ledger_projection(epic_dir, state, dag)


def command_worker_record(args: argparse.Namespace) -> int:
    epic_dir, dag, state, _ = _load_mutation(args)
    task_state = state["tasks"][args.task_id]
    if task_state["status"] != "IN_PROGRESS":
        _fail(f"{args.task_id} must be IN_PROGRESS before recording a worker result.")
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", args.commit):
        _fail("Worker commit must be a hexadecimal Git SHA.")
    task_state["worker_commit"] = args.commit
    task_state["modified_paths"] = args.path
    task_state["verification"] = _evidence_path(epic_dir, args.evidence)
    required_reviews = ["standards", "spec", "challenger"]
    for axis in args.required_review or []:
        if axis not in required_reviews:
            required_reviews.append(axis)
    task_state["required_reviews"] = required_reviews
    task_state["reviews"] = {}
    if args.status == "COMPLETED":
        task_state["status"] = "IN_REVIEW"
    else:
        task_state["status"] = args.status
    _record_event(state, "worker-recorded", args.task_id, {"commit": args.commit, "status": args.status})
    _persist_mutation(epic_dir, dag, state)
    print(f"Recorded worker result for {args.task_id}; status={task_state['status']}.")
    return 0


def command_review_record(args: argparse.Namespace) -> int:
    epic_dir, dag, state, _ = _load_mutation(args)
    task_state = state["tasks"][args.task_id]
    if task_state["status"] not in {"IN_REVIEW", "IN_REMEDIATION"}:
        _fail(f"{args.task_id} is not accepting review evidence in status {task_state['status']}.")
    if args.axis not in task_state.get("required_reviews", []):
        _fail(f"Review axis '{args.axis}' is not required for {args.task_id}.")
    task_state.setdefault("reviews", {})[args.axis] = {
        "verdict": args.verdict,
        "evidence": _evidence_path(epic_dir, args.evidence),
        "recorded_at": _now(),
    }
    _record_event(state, "review-recorded", args.task_id, {"axis": args.axis, "verdict": args.verdict})
    _persist_mutation(epic_dir, dag, state)
    print(f"Recorded {args.axis}={args.verdict} for {args.task_id}.")
    return 0


TRANSITIONS = {
    "READY_TO_DISPATCH": {"IN_PROGRESS"},
    "IN_PROGRESS": {"IN_REVIEW", "BLOCKED", "FAILED"},
    "IN_REVIEW": {"INTEGRATING", "IN_REMEDIATION", "BLOCKED", "FAILED"},
    "IN_REMEDIATION": {"IN_REVIEW", "BLOCKED", "FAILED"},
    "INTEGRATING": {"VERIFIED", "BLOCKED", "FAILED"},
    "VERIFIED": {"COMPLETED", "FAILED"},
}


def _all_reviews_pass(task_state: dict) -> bool:
    required = task_state.get("required_reviews", [])
    reviews = task_state.get("reviews", {})
    return bool(required) and all(reviews.get(axis, {}).get("verdict") == "PASS" for axis in required)


def command_transition(args: argparse.Namespace) -> int:
    epic_dir, dag, state, _ = _load_mutation(args)
    task_state = state["tasks"][args.task_id]
    current = task_state["status"]
    if args.to not in TRANSITIONS.get(current, set()):
        _fail(f"Illegal transition for {args.task_id}: {current} -> {args.to}.")
    if args.to == "IN_REVIEW" and not task_state.get("worker_commit"):
        _fail("A worker commit is required before entering IN_REVIEW.")
    if args.to == "INTEGRATING" and not _all_reviews_pass(task_state):
        _fail("Every required review must be present and PASS before integration.")
    if args.to == "COMPLETED" and (not task_state.get("integrated_commit") or not task_state.get("integrated_verification")):
        _fail("Integrated commit and integrated verification are required before COMPLETED.")
    if args.to == "IN_REMEDIATION":
        task_state["remediation_count"] = task_state.get("remediation_count", 0) + 1
        if task_state["remediation_count"] > args.remediation_limit:
            _fail("Remediation limit exceeded; use BLOCKED or FAILED and escalate.")
    task_state["status"] = args.to
    _record_event(state, "transition", args.task_id, {"from": current, "to": args.to})
    _persist_mutation(epic_dir, dag, state)
    print(f"Transitioned {args.task_id}: {current} -> {args.to}.")
    return 0


def command_integrate_record(args: argparse.Namespace) -> int:
    epic_dir, dag, state, _ = _load_mutation(args)
    task_state = state["tasks"][args.task_id]
    if task_state["status"] != "INTEGRATING":
        _fail(f"{args.task_id} must be INTEGRATING before recording integration.")
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", args.commit):
        _fail("Integrated commit must be a hexadecimal Git SHA.")
    task_state["integrated_commit"] = args.commit
    _record_event(state, "integration-recorded", args.task_id, {"commit": args.commit})
    _persist_mutation(epic_dir, dag, state)
    print(f"Recorded integrated commit for {args.task_id}.")
    return 0


def command_verify_record(args: argparse.Namespace) -> int:
    epic_dir, dag, state, _ = _load_mutation(args)
    task_state = state["tasks"][args.task_id]
    if task_state["status"] != "INTEGRATING":
        _fail(f"{args.task_id} must be INTEGRATING before recording integrated verification.")
    task_state["integrated_verification"] = _evidence_path(epic_dir, args.evidence)
    task_state["verification"] = task_state["integrated_verification"]
    task_state["status"] = "VERIFIED"
    _record_event(state, "integrated-verification-recorded", args.task_id, {"evidence": task_state["integrated_verification"]})
    _persist_mutation(epic_dir, dag, state)
    print(f"Recorded integrated verification for {args.task_id}; status=VERIFIED.")
    return 0


def _parse_task_progress(value: str) -> tuple[str, int, int]:
    parts = value.split(":")
    if len(parts) != 3:
        _fail(f"--task-progress must be TASK_ID:COMPLETED_STEP:TOTAL_STEPS, got {value!r}")
    task_id, completed, total = parts
    if not TASK_ID_RE.fullmatch(task_id):
        _fail(f"Invalid task ID in --task-progress: {task_id!r}")
    try:
        completed_int, total_int = int(completed), int(total)
    except ValueError:
        _fail(f"Step numbers must be integers in --task-progress: {value!r}")
    if completed_int < 0 or total_int < 1 or completed_int > total_int:
        _fail(f"Invalid step range in --task-progress: completed={completed_int}, total={total_int}")
    return task_id, completed_int, total_int


def _step_summary_from_card(epic_dir: Path, task_id: str, step_num: int) -> str:
    cards = _task_cards(epic_dir)
    card = cards.get(task_id)
    if not card:
        return ""
    text = card.read_text(encoding="utf-8")
    patterns = [
        rf"(?:^|\n)[ \t]*-[ \t]*\*\*Step[ \t]+{step_num}:?\*\*[ \t]*(.+)",
        rf"(?:^|\n)[ \t]*\*\*Step[ \t]+{step_num}:?\*\*[ \t]*(.+)",
        rf"(?:^|\n)[ \t]*{step_num}\.[ \t]*\*\*(.+?)\*\*",
        rf"(?:^|\n)[ \t]*{step_num}\.[ \t]+([^\n]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            val = match.group(1).strip().rstrip(":").strip()
            if val and not _is_placeholder(val):
                return val
    return ""


def _generate_handoff_dossier(
    epic_dir: Path,
    epic: str,
    state: dict,
    dag: dict,
    reason: str,
    note: str,
    parent_branch: str,
    parent_head: str,
    progress_map: dict[str, dict],
    repo_root: Path | None = None,
) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M")
    filename = f"HANDOFF-{timestamp}.md"
    path = epic_dir / "handoff" / filename

    tasks = state.get("tasks", {})
    completed = [tid for tid, t in tasks.items() if t.get("status") == "COMPLETED"]
    in_progress = [tid for tid, t in tasks.items() if t.get("status") == "IN_PROGRESS"]
    in_review = [tid for tid, t in tasks.items() if t.get("status") in ("IN_REVIEW", "IN_REMEDIATION")]
    blocked = [tid for tid, t in tasks.items() if t.get("status") in ("BLOCKED", "FAILED")]
    ready = [tid for tid, t in tasks.items() if t.get("status") == "READY_TO_DISPATCH"]

    lines = [
        f"# Handoff: {epic} — {_now()}",
        "",
        "## Pause Reason",
        f"**{reason}**" + (f" — {note}" if note else ""),
        "",
        "## Session Summary",
        f"- **Completed:** {', '.join(sorted(completed)) or 'None'}",
        f"- **In Progress:** {', '.join(sorted(in_progress)) or 'None'}",
        f"- **In Review:** {', '.join(sorted(in_review)) or 'None'}",
        f"- **Blocked/Failed:** {', '.join(sorted(blocked)) or 'None'}",
        f"- **Ready to Dispatch:** {', '.join(sorted(ready)) or 'None'}",
        "",
    ]

    if in_progress or in_review:
        lines.append("## In-Flight Task Details")
        lines.append("")
        for tid in sorted(in_progress + in_review):
            t = tasks[tid]
            lines.append(f"### {tid}")
            lines.append(f"- **Status:** {t.get('status')}")
            if t.get("worktree"):
                lines.append(f"- **Worktree:** `{t['worktree']}`")
            if t.get("branch"):
                lines.append(f"- **Branch:** `{t['branch']}`")
            if t.get("worker_commit"):
                lines.append(f"- **Worker Commit:** `{t['worker_commit']}`")
            elif t.get("branch") and repo_root:
                try:
                    wip_commit = _git(repo_root, "rev-parse", t["branch"]).strip()
                    if wip_commit and wip_commit != parent_head:
                        lines.append(f"- **WIP Commit:** `{wip_commit[:12]}`")
                except DeepPlanError:
                    pass

            prog = progress_map.get(tid) or t.get("step_progress")
            if prog:
                completed_step = prog["completed_step"]
                total = prog["total_steps"]
                summary = prog.get("summary", "")
                summary_str = f' — "{summary}"' if summary else ""
                lines.append(f"- **Last Completed Step:** {completed_step} of {total}{summary_str}")
                if completed_step < total:
                    next_step = completed_step + 1
                    next_summary = _step_summary_from_card(epic_dir, tid, next_step)
                    next_summary_str = f' — "{next_summary}"' if next_summary else ""
                    lines.append(f"- **Next Step:** {next_step}{next_summary_str}")

            if t.get("status") in ("IN_REVIEW", "IN_REMEDIATION"):
                required = t.get("required_reviews", [])
                reviews = t.get("reviews", {})
                pending = [ax for ax in required if ax not in reviews]
                if pending:
                    lines.append(f"- **Pending Reviews:** {', '.join(pending)}")
            lines.append("")

    lines.extend([
        "## Git State",
        f"- **Parent Branch:** `{parent_branch}`",
        f"- **Parent HEAD:** `{parent_head}`",
        "",
        "## Resume Instructions",
        f"1. Run: `python script/deep_plan.py resume {epic}`",
        f"2. Verify parent branch HEAD matches `{parent_head[:12]}`",
    ])

    step_counter = 3
    for tid in sorted(in_progress):
        prog = progress_map.get(tid) or tasks[tid].get("step_progress")
        if prog and prog["completed_step"] < prog["total_steps"]:
            next_step = prog["completed_step"] + 1
            summary = _step_summary_from_card(epic_dir, tid, next_step)
            action_desc = f' — "{summary}"' if summary else ""
            lines.append(f"{step_counter}. Continue {tid} from Step {next_step}{action_desc}")
            step_counter += 1

    lines.append("")
    (epic_dir / "handoff").mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return f"handoff/{filename}"


def _update_ledger_checkpoint(
    epic_dir: Path,
    state: dict,
    dag: dict,
    parent_branch: str,
    parent_head: str,
    handoff_path: str,
) -> None:
    ledger_path = _ledger_path(epic_dir)
    if not ledger_path.is_file():
        return
    text = ledger_path.read_text(encoding="utf-8")
    section_header = "## 5. Resume Checkpoint"
    header_index = text.find(section_header)
    if header_index < 0:
        return

    next_section = text.find("\n## ", header_index + len(section_header))
    section_end = next_section if next_section >= 0 else len(text)

    tasks = state.get("tasks", {})
    last_event = state.get("events", [{}])[-1] if state.get("events") else {}
    last_transition = f"{last_event.get('task_id', 'epic')}/{last_event.get('action', 'none')}"

    integrated = [
        f"`{t.get('integrated_commit', '')[:12]}`"
        for t in tasks.values()
        if t.get("integrated_commit")
    ]
    ready = _ready_state_task_ids(dag, state)

    in_flight_lines = []
    for tid, t in sorted(tasks.items()):
        if t.get("status") in ("IN_PROGRESS", "IN_REVIEW", "IN_REMEDIATION"):
            prog = t.get("step_progress")
            step_info = ""
            if prog:
                step_info = f" (Step {prog['completed_step']}/{prog['total_steps']})"
            in_flight_lines.append(f"  - {tid}: {t['status']}{step_info}")

    in_flight_text = "\n".join(in_flight_lines) if in_flight_lines else "  - None"

    replacement = f"""{section_header}

- **Last completed transition:** `{last_transition}`
- **Parent branch:** `{parent_branch}`
- **Parent HEAD:** `{parent_head[:12]}`
- **Integrated commits:** {', '.join(integrated) or 'None'}
- **Next ready tasks:** {', '.join(ready) or 'None'}
- **In-flight tasks:**
{in_flight_text}
- **Handoff summary:** `{handoff_path}`
"""
    new_text = text[:header_index] + replacement
    if next_section >= 0:
        new_text += text[section_end:]
    ledger_path.write_text(new_text, encoding="utf-8")


def command_pause(args: argparse.Namespace) -> int:
    repo_root = _assert_pm_checkout()
    epic_dir = _epic_dir(args.root, args.epic)
    dag, dag_errors = _read_dag(epic_dir, args.epic)
    state, state_errors = _load_state(epic_dir, args.epic)
    if dag_errors or state_errors:
        _fail("; ".join(dag_errors + state_errors))

    if state.get("pause_state"):
        _fail(f"Epic {args.epic} is already paused. Run 'resume' before pausing again.")

    progress_map: dict[str, dict] = {}
    for entry in args.task_progress or []:
        task_id, completed, total = _parse_task_progress(entry)
        if task_id not in state.get("tasks", {}):
            _fail(f"Unknown task {task_id} in --task-progress.")
        summary = _step_summary_from_card(epic_dir, task_id, completed) if completed > 0 else ""
        progress_map[task_id] = {
            "completed_step": completed,
            "total_steps": total,
            "summary": summary,
            "recorded_at": _now(),
        }

    for task_id, prog in progress_map.items():
        state["tasks"][task_id]["step_progress"] = prog

    parent_branch = _git_branch(repo_root)
    parent_head = _git_head(repo_root)

    tasks = state.get("tasks", {})
    in_flight = {}
    for tid, t in tasks.items():
        if t.get("status") == "IN_PROGRESS":
            entry = {
                "status": "IN_PROGRESS",
                "worktree": t.get("worktree", ""),
                "branch": t.get("branch", ""),
            }
            if t.get("branch"):
                try:
                    wip = _git(repo_root, "rev-parse", t["branch"]).strip()
                    if wip and wip != parent_head:
                        entry["wip_commit"] = wip[:12]
                except DeepPlanError:
                    pass
            prog = progress_map.get(tid) or t.get("step_progress")
            if prog:
                entry["step_progress"] = {
                    "completed_step": prog["completed_step"],
                    "total_steps": prog["total_steps"],
                }
                if prog.get("summary"):
                    entry["step_progress"]["summary"] = prog["summary"]
            in_flight[tid] = entry
        elif t.get("status") in ("IN_REVIEW", "IN_REMEDIATION"):
            required = t.get("required_reviews", [])
            reviews = t.get("reviews", {})
            pending = [ax for ax in required if ax not in reviews]
            in_flight[tid] = {
                "status": t["status"],
                "pending_reviews": pending,
            }

    completed_this_session = [
        e["task_id"] for e in state.get("events", [])
        if e.get("action") == "transition"
        and e.get("details", {}).get("to") == "COMPLETED"
        and e.get("task_id")
    ]

    handoff_path = _generate_handoff_dossier(
        epic_dir, args.epic, state, dag,
        args.reason, args.note or "", parent_branch, parent_head,
        progress_map,
        repo_root=repo_root,
    )

    state["pause_state"] = {
        "reason": args.reason,
        "note": args.note or "",
        "paused_at": _now(),
        "parent_branch": parent_branch,
        "parent_head": parent_head,
        "handoff_path": handoff_path,
        "session_tasks_completed": sorted(set(completed_this_session)),
        "in_flight_tasks": in_flight,
    }

    _record_event(state, "paused", details={
        "reason": args.reason,
        "handoff_path": handoff_path,
        "in_flight_count": len(in_flight),
    })

    _update_ledger_checkpoint(epic_dir, state, dag, parent_branch, parent_head, handoff_path)
    _persist_mutation(epic_dir, dag, state)

    print(f"Epic {args.epic} paused ({args.reason}).")
    print(f"Handoff dossier: {handoff_path}")
    if in_flight:
        print(f"In-flight tasks: {', '.join(sorted(in_flight))}")
    return 0


def command_resume(args: argparse.Namespace) -> int:
    repo_root = _assert_pm_checkout()
    epic_dir = _epic_dir(args.root, args.epic)
    dag, dag_errors = _read_dag(epic_dir, args.epic)
    state, state_errors = _load_state(epic_dir, args.epic)
    if dag_errors or state_errors:
        _fail("; ".join(dag_errors + state_errors))

    pause = state.get("pause_state")
    tasks = state.get("tasks", {})

    current_branch = _git_branch(repo_root)
    current_head = _git_head(repo_root)

    print(f"[Deep Plan] Resuming epic: {args.epic}")
    print()

    if pause:
        print(f"  Paused at:       {pause.get('paused_at', 'N/A')}")
        print(f"  Reason:          {pause.get('reason', 'N/A')}")
        if pause.get("note"):
            print(f"  Note:            {pause['note']}")
        print(f"  Handoff dossier: {pause.get('handoff_path', 'N/A')}")
        print()

        expected_head = pause.get("parent_head", "")
        expected_branch = pause.get("parent_branch", "")

        if expected_branch and current_branch != expected_branch:
            print(f"  ! Branch mismatch: expected '{expected_branch}', on '{current_branch}'")
        if expected_head and current_head != expected_head:
            print(f"  ! HEAD mismatch: expected {expected_head[:12]}, got {current_head[:12]}")
            print("    Parent branch may have advanced. Verify integrated commits are intact.")
        else:
            print("  * Parent branch HEAD matches recorded checkpoint.")
        print()

    in_progress = {tid: t for tid, t in tasks.items() if t.get("status") == "IN_PROGRESS"}
    in_review = {tid: t for tid, t in tasks.items() if t.get("status") in ("IN_REVIEW", "IN_REMEDIATION")}

    if in_progress:
        print("  In-Progress Tasks (worktree reconciliation):")
        for tid, t in sorted(in_progress.items()):
            worktree = t.get("worktree", "")
            branch = t.get("branch", "")
            worktree_path = (repo_root / worktree) if worktree else None

            prog = t.get("step_progress")
            step_info = ""
            if prog:
                step_info = f" (Step {prog['completed_step']}/{prog['total_steps']})"

            if worktree_path and worktree_path.is_dir():
                parent_ref = t.get("parent_ref", "HEAD")
                has_commits = False
                if branch:
                    try:
                        log = _git(repo_root, "log", "--oneline", f"{parent_ref}..{branch}")
                        has_commits = bool(log.strip())
                    except DeepPlanError:
                        pass

                if prog and prog["completed_step"] < prog["total_steps"]:
                    next_step = prog["completed_step"] + 1
                    summary = _step_summary_from_card(epic_dir, tid, next_step)
                    action_desc = f' — "{summary}"' if summary else ""
                    commit_status = "with WIP commit" if has_commits else "no new commits"
                    print(f"    {tid}: Worktree exists ({commit_status}){step_info}")
                    print(f"      -> Action: Continue from Step {next_step}{action_desc}")
                elif has_commits:
                    print(f"    {tid}: Worktree exists with finished commit(s){step_info}")
                    print("      -> Action: Record worker result with worker-record, then advance to IN_REVIEW")
                else:
                    print(f"    {tid}: Worktree exists, no new commits{step_info}")
                    print("      -> Action: Re-dispatch worker in existing worktree")
            else:
                print(f"    {tid}: Worktree missing or not yet created")
                print("      -> Action: Create worktree with worktree-create, then dispatch")
        print()

    if in_review:
        print("  In-Review Tasks:")
        for tid, t in sorted(in_review.items()):
            required = t.get("required_reviews", [])
            reviews = t.get("reviews", {})
            pending = [ax for ax in required if ax not in reviews]
            failed = [ax for ax, r in reviews.items() if r.get("verdict") == "FAIL"]
            if pending:
                print(f"    {tid}: Pending reviews: {', '.join(pending)}")
            if failed:
                print(f"    {tid}: Failed reviews: {', '.join(failed)}")
            if not pending and not failed:
                print(f"    {tid}: All reviews passed -> ready for transition --to INTEGRATING")
        print()

    ready = _ready_state_task_ids(dag, state)
    if ready:
        print(f"  Ready to dispatch: {', '.join(ready)}")
    else:
        all_completed = all(t.get("status") == "COMPLETED" for t in tasks.values())
        if all_completed and tasks:
            print("  All tasks COMPLETED — run final epic verification.")
        else:
            print("  No tasks ready to dispatch.")

    counts = Counter(t.get("status", "UNKNOWN") for t in tasks.values())
    print()
    print("  Status summary:")
    for status in sorted(counts):
        print(f"    {status}: {counts[status]}")

    state["pause_state"] = None
    _record_event(state, "resumed", details={
        "from_pause": pause.get("paused_at") if pause else None,
        "head_match": (not pause or current_head == pause.get("parent_head", "")),
        "in_progress_count": len(in_progress),
        "ready_count": len(ready),
    })
    _save_state(state, epic_dir)
    _sync_ledger_projection(epic_dir, state, dag)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic Deep Plan workflow helpers.")
    parser.add_argument("--root", type=Path, default=Path(".deep-plan"), help="Deep Plan state directory.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init = subparsers.add_parser("init", help="Create a new Deep Plan workspace.")
    init.add_argument("epic")
    init.set_defaults(handler=command_init)
    validate = subparsers.add_parser("validate", help="Validate workspace or completed plan structure.")
    validate.add_argument("epic")
    validate.add_argument("--stage", choices=("scaffold", "plan"), default="plan")
    validate.set_defaults(handler=command_validate)
    sync = subparsers.add_parser("sync-ledger", help="Create missing ledger rows from the DAG.")
    sync.add_argument("epic")
    sync.set_defaults(handler=command_sync_ledger)
    status = subparsers.add_parser("status", help="Show ledger counts and derived ready tasks.")
    status.add_argument("epic")
    status.set_defaults(handler=command_status)
    ready = subparsers.add_parser("ready", help="Print dispatchable task IDs.")
    ready.add_argument("epic")
    ready.set_defaults(handler=command_ready)
    worktree = subparsers.add_parser("worktree-create", help="Create a guarded worker worktree for a ready task.")
    worktree.add_argument("epic")
    worktree.add_argument("task_id")
    worktree.add_argument("--parent", required=True, help="Verified parent branch or commit.")
    worktree.set_defaults(handler=command_worktree_create)
    worker = subparsers.add_parser("worker-record", help="Record a worker result in PM-owned state.")
    worker.add_argument("epic")
    worker.add_argument("task_id")
    worker.add_argument("--status", choices=("COMPLETED", "BLOCKED", "FAILED"), default="COMPLETED")
    worker.add_argument("--commit", required=True)
    worker.add_argument("--evidence", required=True)
    worker.add_argument("--path", action="append", default=[])
    worker.add_argument("--required-review", action="append")
    worker.set_defaults(handler=command_worker_record)
    review = subparsers.add_parser("review-record", help="Record one reviewer verdict in PM-owned state.")
    review.add_argument("epic")
    review.add_argument("task_id")
    review.add_argument("--axis", choices=("standards", "spec", "challenger", "security", "performance", "documentation"), required=True)
    review.add_argument("--verdict", choices=("PASS", "FAIL"), required=True)
    review.add_argument("--evidence", required=True)
    review.set_defaults(handler=command_review_record)
    transition = subparsers.add_parser("transition", help="Apply a guarded task state transition.")
    transition.add_argument("epic")
    transition.add_argument("task_id")
    transition.add_argument("--to", required=True, choices=sorted(ALLOWED_STATUSES))
    transition.add_argument("--remediation-limit", type=int, default=2)
    transition.set_defaults(handler=command_transition)
    integration = subparsers.add_parser("integration-record", help="Record a manually integrated commit.")
    integration.add_argument("epic")
    integration.add_argument("task_id")
    integration.add_argument("--commit", required=True)
    integration.set_defaults(handler=command_integrate_record)
    verification = subparsers.add_parser("verify-record", help="Record integrated-tree verification.")
    verification.add_argument("epic")
    verification.add_argument("task_id")
    verification.add_argument("--evidence", required=True)
    verification.set_defaults(handler=command_verify_record)
    pause = subparsers.add_parser("pause", help="Gracefully pause the epic and generate a handoff dossier.")
    pause.add_argument("epic")
    pause.add_argument("--reason", required=True, choices=PAUSE_REASONS, help="Why the epic is being paused.")
    pause.add_argument("--note", help="Context for the next session.")
    pause.add_argument("--task-progress", action="append", default=[], help="Step progress as TASK_ID:COMPLETED_STEP:TOTAL_STEPS (repeatable).")
    pause.set_defaults(handler=command_pause)
    resume_cmd = subparsers.add_parser("resume", help="Resume a paused epic with worktree reconciliation.")
    resume_cmd.add_argument("epic")
    resume_cmd.set_defaults(handler=command_resume)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except DeepPlanError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
