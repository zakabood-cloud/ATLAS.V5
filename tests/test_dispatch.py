"""Tests for the pure, dependency-safe handoff planner."""

import copy
import unittest

from atlas.dispatch import dispatch_plan, validate_task_scope


def task(identifier, paths=None, **values):
    result = {
        "id": identifier, "objective": f"Do {identifier}", "owner": "researcher",
        "evidence_required": True, "depends_on": [], "status": "pending",
        "attempts": 0,
    }
    if paths is not None:
        result["write_paths"] = paths
    result.update(values)
    return result


def status(*tasks, **values):
    result = {"revision": 7, "state": "RESEARCH", "hold": None, "tasks": list(tasks)}
    result.update(values)
    return result


class DispatchTests(unittest.TestCase):
    def selected_ids(self, plan):
        return [item["id"] for item in plan["selected"]]

    def test_disjoint_parallel_and_no_mutation(self):
        source = status(task("a", ["src/a.py"]), task("b", ["src/b.py"]))
        original = copy.deepcopy(source)
        plan = dispatch_plan(source)
        self.assertEqual(self.selected_ids(plan), ["a", "b"])
        self.assertEqual(plan["mode"], "parallel")
        self.assertFalse(plan["launch_performed"])
        self.assertEqual(plan["state_revision"], 7)
        self.assertEqual(source, original)
        plan["selected"][0]["write_paths"].append("different")
        self.assertEqual(source, original)

    def test_equal_and_ancestor_conflicts(self):
        for left, right in (("src/a", "src/a"), ("src", "src/a"), ("src/a", "src")):
            with self.subTest(left=left, right=right):
                plan = dispatch_plan(status(task("a", [left]), task("b", [right])))
                self.assertEqual(self.selected_ids(plan), ["a"])
                self.assertIn("write path conflict", plan["deferred"][0]["reason"])
                self.assertEqual(plan["mode"], "serial")

    def test_path_component_boundaries(self):
        plan = dispatch_plan(status(task("a", ["src/a"]), task("b", ["src/ab"])))
        self.assertEqual(self.selected_ids(plan), ["a", "b"])

    def test_case_alias_paths_conflict(self):
        for left, right in (
            ("a.py", "A.py"), ("Src", "src/a"), ("src/a", "SRC"),
            ("Straße/file", "STRASSE/FILE"),
        ):
            with self.subTest(left=left, right=right):
                plan = dispatch_plan(status(task("a", [left]), task("b", [right])))
                self.assertEqual(self.selected_ids(plan), ["a"])
                self.assertIn("write path conflict", plan["deferred"][0]["reason"])

    def test_running_consumes_capacity(self):
        source = status(
            task("running", ["one"], status="running"),
            task("a", ["two"]), task("b", ["three"]),
        )
        plan = dispatch_plan(source, 2)
        self.assertEqual(plan["running_ids"], ["running"])
        self.assertEqual(self.selected_ids(plan), ["a"])
        self.assertIn("capacity", plan["deferred"][0]["reason"])
        self.assertEqual(dispatch_plan(source, 1)["selected"], [])

    def test_running_scopes_conflict(self):
        plan = dispatch_plan(status(
            task("r", ["src"], status="running"),
            task("a", ["src/a"]), task("b", ["other"]),
        ))
        self.assertEqual(self.selected_ids(plan), ["b"])
        self.assertIn("task r", plan["deferred"][0]["reason"])

    def test_unknown_is_serial_in_both_orders_and_running(self):
        for tasks in (
            (task("a"), task("b", [])),
            (task("a", []), task("b")),
            (task("a", status="running"), task("b", ["src"])),
        ):
            plan = dispatch_plan(status(*tasks))
            self.assertEqual(len(plan["selected"]) + len(plan["running_ids"]), 1)
            self.assertIn("unknown write scope", plan["deferred"][0]["reason"])

    def test_read_only_parallel(self):
        plan = dispatch_plan(status(task("a", []), task("b", []), task("c", ["src"])))
        self.assertEqual(self.selected_ids(plan), ["a", "b", "c"])

    def test_exclusive_resources_selected_and_running(self):
        for first_status in ("pending", "running"):
            plan = dispatch_plan(status(
                task("a", [], status=first_status, exclusive_resources=["browser"]),
                task("b", [], exclusive_resources=["browser"]),
                task("c", [], exclusive_resources=["database"]),
            ))
            self.assertNotIn("b", self.selected_ids(plan))
            self.assertIn("c", self.selected_ids(plan))
            self.assertIn("exclusive resource", plan["deferred"][0]["reason"])

    def test_dependencies_done_only_and_failed_not_retried(self):
        plan = dispatch_plan(status(
            task("done", [], status="done"),
            task("failed", [], status="failed", attempts=1),
            task("skipped", [], status="skipped"),
            task("a", [], depends_on=["done"]),
            task("b", [], depends_on=["failed"]),
            task("c", [], depends_on=["a"]),
            task("d", [], depends_on=["skipped"]),
        ))
        self.assertEqual(self.selected_ids(plan), ["a"])
        self.assertEqual([item["id"] for item in plan["deferred"]], ["failed", "b", "c", "d"])
        self.assertIn("explicit retry", plan["deferred"][0]["reason"])

    def test_bad_ids_dependencies_and_cycles(self):
        cases = [
            status(task("a", []), task("a", [])),
            status(task("", [])),
            status(task(3, [])),
            status(task("a", [], depends_on=["unknown"])),
            status(task("a", [], depends_on=["a"])),
            status(task("a", [], depends_on=["b"]), task("b", [], depends_on=["a"])),
            status(task("a", [], depends_on="b")),
            status(task("a", [], depends_on=[1])),
            status(task("a", [], depends_on=["b", "b"]), task("b", [])),
        ]
        for source in cases:
            with self.subTest(source=source), self.assertRaises(ValueError):
                dispatch_plan(source)

    def test_task_ids_match_core_regex(self):
        for identifier in ("a.b", "a/b", "a b", "é", "a" * 81, "a\n"):
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                dispatch_plan(status(task(identifier, [])))
        self.assertEqual(
            self.selected_ids(dispatch_plan(status(task("A_z-09", [])))),
            ["A_z-09"],
        )
        self.assertEqual(
            self.selected_ids(dispatch_plan(status(task("a" * 80, [])))),
            ["a" * 80],
        )

    def test_blocked_task_is_deferred_without_rejecting_status(self):
        plan = dispatch_plan(status(
            task("blocked", [], status="blocked"),
            task("ready", []),
            task("dependent", [], depends_on=["blocked"]),
        ))
        self.assertEqual(self.selected_ids(plan), ["ready"])
        self.assertIn("explicit resolution", plan["deferred"][0]["reason"])
        self.assertIn("dependencies not done", plan["deferred"][1]["reason"])

    def test_attempt_cap_requires_amendment(self):
        plan = dispatch_plan(status(
            task("last", [], attempts=2),
            task("capped", [], attempts=3),
            task("over", [], attempts=4),
        ))
        self.assertEqual(self.selected_ids(plan), ["last"])
        for deferred in plan["deferred"]:
            self.assertIn("attempt cap of 3", deferred["reason"])
            self.assertIn("no automatic amendment", deferred["reason"])

    def test_hold_state_and_access_blocks_reject(self):
        for changes in (
            {"hold": {"reason": "blocked"}},
            {"state": "META"},
            {"access_blocks": [{"status": "open"}]},
            {"access": {"blocks": [{"resolved": False}]}},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                dispatch_plan(status(task("a", []), **changes))

    def test_historical_access_dispositions(self):
        for disposition in ("access_restored", "user_accepted_gap"):
            for changes in (
                {"access_blocks": [{"disposition": disposition}]},
                {"access": {"blocks": [{"disposition": disposition}]}},
            ):
                with self.subTest(changes=changes):
                    self.assertEqual(
                        self.selected_ids(dispatch_plan(status(task("a", []), **changes))),
                        ["a"],
                    )
        for disposition in ("unknown", "pending", "", None):
            with self.subTest(disposition=disposition), self.assertRaises(ValueError):
                dispatch_plan(status(
                    task("a", []), access_blocks=[{"disposition": disposition}],
                ))
        with self.assertRaises(ValueError):
            dispatch_plan(status(
                task("a", []),
                access_blocks=[{"disposition": "unknown", "resolved": True}],
            ))

    def test_access_needs_require_use_decision(self):
        scoped = task("a", [], access_need_ids=["api"])
        for approvals in (
            [], [{"id": "api", "decision": "decline"}],
            [{"id": "api", "decision": "use", "approved": False}],
            [{"id": "api", "decision": "use", "user_approved": False}],
            [{"id": "api", "decision": "use", "approved_by_user": False}],
            [{"id": "api", "decision": "use", "status": "pending"}],
            [{"id": "api", "approved": True}],
        ):
            with self.subTest(approvals=approvals), self.assertRaises(ValueError):
                dispatch_plan(status(scoped, access_approvals=approvals))
        plan = dispatch_plan(status(
            scoped, access={"decisions": [{"need_id": "api", "decision": "use"}]},
        ))
        self.assertEqual(self.selected_ids(plan), ["a"])

    def test_missing_access_scope_does_not_infer_rights(self):
        self.assertEqual(self.selected_ids(dispatch_plan(status(task("a", [])))), ["a"])

    def test_reserved_coordinator_paths(self):
        for path in (
            "state.sqlite3", "mandate.md", "protocol.json", "plan",
            "evidence.jsonl", "coverage.json", "search_log.md", "review.md",
            "synthesis.md", "deliverables/report.md", "enablement.json",
            "access_plan.json", "checkpoints/one.json", "01_mandate.md",
            ".atlas/state.sqlite3", "nested/state.sqlite3", ".git/index",
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_task_scope({"write_paths": [path]})

    def test_unsafe_and_malformed_scopes(self):
        for path in (
            "/absolute", "../parent", "src/../other", "src/./a", "src//a",
            ".", "", "a\\b", "C:drive", "src/*", "src/?.py", "src/[ab]",
            " leading", "trailing ", "src/name.", "src/\nname",
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_task_scope({"write_paths": [path]})
        for scope in (
            {"write_paths": None}, {"write_paths": "src"}, {"write_paths": [1]},
            {"write_paths": ["src", "src/"]},
            {"exclusive_resources": ["same", "same"]},
            {"exclusive_resources": [False]}, {"access_need_ids": "api"},
        ):
            with self.subTest(scope=scope), self.assertRaises(ValueError):
                validate_task_scope(scope)
        self.assertEqual(validate_task_scope({"write_paths": ["src/"]}), {"write_paths": ["src"]})
        self.assertEqual(validate_task_scope({}), {})

    def test_malformed_parameters(self):
        for workers in (True, False, 0, 9, -1, 1.5, "2", None):
            with self.subTest(workers=workers), self.assertRaises(ValueError):
                dispatch_plan(status(), workers)
        for source in (
            None, [], {}, status(revision=True), status(revision=-1),
            status(tasks={}), status(None), status(task("a", [], status="mystery")),
            status(task("a", [], status=[])),
            status(task("a", [], attempts=True)),
            status(task("a", [], objective=3)),
            status(task("a", [], objective=" ")),
            status(task("a", [], owner="")),
            status(schema_version=1), status(schema_version=True), status(schema_version=2.0),
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                dispatch_plan(source)

    def test_deterministic_bounded_greedy_selection(self):
        source = status(
            task("z", ["src"]), task("a", ["src/a"]),
            task("b", ["other"]), task("c", ["third"]),
        )
        expected = dispatch_plan(source, 2)
        self.assertEqual(self.selected_ids(expected), ["z", "b"])
        for _ in range(5):
            self.assertEqual(dispatch_plan(source, 2), expected)
        self.assertEqual(dispatch_plan(status())["mode"], "waiting")
        self.assertEqual(dispatch_plan(status(task("a", [], status="failed")))["mode"], "waiting")

    def test_handoff_is_bounded_and_truthful(self):
        source = task("a", [], extra_secret="not copied", model="not observed")
        handoff = dispatch_plan(status(source))["selected"][0]
        self.assertEqual(handoff["schema_version"], 2)
        self.assertEqual(handoff["state_revision"], 7)
        self.assertNotIn("extra_secret", handoff)
        self.assertNotIn("model", handoff)
        self.assertIn("stop sibling agents", handoff["instructions"])


if __name__ == "__main__":
    unittest.main()
