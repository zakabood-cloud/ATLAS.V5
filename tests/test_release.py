"""Regression tests for release boundaries, not autonomous-research performance."""
import contextlib
import copy
import io
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from atlas.__main__ import main, READY
from atlas.demo import complete, prepare_research, evidence_fixture
from atlas.evidence import validate_evidence
from atlas.io import AtlasError, atomic_json, file_hash, read_json, digest
from atlas.project import Project
from atlas.quant import run_analysis
from atlas.structure import check
from test_engine import Workspace, REPO


class NumericalProvenance(Workspace):
    def setUp(self):
        super().setUp(); self.data=evidence_fixture(self.root)
        spec={"kind":"unit_economics","units":"USD","assumptions":["Synthetic; no empirical market estimate"],"price_gross":"120","vat_rate":"0.2","landed_cost":"75"}
        self.artifact=self.root/"calc.json"; self.item={"input":spec,"result":run_analysis(spec)}
        atomic_json(self.artifact,self.item)
        self.data["claims"][0].update(kind="numeric",numeric_value="25",units="USD per order")
        self.data["calculations"]=[{"path":"calc.json","sha256":file_hash(self.artifact),"claim_ids":["C1"],"bindings":[{"claim_id":"C1","pointer":"/output/contribution_per_order","units":"USD per order"}]}]
    def codes(self): return {e["code"] for e in validate_evidence(self.data,self.root)["errors"]}
    def test_calculation_claim_binding(self): self.assertTrue(validate_evidence(self.data,self.root)["ok"])
    def test_correct_calculation_wrong_claim(self):
        self.data["claims"][0]["numeric_value"]="250"; self.assertIn("calculation",self.codes())
    def test_same_forged_units_rejected(self):
        self.data["claims"][0]["units"]="AED per order"; self.data["calculations"][0]["bindings"][0]["units"]="AED per order"
        self.assertIn("calculation",self.codes())
    def test_unbound_calculation_not_verification(self):
        self.data["calculations"][0]["bindings"]=[]; self.assertIn("numeric_artifact",self.codes())
    def test_altered_calculation_with_new_hash(self):
        self.item["result"]["output"]["contribution_per_order"]="250"; atomic_json(self.artifact,self.item)
        self.data["calculations"][0]["sha256"]=file_hash(self.artifact)
        self.assertIn("calculation",self.codes())
    def test_bad_pointer_rejected(self):
        self.data["calculations"][0]["bindings"][0]["pointer"]="/output/absent"; self.assertIn("calculation",self.codes())
    def test_reported_statistic_still_requires_support(self):
        self.data["claims"][0]["reported_statistic"]=True; self.data["calculations"]=[]; self.data["assessments"]=[]
        self.assertIn("unreviewed_claim",self.codes())


class IntegrityRegressions(Workspace):
    def test_hold_blocks_work_and_persists(self):
        p=prepare_research(self.root); p.hold("paused","User requested pause")
        self.assertEqual(Project(self.root,"demo").status()["hold"]["kind"],"paused")
        with self.assertRaises(AtlasError): p.task("collect","running")
        p.resume("User requested continuation",authorization="Synthetic user requests continuation"); p.task("collect","running")
    def test_aborted_project_requires_explicit_resume(self):
        p=self.new(); p.hold("aborted","User cancelled")
        with self.assertRaises(AtlasError): p.answer("objective","Continue silently")
    def test_evaluation_criteria_required_before_research(self):
        p=prepare_research(self.root); p.reopen("META","Define evaluation")
        protocol=read_json(p.path/"protocol.json"); del protocol["evaluation_criteria"]; atomic_json(p.path/"protocol.json",protocol)
        with self.assertRaises(AtlasError): p.advance("READINESS")

    def test_cost_cannot_use_altered_mandate(self):
        p=prepare_research(self.root); m=read_json(p.path/"mandate.json"); m["paid_budget"]="1000"; atomic_json(p.path/"mandate.json",m)
        with self.assertRaises(AtlasError): p.record_cost("x","1","Unauthorized edited budget")
    def test_cost_before_mandate(self):
        with self.assertRaises(AtlasError): self.new().record_cost("x","0","Before intake")
    def test_task_ledger_tamper_detected(self):
        p=prepare_research(self.root)
        with sqlite3.connect(p.db) as con: con.execute("DELETE FROM tasks")
        with self.assertRaises(AtlasError): p.status()
    def test_cost_ledger_tamper_detected(self):
        p=prepare_research(self.root); p.record_cost("x","0","local")
        with sqlite3.connect(p.db) as con: con.execute("UPDATE costs SET amount='99'")
        with self.assertRaises(AtlasError): p.status()
    def test_evaluation_cannot_change_predefined_criteria(self):
        p=complete(self.root); p.reopen("EVALUATE","Change evaluation")
        e=read_json(p.path/"evaluation.json"); e["criteria"]=["Easy replacement criterion"]; atomic_json(p.path/"evaluation.json",e)
        with self.assertRaises(AtlasError): p.advance("COMPLETE")
    def test_review_must_explicitly_clear_critical_failures(self):
        p=complete(self.root); p.reopen("VERIFY","Review update")
        review=read_json(p.path/"review.json"); del review["unresolved_critical"]; atomic_json(p.path/"review.json",review)
        with self.assertRaises(AtlasError): p.advance("SYNTHESIS")
    def test_stale_source_needs_explicit_resolution(self):
        p=complete(self.root); p.reopen("VERIFY","Freshness reassessment")
        evidence=read_json(p.path/"evidence.json"); evidence["sources"][0]["expires_at"]="2000-01-01"; atomic_json(p.path/"evidence.json",evidence)
        with self.assertRaises(AtlasError): p.advance("SYNTHESIS")
        review=read_json(p.path/"review.json"); review["freshness_resolution"]="Historical fixture only; does not substantiate a current claim"
        review["evidence_sha256"]=digest(evidence); atomic_json(p.path/"review.json",review)
        p.advance("SYNTHESIS")
    def test_unavailable_api_without_fallback_blocks(self):
        p=prepare_research(self.root); p.reopen("READINESS","Lost access")
        r=read_json(p.path/"readiness.json"); r["checks"]["tools"]={"status":"failed","basis":"API unavailable"}; atomic_json(p.path/"readiness.json",r)
        with self.assertRaises(AtlasError): p.advance("ORCHESTRATE")
    def test_limited_tool_needs_fallback(self):
        p=prepare_research(self.root); p.reopen("READINESS","Lost access")
        r=read_json(p.path/"readiness.json"); del r["checks"]["tools"]["fallback"]; atomic_json(p.path/"readiness.json",r)
        with self.assertRaises(AtlasError): p.advance("ORCHESTRATE")
    def test_dependencies_block_early_task(self):
        p=prepare_research(self.root); p.reopen("ORCHESTRATE","Two tasks")
        plan=read_json(p.path/"plan.json"); plan["tasks"].append({"id":"next","objective":"Depends on collection","owner":"worker","evidence_required":"output","depends_on":["collect"]}); atomic_json(p.path/"plan.json",plan); p.advance("RESEARCH")
        with self.assertRaises(AtlasError): p.task("next","running")
    def test_nested_schema_failures_are_results(self):
        for field,value in [("kind",[]),("source_ids",None),("material",{})]:
            d=evidence_fixture(self.root); d["claims"][0][field]=value
            self.assertFalse(validate_evidence(d,self.root)["ok"])
    def test_reopen_does_not_hide_altered_task_output(self):
        p=complete(self.root); p.reopen("RESEARCH","Recheck collection")
        (p.path/"branches/collect.json").write_text("Changed after task completion")
        with self.assertRaises(AtlasError): p.advance("VERIFY")
    def test_all_eight_domain_plans_enter_research(self):
        for domain in ["amazon","commerce","markets","opportunity","finance","science","technology","general"]:
            with self.subTest(domain=domain):
                p=prepare_research(self.root,domain,domain); self.assertEqual(p.status()["state"],"RESEARCH")


class ReleaseStructure(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)/"ATLAS"
        from scripts.release_common import release_files
        for source in release_files(REPO):
            relative=source.relative_to(REPO)
            if relative.parts[0]=="projects": continue
            target=self.root/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target)
    def tearDown(self): self.tmp.cleanup()
    def test_shipped_structure(self): self.assertTrue(check(self.root)["ok"],check(self.root)["errors"])
    def test_initialization_exact_message_and_stop(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out): code=main(["--root",str(self.root),"init"])
        self.assertEqual(code,0); self.assertTrue(out.getvalue().endswith(READY+"\n"))
        self.assertFalse((self.root/"projects").exists()); self.assertIn('"state": "AWAITING_INQUIRY"',out.getvalue())
    def test_failed_initialization_has_no_ready(self):
        (self.root/"AGENTS.md").unlink(); out=io.StringIO()
        with contextlib.redirect_stdout(out): code=main(["--root",str(self.root),"init"])
        self.assertNotEqual(code,0); self.assertNotIn(READY,out.getvalue())
    def test_bad_python_detected(self):
        (self.root/"atlas/quant.py").write_text("def broken(:\n")
        self.assertFalse(check(self.root)["ok"])
    def test_invalid_frontmatter_detected(self):
        p=self.root/".github/agents/domain-researcher.agent.md"; p.write_text("---\nname: [broken\ndescription: x\n---\nbody\n")
        self.assertFalse(check(self.root)["ok"])
    def test_missing_local_link_detected(self):
        p=self.root/"README.md"; p.write_text(p.read_text()+"\n[broken](missing.md)\n")
        self.assertFalse(check(self.root)["ok"])
    def test_copilot_skill_and_agent_files_are_required(self):
        skill=self.root/".github/skills/atlas-research/SKILL.md"
        agent=self.root/".github/agents/domain-researcher.agent.md"
        self.assertTrue(skill.is_file()); self.assertTrue(agent.is_file())
    def test_cloud_model_routing_guidance_is_linked_and_uses_native_auto(self):
        guide=self.root/"docs/MODEL_ROUTING.md"
        self.assertTrue(guide.is_file())
        self.assertIn("MODEL_ROUTING.md",(self.root/"docs/USAGE.md").read_text())
        self.assertIn("Auto",guide.read_text())
        self.assertIn("not exposed",guide.read_text())
    def test_claude_adapter_is_required_and_validated(self):
        self.assertTrue(check(self.root)["ok"])
        (self.root/".claude/skills/atlas-init/SKILL.md").unlink()
        self.assertFalse(check(self.root)["ok"])


if __name__=="__main__": unittest.main()
