"""Pure, conservative planning of bounded Copilot task handoffs."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


_STATUSES = {"pending", "running", "done", "completed", "failed", "skipped", "blocked"}
_DONE = {"done", "completed"}
_CONTROL_NAMES = {
    "state", "mandate", "protocol", "plan", "evidence", "coverage",
    "search_log", "search-log", "review", "synthesis", "deliverables",
    "enablement", "access_plan", "access-plan", "access", "checkpoints",
    "checkpoint", "status", "tasks", "audit", "events", "ledger",
}
_STOP_INSTRUCTION = (
    "Do not write coordinator state or launch further workers. Stay within the "
    "declared scope and approved access. On any source, API, MCP, site, or task "
    "access block, stop work and notify the coordinator immediately; the "
    "coordinator must hold the project and stop sibling agents through the "
    "actual client. Return evidence and observed executor information; roles "
    "do not establish model independence. Do not claim a model identity unless "
    "visible (Auto/default only when actually visible)."
)


def _strings(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{name} must be a list of nonempty strings")
    if len(set(value)) != len(value):
        raise ValueError(f"{name} must not contain duplicates")
    return list(value)


def _path(value: str) -> str:
    if (
        not value
        or value != value.strip()
        or value.startswith("/")
        or "\\" in value
        or ":" in value
        or any(char in value for char in "*?[]")
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        raise ValueError(f"unsafe write path: {value!r}")
    parts = value.rstrip("/").split("/")
    if any(part in {"", ".", ".."} or part.endswith((" ", ".")) for part in parts):
        raise ValueError(f"write paths must be normalized relative paths: {value!r}")
    first = re.sub(r"^\d+[-_]", "", parts[0].lower()).split(".", 1)[0]
    if first in _CONTROL_NAMES or parts[0].lower() in {".atlas", ".git"}:
        raise ValueError(f"worker cannot write coordinator control path: {value!r}")
    if any(part.lower() == "state.sqlite3" for part in parts):
        raise ValueError(f"worker cannot write coordinator state: {value!r}")
    return "/".join(parts)


def validate_task_scope(task: Mapping[str, Any]) -> dict[str, Any]:
    """Validate optional scope; absent write_paths means unknown, not read-only.

    Return fresh normalized fields suitable for persistence or a handoff.
    No filesystem or access-rights inference is performed.
    """
    if not isinstance(task, Mapping):
        raise ValueError("task must be an object")
    scope: dict[str, Any] = {}
    if "write_paths" in task:
        paths = _strings(task["write_paths"], "write_paths")
        normalized = [_path(path) for path in paths]
        if len(set(normalized)) != len(normalized):
            raise ValueError("write_paths must not contain equivalent duplicates")
        scope["write_paths"] = normalized
    for key in ("exclusive_resources", "access_need_ids"):
        if key in task:
            scope[key] = _strings(task[key], key)
    return scope


def _conflict(left: Mapping[str, Any], right: Mapping[str, Any]) -> str | None:
    if "write_paths" not in left or "write_paths" not in right:
        return "unknown write scope requires serial execution"
    resources = set(left.get("exclusive_resources", ())) & set(
        right.get("exclusive_resources", ())
    )
    if resources:
        return f"exclusive resource conflict: {sorted(resources)[0]}"
    for a in left["write_paths"]:
        for b in right["write_paths"]:
            folded_a, folded_b = a.casefold(), b.casefold()
            if (
                folded_a == folded_b
                or folded_a.startswith(folded_b + "/")
                or folded_b.startswith(folded_a + "/")
            ):
                return f"write path conflict: {a} / {b}"
    return None


def _unresolved(blocks: Any) -> bool:
    if blocks is None or blocks is False:
        return False
    if isinstance(blocks, list):
        return any(_unresolved(block) for block in blocks)
    if isinstance(blocks, Mapping):
        if "disposition" in blocks:
            return (blocks.get("severity", "critical") != "optional"
                    and blocks["disposition"] not in ("access_restored", "user_accepted_gap"))
        return not (
            blocks.get("resolved") is True
            or blocks.get("status") in ("resolved", "cleared", "closed")
            or blocks.get("state") in ("resolved", "cleared", "closed")
        )
    return bool(blocks)


def _access_records(status: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    access = status.get("access", {})
    if not isinstance(access, Mapping):
        raise ValueError("access must be an object")
    for blocks in (
        status.get("access_blocks"), access.get("blocks"),
        access.get("unresolved_blocks"),
    ):
        if _unresolved(blocks):
            raise ValueError("unresolved access block prevents dispatch")
    records: dict[str, Mapping[str, Any]] = {}
    for source in (
        access.get("needs", []), access.get("approvals", []),
        access.get("decisions", []), status.get("access_approvals", []),
        status.get("access_decisions", []),
    ):
        if isinstance(source, Mapping):
            items = [
                dict(value, id=key) if isinstance(value, Mapping) else
                {"id": key, "decision": value}
                for key, value in source.items()
            ]
        elif isinstance(source, list):
            items = source
        else:
            raise ValueError("access approvals must be an object or list")
        for item in items:
            if not isinstance(item, Mapping):
                raise ValueError("access approval must be an object")
            identifier = item.get("need_id", item.get("id"))
            if not isinstance(identifier, str) or not identifier:
                raise ValueError("access approval needs a nonempty id or need_id")
            previous = records.get(identifier)
            if previous is not None and previous.get("decision") is not None:
                if item.get("decision") not in (None, previous.get("decision")):
                    raise ValueError(f"conflicting access decisions for {identifier}")
            if item.get("decision") is not None or previous is None:
                records[identifier] = item
    return records


def _validate_access(scope: Mapping[str, Any], records: Mapping[str, Any]) -> None:
    for identifier in scope.get("access_need_ids", []):
        record = records.get(identifier, {})
        if (
            record.get("decision") != "use"
            or record.get("approved") is False
            or record.get("user_approved") is False
            or record.get("approved_by_user") is False
            or record.get("status") in ("declined", "blocked", "pending", "denied")
            or _unresolved(record.get("blocks"))
        ):
            raise ValueError(f"access need {identifier!r} lacks an approved use decision")


def dispatch_plan(status: Mapping[str, Any], max_workers: int = 4) -> dict[str, Any]:
    """Select compatible ready tasks in input order without changing any input.

    This is a plan, not an executor or an authorization bypass. The coordinator
    must apply its feature, seal, and topic-access gates immediately before use.
    Evidence declarations accept legacy booleans/lists as well as strings;
    coordinator task gates remain authoritative for real task creation.
    """
    if isinstance(max_workers, bool) or not isinstance(max_workers, int):
        raise ValueError("max_workers must be an integer from 1 through 8")
    if not 1 <= max_workers <= 8:
        raise ValueError("max_workers must be an integer from 1 through 8")
    if not isinstance(status, Mapping):
        raise ValueError("status must be an object")
    if "schema_version" in status and (
        isinstance(status["schema_version"], bool)
        or not isinstance(status["schema_version"], int)
        or status["schema_version"] != 2
    ):
        raise ValueError("dispatch requires schema version 2 status")
    if status.get("state") != "RESEARCH":
        raise ValueError("dispatch requires RESEARCH state")
    if status.get("hold"):
        raise ValueError("active project hold prevents dispatch")
    revision = status.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise ValueError("status revision must be a nonnegative integer")
    tasks = status.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("tasks must be a list")
    records = _access_records(status)
    by_id: dict[str, Mapping[str, Any]] = {}
    scopes: dict[str, dict[str, Any]] = {}
    dependencies: dict[str, list[str]] = {}
    for task in tasks:
        if not isinstance(task, Mapping):
            raise ValueError("every task must be an object")
        identifier = task.get("id")
        if not isinstance(identifier, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,80}", identifier) is None:
            raise ValueError("task id must match [A-Za-z0-9_-]{1,80}")
        if identifier in by_id:
            raise ValueError(f"duplicate task id: {identifier}")
        if not isinstance(task.get("status"), str) or task["status"] not in _STATUSES:
            raise ValueError(f"invalid task status for {identifier}")
        for field in ("objective", "owner"):
            if field in task and (
                not isinstance(task[field], str) or not task[field].strip()
            ):
                raise ValueError(f"{field} must be a nonempty string")
        attempts = task.get("attempts", 0)
        if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 0:
            raise ValueError("attempts must be a nonnegative integer")
        if "evidence_required" in task:
            evidence = task["evidence_required"]
            if isinstance(evidence, list):
                _strings(evidence, "evidence_required")
            elif not isinstance(evidence, (str, bool)):
                raise ValueError("evidence_required must be a boolean, string, or list")
        dependencies[identifier] = _strings(task.get("depends_on", []), "depends_on")
        scopes[identifier] = validate_task_scope(task)
        _validate_access(scopes[identifier], records)
        by_id[identifier] = task
    for identifier, deps in dependencies.items():
        if any(dep not in by_id for dep in deps):
            raise ValueError(f"unknown dependency for {identifier}")
    # Iterative traversal avoids recursion limits for otherwise valid large DAGs.
    indegree = {identifier: len(deps) for identifier, deps in dependencies.items()}
    children: dict[str, list[str]] = {identifier: [] for identifier in by_id}
    for identifier, deps in dependencies.items():
        for dep in deps:
            children[dep].append(identifier)
    ready = [identifier for identifier, degree in indegree.items() if not degree]
    visited = 0
    while ready:
        identifier = ready.pop()
        visited += 1
        for child in children[identifier]:
            indegree[child] -= 1
            if not indegree[child]:
                ready.append(child)
    if visited != len(by_id):
        raise ValueError("task dependency cycle")
    running = [identifier for identifier, task in by_id.items() if task["status"] == "running"]
    occupied = list(running)
    selected: list[dict[str, Any]] = []
    deferred: list[dict[str, str]] = []
    for identifier, task in by_id.items():
        task_status = task["status"]
        if task_status in _DONE | {"skipped", "running"}:
            continue
        reason = None
        if task_status == "failed":
            reason = "failed task requires an explicit retry; no automatic retry"
        elif task_status == "blocked":
            reason = "blocked task requires explicit resolution before dispatch"
        elif task.get("attempts", 0) >= 3:
            reason = "attempt cap of 3 reached; explicit amendment required, no automatic amendment"
        else:
            unmet = [
                dep for dep in dependencies[identifier]
                if by_id[dep]["status"] not in _DONE
            ]
            if unmet:
                reason = "dependencies not done: " + ", ".join(unmet)
            else:
                for other in occupied:
                    conflict = _conflict(scopes[identifier], scopes[other])
                    if conflict:
                        reason = f"{conflict} (task {other})"
                        break
                if reason is None and len(occupied) >= max_workers:
                    reason = "worker capacity exhausted"
        if reason is not None:
            deferred.append({"id": identifier, "reason": reason})
            continue
        handoff = {
            "schema_version": 2,
            "state_revision": revision,
            "id": identifier,
            "objective": task.get("objective", ""),
            "owner": task.get("owner", ""),
            "evidence_required": (
                list(task["evidence_required"])
                if isinstance(task.get("evidence_required"), list)
                else task.get("evidence_required", True)
            ),
            "depends_on": list(dependencies[identifier]),
            "status": "pending",
            "attempts": task.get("attempts", 0),
            **scopes[identifier],
            "instructions": _STOP_INSTRUCTION,
        }
        selected.append(handoff)
        occupied.append(identifier)
    return {
        "schema_version": 1,
        "state_revision": revision,
        "launch_performed": False,
        "max_workers": max_workers,
        "selected": selected,
        "deferred": deferred,
        "running_ids": running,
        "mode": "parallel" if len(occupied) > 1 else "serial" if occupied else "waiting",
        "limitations": [
            "Planning only: no agents are launched and no project state is written.",
            "Coordinator feature, seal, user-approval, and current access gates still apply.",
            "Unknown write scopes are serial; scopes are declarations, not filesystem sandboxes.",
            "Greedy input-order selection is deterministic, not a maximum parallel schedule.",
            "Actual session tools must launch and stop agents; missing capabilities are not enabled.",
            "Only observed executor/model metadata may be reported; roles are not model independence.",
            "run-workers fixture results remain synthetic and do not prove live agent execution.",
        ],
    }
