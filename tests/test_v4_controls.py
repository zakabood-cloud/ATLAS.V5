"""Observed local contracts, not live Copilot, MCP or semantic-quality validation."""
import asyncio
import contextlib
import copy
from datetime import timedelta
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from atlas.__main__ import main
from atlas.access import AccessBlocked, recommend_needs
from atlas.adapters import guarded_search
from atlas.archive import extract_checked
from atlas.contracts import validate_coverage
from atlas.decision import correlated_simulation
from atlas.demo import (access_fixture, complete, coverage_fixture, enablement_fixture,
                        evidence_fixture, handoff_fixture, prepare_research)
from atlas.enablement import feature_inventory
from atlas.evidence import validate_evidence
from atlas.dispatch import dispatch_plan
from atlas.intake import questions
from atlas.io import AtlasError, atomic_json, date, digest, file_hash, now, read_json
from atlas.project import Project
from atlas.project_archive import restore
from atlas.quant import run_analysis
from atlas.scheduler import run_ready
from atlas.verification import report_audit, review_packet, validate_review_receipts

REPO=Path(__file__).resolve().parents[1]
BASELINE_HASH="048b48ce4e5379af0b1e1502b24b7469086b331aa8eb0c291fc0fe3c50b14deb"


class Workspace(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)/"repo"; self.root.mkdir()
        shutil.copytree(REPO/"methods",self.root/"methods")

    def mandate(self):
        project=Project.create(self.root,"test","Synthetic feature review","general")
        for question in questions(self.root,"general"):
            project.answer(question["key"],"Synthetic input, not a user preference")
        project.mandate(acknowledged=True); project.advance("MANDATE")
        return project

    def receipt(self,project,need="local",resource="local:fixture",operation="read fixture"):
        stamp=now(); artifact=f"access-tests/{need}-replacement.json"
        atomic_json(project.path/artifact,{"ok":True,"resource":resource,"operation":operation,
                    "observed_at":stamp,"expires_at":(date(stamp)+timedelta(days=1)).isoformat(),
                    "limitations":"Synthetic test receipt only"})
        return artifact


class FeatureEnablement(Workspace):
    def test_explicit_stage_prevents_skipping_feature_review(self):
        project=self.mandate()
        with self.assertRaises(AtlasError): project.advance("META")
        project.advance("ENABLEMENT")
        with self.assertRaises(AtlasError): project.advance("META")
        enablement_fixture(project); access_fixture(project); project.advance("META")

    def test_inventory_is_not_a_platform_availability_claim(self):
        template=feature_inventory("question")
        self.assertTrue(all(f["status"]=="unknown" for f in template["features"]))
        self.assertTrue(all(not f["needed"] for f in template["features"]))
        self.assertIn("Offline",template["discovery_limits"])

    def test_enable_request_remains_blocked_until_verified_or_accepted(self):
        project=self.mandate(); project.advance("ENABLEMENT")
        plan=feature_inventory(project.status()["question"])
        plan["features"][0].update(status="disabled",needed=True,basis="Synthetic disabled subagents")
        atomic_json(project.path/"enablement.json",plan)
        decisions=[{"feature_id":f["id"],"decision":"enable" if f["needed"] else "not_needed",
                    "reason":"Synthetic user decision"} for f in plan["features"]]
        self.assertFalse(project.approve_enablement(decisions,"Synthetic explicit enable request")["ready"])
        with self.assertRaises(AtlasError): project._enablement(project.status())
        decisions[0]["decision"]="accept_limit"
        self.assertTrue(project.approve_enablement(decisions,"Synthetic authorization of single-agent limitation")["ready"])
        access_fixture(project); project.advance("META")

    def test_disabled_feature_cannot_be_claimed_usable_or_irrelevant(self):
        project=self.mandate(); project.advance("ENABLEMENT")
        plan=feature_inventory(project.status()["question"]); plan["features"][0]["needed"]=True
        atomic_json(project.path/"enablement.json",plan)
        decisions=[{"feature_id":f["id"],"decision":"not_needed","reason":"Synthetic"} for f in plan["features"]]
        for action in ("use","not_needed"):
            decisions[0]["decision"]=action
            with self.subTest(action=action),self.assertRaises(AtlasError):
                project.approve_enablement(decisions,"Synthetic")

    def test_enabled_receipt_is_rechecked_before_dispatch(self):
        project=prepare_research(self.root)
        (project.path/"feature-tests/execution.json").write_text("{}")
        with self.assertRaises(AtlasError): project.task("collect","running")
        with self.assertRaises(AtlasError): project.dispatch_context()

    def test_feature_plan_mutation_invalidates_approval(self):
        project=prepare_research(self.root)
        plan=read_json(project.path/"enablement.json")
        plan["features"][0]["needed"]=True
        atomic_json(project.path/"enablement.json",plan)
        with self.assertRaises(AtlasError): project.task("collect","running")

    def test_enablement_requires_every_standard_capability(self):
        project=self.mandate(); project.advance("ENABLEMENT")
        plan=feature_inventory(project.status()["question"]); plan["features"].pop()
        atomic_json(project.path/"enablement.json",plan)
        with self.assertRaises(AtlasError): project.approve_enablement([],"Synthetic")


class AccessControls(Workspace):
    def test_access_plan_mutation_and_missing_test_fail_closed(self):
        project=prepare_research(self.root)
        plan=read_json(project.path/"access_plan.json"); plan["needs"][0]["endpoint"]="local:other"
        atomic_json(project.path/"access_plan.json",plan)
        with self.assertRaises(AtlasError): project.task("collect","running")
        project.approve_access([{"need_id":"local","decision":"use","reason":"Synthetic approved change"}],"Synthetic")
        with self.assertRaises(AtlasError): project.task("collect","running")

    def test_any_block_is_durable_and_resume_needs_scope_and_authorization(self):
        project=prepare_research(self.root)
        project.block_access("https://source.example","read original","Synthetic 403","Loses original context")
        reloaded=Project(self.root,project.slug)
        self.assertEqual(reloaded.status()["hold"]["category"],"access")
        for action in (lambda:project.task("collect","running"),lambda:project.advance("VERIFY"),
                       lambda:project.resume("Generic reason"),lambda:project.hold("paused","Replace access hold"),
                       lambda:project.approve_access([{"need_id":"local","decision":"use","reason":"Synthetic"}],"Synthetic")):
            with self.assertRaises(AtlasError): action()
        project.resume("User accepts this named gap",authorization="Synthetic actual choice",scope="continue-with-gaps")
        self.assertEqual(project.status()["access_blocks"][0]["disposition"],"user_accepted_gap")
        project.task("collect","running")

    def test_accepting_gap_defers_failed_capability_instead_of_fake_test(self):
        project=prepare_research(self.root)
        project.block_access("local:fixture","read fixture","Synthetic access error","Cannot read fixture","local")
        project.resume("Proceed without fixture",authorization="Synthetic named gap acceptance",scope="continue-with-gaps")
        self.assertEqual(project.status()["access"]["decisions"][0]["decision"],"defer")
        self.assertNotIn("local",project.status()["access"]["tests"])
        with self.assertRaises(AtlasError): project.require_access("local","local:fixture","read fixture")

    def test_gap_continuation_does_not_dispatch_task_requiring_deferred_access(self):
        project=prepare_research(self.root)
        project.reopen("ORCHESTRATE","Synthetic declared task access")
        plan=project.artifact("plan.json"); plan["tasks"][0]["access_need_ids"]=["local"]
        atomic_json(project.path/"plan.json",plan); project.advance("RESEARCH")
        project.block_access("local:fixture","read fixture","Synthetic failure","Gap","local")
        project.resume("Proceed with named gap",authorization="Synthetic user choice",scope="continue-with-gaps")
        with self.assertRaisesRegex(AtlasError,"no longer approved"): project.task("collect","running")

    def test_retry_keeps_research_held_and_cannot_dispatch_twice(self):
        project=prepare_research(self.root)
        project.block_access("local:fixture","read fixture","Synthetic timeout","Missing context","local")
        project.resume("Retry just this access",authorization="Synthetic one retry",scope="retry")
        with self.assertRaises(AtlasError): project.task("collect","running")
        with self.assertRaises(AtlasError): project.require_access("local","local:fixture","another operation",True)
        project.require_access("local","local:fixture","read fixture",True)
        with self.assertRaises(AtlasError): project.require_access("local","local:fixture","read fixture",True)
        project.record_access_test("local",self.receipt(project))
        self.assertIsNone(project.status()["hold"])
        self.assertEqual(project.status()["access_blocks"][0]["disposition"],"access_restored")
        project.task("collect","running")

    def test_unsuccessful_retry_creates_new_hold_without_implicit_retry(self):
        project=prepare_research(self.root)
        project.block_access("local:fixture","read fixture","First failure","Gap","local")
        project.resume("Retry",authorization="Synthetic retry",scope="retry")
        project.require_access("local","local:fixture","read fixture",True)
        project.block_access("local:fixture","read fixture","Still unavailable","Gap","local")
        self.assertEqual(len(project.status()["access_blocks"]),2)
        with self.assertRaises(AtlasError): project.require_access("local","local:fixture","read fixture",True)

    def test_old_receipt_cannot_clear_new_retry_hold(self):
        project=prepare_research(self.root)
        old="access-tests/local.json"
        project.block_access("local:fixture","read fixture","Synthetic failure","Gap","local")
        project.resume("Retry",authorization="Synthetic retry",scope="retry")
        with self.assertRaises(AtlasError): project.record_access_test("local",old)
        self.assertIsNotNone(project.status()["hold"])

    def test_failed_or_changed_test_does_not_count_as_available(self):
        project=prepare_research(self.root)
        artifact=self.receipt(project)
        receipt=read_json(project.path/artifact); receipt["ok"]=False
        atomic_json(project.path/artifact,receipt)
        with self.assertRaises(AtlasError): project.record_access_test("local",artifact)
        (project.path/"access-tests/local.json").write_text("{}")
        with self.assertRaises(AtlasError): project.task("collect","running")

    def test_mcp_requires_verified_publisher_and_paid_approval(self):
        project=prepare_research(self.root)
        plan=read_json(project.path/"access_plan.json")
        need=plan["needs"][0]; need.update(kind="mcp",paid=True,endpoint="https://service.example/mcp")
        atomic_json(project.path/"access_plan.json",plan)
        decisions=[{"need_id":"local","decision":"use","reason":"Synthetic"}]
        with self.assertRaises(AtlasError): project.approve_access(decisions,"Synthetic")
        need.update(publisher="Synthetic publisher",verification_url="https://publisher.example/docs",publisher_verified_at=now())
        atomic_json(project.path/"access_plan.json",plan)
        with self.assertRaises(AtlasError): project.approve_access(decisions,"Synthetic")
        decisions[0]["paid_approved"]=True
        project.approve_access(decisions,"Synthetic separate paid approval")
        self.assertEqual(project.status()["access"]["tests"],{})

    def test_guarded_metadata_failure_holds_project_without_retry(self):
        project=prepare_research(self.root)
        project.reopen("ORCHESTRATE","Synthetic metadata probe")
        plan=read_json(project.path/"access_plan.json")
        plan["needs"][0]["endpoint"]="https://api.openalex.org/works"
        atomic_json(project.path/"access_plan.json",plan)
        project.approve_access([{"need_id":"local","decision":"use","reason":"Synthetic metadata test"}],"Synthetic")
        with patch("atlas.adapters.http_json",side_effect=AtlasError("Synthetic 403")) as request:
            with self.assertRaises(AccessBlocked): guarded_search(project,"local","openalex","fixture",limit=1,probe=True)
            self.assertEqual(request.call_count,1)
            with self.assertRaises(AtlasError): guarded_search(project,"local","openalex","fixture",limit=1,probe=True)
            self.assertEqual(request.call_count,1)
        self.assertEqual(project.status()["hold"]["category"],"access")
        receipt=project.status()["retrieval_receipts"][0]
        self.assertFalse(read_json(project.path/receipt["artifact"])["ok"])

    def test_scholarly_research_is_stage_gated_and_probe_explicitly_bounded(self):
        project=prepare_research(self.root)
        project.reopen("ORCHESTRATE","Synthetic preparation")
        with patch("atlas.adapters.http_json") as request:
            with self.assertRaises(AtlasError): guarded_search(project,"local","openalex","fixture")
            with self.assertRaises(AtlasError): guarded_search(project,"local","openalex","fixture",probe=True)
            request.assert_not_called()

    def test_successful_research_retains_query_and_result_receipt(self):
        project=prepare_research(self.root)
        project.reopen("ENABLEMENT","Synthetic provider preparation")
        access=project.artifact("access_plan.json")
        access["needs"][0]["endpoint"]="https://api.openalex.org/works"
        atomic_json(project.path/"access_plan.json",access)
        project.approve_access([{"need_id":"local","decision":"use","reason":"Synthetic"}],"Synthetic")
        receipt=self.receipt(project,resource="https://api.openalex.org/works",operation="scholarly-search")
        project.record_access_test("local",receipt)
        project.advance("META")
        protocol=project.artifact("protocol.json")
        protocol["search_plan"][0]["query"]="fixture"
        atomic_json(project.path/"protocol.json",protocol)
        for state in ("READINESS","ORCHESTRATE","RESEARCH"): project.advance(state)
        with patch("atlas.adapters.http_json",return_value={"results":[]}):
            result=guarded_search(project,"local","openalex","fixture",plan_id="P1")
        saved=read_json(project.path/result["retrieval_artifact"])
        self.assertEqual(saved["query"],"fixture")
        self.assertEqual(saved["result"]["items"],[])
        self.assertEqual(project.status()["retrieval_receipts"][0]["purpose"],"research")

    def test_offline_needs_are_not_claimed_server_connections(self):
        plan=recommend_needs("Synthetic question","science")
        self.assertTrue(plan["candidate_capabilities"])
        self.assertIn("not exhaustive",plan["limitations"])
        self.assertNotIn("connected",plan.keys())

    def test_external_tool_retry_requires_current_authorization_and_exact_block(self):
        project=prepare_research(self.root)
        project.block_access("copilot:subagents","launch specialist","Synthetic cancellation","Missing specialist output")
        stamp=now(); artifact="access-tests/external.json"
        atomic_json(project.path/artifact,{"ok":True,"resource":"copilot:subagents","operation":"launch specialist",
                    "observed_at":stamp,"method":"Synthetic successful tool result","limitations":"No live platform validation"})
        with self.assertRaises(AtlasError): project.resolve_external_access("B0001",artifact)
        project.resume("Retry external tool",authorization="Synthetic explicit retry",scope="retry")
        with self.assertRaises(AtlasError): project.resolve_external_access("B0001",artifact)
        receipt=read_json(project.path/artifact); receipt["observed_at"]=now()
        atomic_json(project.path/artifact,receipt)
        project.resolve_external_access("B0001",artifact)
        self.assertIsNone(project.status()["hold"])
        self.assertEqual(project.status()["access_blocks"][0]["disposition"],"access_restored")

    def test_cli_structured_failure_returns_nonzero(self):
        project=prepare_research(self.root)
        with contextlib.redirect_stdout(io.StringIO()):
            code=main(["--root",str(self.root),"access-block",project.slug,"--resource","local:fixture",
                       "--operation","read fixture","--reason","Synthetic failure","--quality-impact","Gap","--need-id","local"])
        self.assertEqual(code,1)


class EvidenceAndDelivery(Workspace):
    def setUp(self):
        super().setUp()
        self.data=evidence_fixture(self.root,strict=True)

    def codes(self):
        return {r["code"] for r in validate_evidence(self.data,self.root)["errors"]}

    def test_changed_claim_invalidates_old_review(self):
        self.assertTrue(validate_evidence(self.data,self.root)["ok"])
        self.data["claims"][0]["text"]="Different claim"
        self.assertIn("review_binding",self.codes())

    def test_new_snapshot_hash_does_not_rebind_old_review(self):
        path=self.root/"sources/fixture.txt"
        path.write_text(path.read_text()+"Different surrounding context")
        self.data["sources"][0]["sha256"]=file_hash(path)
        self.assertIn("review_binding",self.codes())

    def test_structured_scope_and_uncertainty_are_required(self):
        self.data["claims"][0].pop("scope")
        self.data["claims"][0]["uncertainty"]={"level":.95}
        self.assertTrue({"claim_scope","uncertainty"}<=self.codes())

    def test_review_packet_rejects_modified_registered_bytes(self):
        (self.root/"sources/fixture.txt").write_text("changed")
        with self.assertRaises(AtlasError): review_packet(self.data,self.root,"C1")

    def test_review_packet_includes_late_quote_and_explicit_omissions(self):
        path=self.root/"sources/fixture.txt"
        path.write_text("x"*30000+"\nThe observed count is ten.\n"+"y"*30000)
        self.data["sources"][0]["sha256"]=file_hash(path)
        packet=review_packet(self.data,self.root,"C1")
        source=packet["sources"][0]
        self.assertIn("The observed count is ten.",source["content_context"])
        self.assertTrue(source["truncated"])
        self.assertTrue(source["omitted_ranges"])
        self.assertGreater(source["segments"][0]["start"],0)
        self.assertLessEqual(len(source["content_context"]),15000)

    def test_uncited_bullets_tables_quotes_and_missing_material_claim_fail(self):
        for text in ("- The observed count is ten in this test fixture.",
                     "| Count | 10 |","> The observed count is ten in this test fixture.",
                     "No material marker included."):
            with self.subTest(text=text): self.assertFalse(report_audit(text,self.data)["ok"])
        self.assertTrue(report_audit("Fixture count ten. [[claim:C1]]",self.data)["ok"])

    def test_stale_review_cannot_support_report(self):
        self.data["claims"][0]["text"]="Unreviewed revision"
        self.assertFalse(report_audit("Finding [[claim:C1]]",self.data)["ok"])

    def test_delivery_gate_runs_report_audit_not_only_hashes(self):
        project=complete(self.root)
        project.reopen("DELIVER","Synthetic missed citation")
        path=project.path/"outputs/demo-report.md"
        path.write_text("- The observed count is ten in this test fixture.\n")
        manifest=read_json(project.path/"deliverables.json")
        manifest["files"][0]["sha256"]=file_hash(path)
        atomic_json(project.path/"deliverables.json",manifest)
        with self.assertRaisesRegex(AtlasError,"citation audit"): project.advance("MEMORY")

    def test_final_review_binds_exact_evidence(self):
        project=complete(self.root); project.reopen("VERIFY","Synthetic changed evidence")
        evidence=read_json(project.path/"evidence.json")
        evidence["claims"][0]["text"]+=" Changed."
        evidence["assessments"][0]["claim_sha256"]=digest(evidence["claims"][0])
        atomic_json(project.path/"evidence.json",evidence)
        with self.assertRaisesRegex(AtlasError,"bound to current evidence"): project.advance("SYNTHESIS")

    def test_source_lineage_must_resolve(self):
        self.data["sources"][0]["derived_from"]=["missing"]
        self.assertIn("lineage",self.codes())

    def test_review_receipt_must_match_exact_review_artifact(self):
        claim=self.data["claims"][0]; source=self.data["sources"][0]
        row={"claim_id":"C1","reviewer":"another reviewer","model_or_human":"not exposed",
             "verdict":"supports","rationale":"Synthetic fixture judgment",
             "claim_sha256":digest(claim),"source_hashes":{"S1":source["sha256"]}}
        path=self.root/"review-receipt.json"; atomic_json(path,row)
        receipt=dict(row,artifact=path.name,sha256=file_hash(path))
        self.assertTrue(validate_review_receipts(self.root,self.data,[receipt])["ok"])
        receipt["rationale"]="Forged replacement"
        self.assertFalse(validate_review_receipts(self.root,self.data,[receipt])["ok"])


class CoverageAndTasks(Workspace):
    def test_verify_requires_every_recorded_research_request_in_search_log(self):
        project=complete(self.root)
        project.reopen("RESEARCH","Synthetic omitted retrieval log")
        artifact="retrieval/synthetic.json"
        atomic_json(project.path/artifact,{"id":"synthetic-retrieval","purpose":"research","plan_id":"P1",
                    "need_id":"local","query":"Synthetic fixture","resource":"local:fixture","at":now(),
                    "ok":True,"result":{"items":[]}})
        project.record_search(artifact)
        with self.assertRaisesRegex(AtlasError,"omits a recorded research retrieval"): project.advance("VERIFY")
        log=project.artifact("search_log.json")
        log["queries"][0]["retrieval_artifact"]=artifact
        atomic_json(project.path/"search_log.json",log)
        project.advance("VERIFY")

    def test_parallel_planning_requires_observed_enabled_subagents(self):
        project=prepare_research(self.root)
        with self.assertRaisesRegex(AtlasError,"enabled subagents"): project.dispatch_context(4)
        self.assertEqual(project.dispatch_context(1)["state"],"RESEARCH")

    def test_approved_observed_subagents_allow_disjoint_parallel_plan_only(self):
        project=prepare_research(self.root)
        project.reopen("ENABLEMENT","Synthetic observed subagent capability")
        plan=project.artifact("enablement.json")
        feature=next(f for f in plan["features"] if f["id"]=="subagents")
        stamp=now(); artifact="feature-tests/subagents.json"
        atomic_json(project.path/artifact,{"feature_id":"subagents","status":"enabled","observed_at":stamp,
                    "expires_at":(date(stamp)+timedelta(days=1)).isoformat(),
                    "method":"Synthetic fixture only","limitations":"No actual model or launch"})
        feature.update(needed=True,status="enabled",basis="Synthetic observation",
                       verification={"artifact":artifact,"sha256":file_hash(project.path/artifact)})
        atomic_json(project.path/"enablement.json",plan)
        decisions=copy.deepcopy(project.status()["enablement"]["decisions"])
        next(d for d in decisions if d["feature_id"]=="subagents")["decision"]="use"
        project.approve_enablement(decisions,"Synthetic explicit subagent approval")
        for state in ("META","READINESS","ORCHESTRATE"): project.advance(state)
        task_plan=project.artifact("plan.json")
        task_plan["tasks"][0]["write_paths"]=["branches/first.json"]
        task_plan["tasks"].append(dict(task_plan["tasks"][0],id="second",write_paths=["branches/second.json"]))
        atomic_json(project.path/"plan.json",task_plan); project.advance("RESEARCH")
        result=dispatch_plan(project.dispatch_context(2),2)
        self.assertEqual(len(result["selected"]),2)
        self.assertFalse(result["launch_performed"])
        self.assertEqual({t["status"] for t in project.status()["tasks"]},{"pending"})

    def test_coverage_cannot_claim_unretrieved_source(self):
        project=prepare_research(self.root); evidence=evidence_fixture(project.path,strict=True)
        coverage_fixture(project)
        coverage=read_json(project.path/"coverage.json"); log=read_json(project.path/"search_log.json")
        self.assertEqual(validate_coverage(project.artifact("protocol.json"),coverage,log,evidence,[])["queries"],2)
        log["queries"][0].update(included_ids=[],retrieved_ids=[])
        with self.assertRaises(AtlasError):
            validate_coverage(project.artifact("protocol.json"),coverage,log,evidence,[])

    def test_exclusion_accounting_and_independent_origin_threshold(self):
        project=prepare_research(self.root); evidence=evidence_fixture(project.path,strict=True)
        coverage_fixture(project)
        coverage=project.artifact("coverage.json"); log=project.artifact("search_log.json")
        log["queries"][0]["retrieved_ids"].append("excluded")
        with self.assertRaises(AtlasError):
            validate_coverage(project.artifact("protocol.json"),coverage,log,evidence,[])
        log["queries"][0]["exclusions"]=[{"id":"excluded","reason":"Synthetic irrelevant result"}]
        protocol=project.artifact("protocol.json")
        protocol["stopping_criteria"]["min_independent_origins"]=2
        with self.assertRaises(AtlasError): validate_coverage(protocol,coverage,log,evidence,[])

    def test_task_requires_real_handoff_shape_and_failed_retries_are_explicit(self):
        project=prepare_research(self.root); project.task("collect","running")
        path=project.path/"branches/handoff.json"; atomic_json(path,{"task_id":"collect"})
        with self.assertRaises(AtlasError): project.task("collect","done","branches/handoff.json")
        project.interrupt_task("collect","Synthetic interrupted process")
        self.assertEqual(project.status()["tasks"][0]["failure_reason"],"Synthetic interrupted process")
        with self.assertRaises(AtlasError): project.task("collect","running")
        project.task("collect","pending"); project.task("collect","running")
        atomic_json(path,handoff_fixture("collect")); project.task("collect","done","branches/handoff.json")

    def test_blocked_task_holds_whole_project_and_resume_is_explicit(self):
        project=prepare_research(self.root)
        project.task("collect","blocked",reason="Synthetic missing resource")
        self.assertIsNotNone(project.status()["hold"])
        with self.assertRaises(AtlasError): project.task("collect","pending")
        project.resume("Synthetic resolution",authorization="Synthetic explicit instruction")
        project.task("collect","pending")

    def test_worker_access_block_cancels_siblings_and_persists_failure(self):
        project=prepare_research(self.root); project.reopen("ORCHESTRATE","Synthetic parallel tasks")
        plan=project.artifact("plan.json")
        plan["tasks"].append(dict(plan["tasks"][0],id="second"))
        atomic_json(project.path/"plan.json",plan); project.advance("RESEARCH")
        class Worker:
            async def execute(self,task,context):
                if task["id"]=="collect":
                    await asyncio.sleep(.01)
                    raise AccessBlocked("local:fixture","read fixture","Synthetic access denial","Gap","local")
                await asyncio.sleep(10)
                return handoff_fixture(task["id"])
        result=asyncio.run(run_ready(project,Worker(),2,10,.5))
        self.assertFalse(result["ok"])
        self.assertEqual(project.status()["hold"]["category"],"access")
        self.assertEqual({t["status"] for t in project.status()["tasks"]},{"failed"})
        self.assertEqual(result["completed"],[])

    def test_worker_timeout_is_not_marked_success(self):
        project=prepare_research(self.root)
        class Worker:
            async def execute(self,task,context):
                await asyncio.sleep(1)
        result=asyncio.run(run_ready(project,Worker(),timeout_per_task=.01))
        self.assertFalse(result["ok"])
        self.assertEqual(project.status()["tasks"][0]["status"],"failed")
        self.assertIn("Timeout",project.status()["tasks"][0]["failure_reason"])
        self.assertEqual(project.status()["hold"]["category"],"access")


class Compatibility(Workspace):
    def test_checkpoint_restore_never_silently_unpauses_work(self):
        project=prepare_research(self.root)
        checkpoint=project.checkpoint()
        project.block_access("local:fixture","read fixture","Synthetic later failure","Gap","local")
        restored=Project.restore(self.root,project.slug,checkpoint)
        self.assertIsNotNone(restored["hold"])
        with self.assertRaises(AtlasError): project.task("collect","running")
        with self.assertRaises(AtlasError): project.resume("Silent continuation")

    def test_legacy_calculation_output_is_reproduced_without_silent_relabeling(self):
        spec={"kind":"ecommerce_economics","units":"USD","assumptions":["Synthetic assumptions"],
              "price_gross":40,"orders":5}
        legacy=run_analysis(spec,engine="atlas.quant/3.0.0")
        modern=run_analysis(spec)
        self.assertEqual(legacy["output"],modern["output"])
        self.assertEqual(legacy["output_units"]["/output/contribution_per_order"],"USD")
        self.assertEqual(modern["output_units"]["/output/contribution_per_order"],"USD per order")
        self.assertEqual(modern["output_units"]["/output/period_operating_profit"],"USD per period")
        with self.assertRaises(AtlasError): run_analysis(spec,engine="unknown")

    def test_reversed_normal_clipping_is_rejected(self):
        spec={"seed":1,"draws":100,"variables":{"x":{"distribution":"normal","mean":0,"sd":1,"low":10,"high":1}},
              "coefficients":{"x":1}}
        with self.assertRaisesRegex(AtlasError,"clipping bounds"): correlated_simulation(spec)

    def test_real_supplied_v1_project_migrates_with_full_restorable_backup(self):
        archive=REPO/"reference/ATLAS_Copilot_v3_baseline.zip"
        self.assertEqual(file_hash(archive),BASELINE_HASH)
        scratch=self.root.parent/"baseline"
        with zipfile.ZipFile(archive) as source: extract_checked(source,scratch)
        candidates=list(scratch.rglob("atlas/__init__.py"))
        self.assertEqual(len(candidates),1)
        baseline=candidates[0].parent.parent
        code=("from pathlib import Path; from atlas.demo import complete; "
              "p=complete(Path('"+str(self.root)+"'),'legacy'); print(p.status()['schema_version'])")
        process=subprocess.run([sys.executable,"-c",code],cwd=baseline,text=True,capture_output=True,timeout=30)
        self.assertEqual(process.returncode,0,process.stderr)
        project=Project(self.root,"legacy")
        self.assertTrue(project.status()["legacy_contract"])
        original={p.relative_to(project.path).as_posix():file_hash(p) for p in project.path.rglob("*")
                  if p.is_file() and p.name!="state.sqlite3"}
        destination=self.root.parent/"migration-backup.zip"
        with self.assertRaises(AtlasError): project.migrate(destination,"Synthetic user",quiesced=False)
        result=project.migrate(destination,"Synthetic explicit migration authorization",quiesced=True)
        self.assertEqual(result["schema_version"],2)
        self.assertEqual(result["state"],"MANDATE")
        for rel,sha in original.items(): self.assertEqual(file_hash(project.path/rel),sha)
        restored=self.root/"projects/restored"
        restore(destination,restored)
        old=Project(self.root,"restored")
        self.assertEqual(old.status()["schema_version"],1)
        self.assertEqual(old.status()["state"],"COMPLETE")
        with self.assertRaises(AtlasError): project.advance("META")
        project.advance("ENABLEMENT"); enablement_fixture(project); access_fixture(project); project.advance("META")


if __name__=="__main__":
    unittest.main()
