"""Synthetic integration fixture: never presented as an external research outcome."""
from .project import Project
from .intake import questions
from datetime import timedelta
from .io import atomic_json, file_hash, now, date, digest
from .enablement import feature_inventory


def evidence_fixture(path,strict=False):
    p=path/"sources/fixture.txt"; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text("Synthetic fixture only. The observed count is ten.\n",encoding="utf-8")
    stamp=now()
    data={"schema_version":2 if strict else 1,
      "sources":[{"id":"S1","source_type":"local","url":"local:synthetic-fixture","title":"Synthetic fixture",
      "provenance_note":"Created for deterministic local testing; not independently observed world data",
      "accessed_at":stamp,"origin_group":"fixture-1","snapshot":"sources/fixture.txt","sha256":file_hash(p)}],
      "claims":[{"id":"C1","text":"The synthetic fixture reports a count of ten.","kind":"factual","material":True,"source_ids":["S1"],"author":"fixture-author"}],
      "assessments":[{"claim_id":"C1","source_id":"S1","excerpt":"The observed count is ten.","locator":"line 1","verdict":"supports",
      "reasoning":"Exact statement in fixture; tests plumbing only, not human semantic review.","reviewer":"fixture-reviewer","reviewer_type":"model","independent":True,"reviewed_at":stamp}],
      "calculations":[]}
    if strict:
        claim=data["claims"][0]
        claim.update(scope="This local synthetic fixture only; no external population, geography or time inference.",
                     uncertainty={"level":"unknown","basis":"Deterministic fixture, not an empirical research observation.",
                                  "limitations":["No real-world validity or research-quality inference."]})
        data["assessments"][0].update(claim_sha256=digest(claim),snapshot_sha256=data["sources"][0]["sha256"])
    return data


def access_fixture(project):
    atomic_json(project.path/"access_plan.json",{
        "schema_version":1,"question":project.status()["question"],"coverage":["fixture_support"],
        "selection_reason":"Synthetic lifecycle uses local files only; no external MCP is needed.",
        "needs":[{"id":"local","name":"Local fixture reader","kind":"local","required":True,"paid":False,
                  "purpose":"Exercise deterministic control paths","endpoint":"local:fixture",
                  "coverage":["fixture_support"],"permissions":["read project fixture"],
                  "data_shared":"None","privacy":"Local synthetic data only","cost":"No external charge",
                  "alternatives":"No live tools used","quality_impact":"Cannot establish any external research conclusion"}]})
    project.approve_access([{"need_id":"local","decision":"use","reason":"Synthetic test of authorization plumbing"}],
                           "SYNTHETIC AUTHORIZATION FIXTURE; not an actual user decision")
    stamp=now()
    atomic_json(project.path/"access-tests/local.json",{
        "ok":True,"resource":"local:fixture","operation":"read fixture","observed_at":stamp,
        "expires_at":(date(stamp)+timedelta(days=1)).isoformat(),"limitations":"Synthetic access receipt, no external test"})
    project.record_access_test("local","access-tests/local.json")


def enablement_fixture(project):
    plan=feature_inventory(project.status()["question"])
    plan["environment"]="Local deterministic fixture; NOT a Copilot platform test"
    decisions=[]
    for feature in plan["features"]:
        if feature["id"]=="execution":
            stamp=now(); artifact="feature-tests/execution.json"
            atomic_json(project.path/artifact,{"feature_id":"execution","status":"enabled","observed_at":stamp,
                        "expires_at":(date(stamp)+timedelta(days=1)).isoformat(),
                        "method":"This synthetic Python fixture is executing","limitations":"No hosted Copilot capability is verified"})
            feature.update(status="enabled",needed=True,basis="Local synthetic execution",
                           verification={"artifact":artifact,"sha256":file_hash(project.path/artifact)})
            decision="use"
        else: decision="not_needed"
        decisions.append({"feature_id":feature["id"],"decision":decision,"reason":"Synthetic offline fixture only"})
    atomic_json(project.path/"enablement.json",plan)
    project.approve_enablement(decisions,"SYNTHETIC USER FEATURE DECISIONS; no actual platform settings changed")


def handoff_fixture(task_id,summary="Synthetic fixture inspected; not external research."):
    return {"task_id":task_id,"summary":summary,"source_ids":[],"unresolved":[],
            "limitations":["Synthetic fixture; no independent model or external research"],
            "execution":{"executor":"fixture-runner","kind":"synthetic","model_selection":"none",
                         "model_identity":"no model invoked","observed_at":now(),"tools":["local Python"]}}


def coverage_fixture(project,gap=False):
    queries=[
        {"id":"Q1","plan_id":"P1","query":"Synthetic fixture","tool":"local file","at":now(),
         "status":"complete","outcome":"Local synthetic source only","retrieved_ids":[] if gap else ["S1"],
         "included_ids":[] if gap else ["S1"],"exclusions":[]},
        {"id":"Q2","plan_id":"P2","query":"Counterexample in fixture","tool":"local file","at":now(),
         "status":"complete","outcome":"No additional included source","retrieved_ids":[],"included_ids":[],"exclusions":[]}]
    atomic_json(project.path/"search_log.json",{"queries":queries})
    item={"dimension":"fixture_support","status":"gap" if gap else "covered",
          "basis":"Synthetic coverage accounting only","search_ids":["Q1","Q2"],"source_ids":[] if gap else ["S1"]}
    if gap: item["decision_impact"]="No external conclusion is supported"
    atomic_json(project.path/"coverage.json",{"items":[item],"stopping_decision":"Synthetic plan processed",
                                            "stopping_reason":"plan_complete"})


def prepare_research(root,slug="demo",domain="general"):
    p=Project.create(root,slug,"Synthetic lifecycle demonstration; no external research",domain)
    for q in questions(root,domain):
        p.answer(q["key"],"Synthetic declared answer; this is not a user preference.")
    p.mandate(acknowledged=True)
    p.advance("MANDATE"); p.advance("ENABLEMENT"); enablement_fixture(p); access_fixture(p); p.advance("META")
    atomic_json(p.path/"dossier.json",{"methods_compared":["Structured source review","Unstructured summary"],"selection_reason":"Fixture chooses explicit provenance",
      "risks":"Synthetic test cannot establish research quality","limitations":"No live API or model","expertise":"Local engineering test","tool_comparison":"No network versus unavailable paid sources",
      "method_sources":[{"url":"https://www.prisma-statement.org/prisma-2020-statement","finding":"Reference label only in synthetic fixture; production dossier requires actual research","accessed_at":now()}],
      "pilot":"Synthetic source import and hash test"})
    atomic_json(p.path/"protocol.json",{"schema_version":2,"methods":["Synthetic source inspection"],"coverage":["fixture_support"],
      "search_plan":[{"id":"P1","dimension":"fixture_support","query":"Read local fixture","strategy":"primary","access_need_id":"local"},
                     {"id":"P2","dimension":"fixture_support","query":"Look for counterexample","strategy":"counterevidence","access_need_id":"local"}],
      "inclusion":"Synthetic fixture only","freshness_policy":"Read the current fixture bytes",
      "uncertainty_policy":"No empirical inference","bias_controls":["Do not interpret fixtures as research"],
      "synthesis_method":"Describe only the exercised local controls",
      "stopping_criteria":{"max_queries":2,"min_sources_per_dimension":1,"min_independent_origins":1,"consecutive_no_new":1},
      "exclusion":"All actual world conclusions","verification":"Compare exact phrase and hash","stopping_rule":"Fixture processed","amendment_policy":"Record reopen reason","meta_iterations":1,"evaluation_criteria":["Valid local control path; no research accuracy claim"]})
    p.advance("READINESS")
    atomic_json(p.path/"readiness.json",{"decision":"limited","checks":{k:{"status":"limited","basis":"Local synthetic fixture only","fallback":"No external claims"} for k in ["methods","evidence","tools","computation","budget","verification","permissions"]},"capabilities":[],"limitations":"Not a Copilot runtime test"})
    p.advance("ORCHESTRATE")
    atomic_json(p.path/"plan.json",{"architecture_reason":"Single deterministic fixture","model_policy":"No model invoked","tasks":[{"id":"collect","objective":"Inspect fixture","owner":"test-runner","evidence_required":"Snapshot and excerpt","depends_on":[]}]})
    p.advance("RESEARCH")
    return p


def complete(root,slug="demo"):
    p=prepare_research(root,slug)
    data=evidence_fixture(p.path,strict=True); atomic_json(p.path/"evidence.json",data)
    p.task("collect","running")
    atomic_json(p.path/"branches/collect.json",handoff_fixture("collect"))
    p.task("collect","done","branches/collect.json")
    coverage_fixture(p)
    p.advance("VERIFY")
    atomic_json(p.path/"review.json",{"author":"fixture-author","reviewer":"fixture-reviewer","independent":True,"decision":"conditional","unresolved_critical":[],"counterarguments":"No factual capability measured","uncertainty":"Synthetic only","coverage_review":"One fixture","numeric_review":"No numeric derivation","limitations":"Review identity is fixture data, not a real independent person or model","evidence_sha256":digest(data),"reviewed_claim_ids":["C1"],"model_identity":"no model invoked"})
    p.advance("SYNTHESIS")
    atomic_json(p.path/"synthesis.json",{"conclusion":"Synthetic pipeline completed","tradeoffs":"Fixture only","uncertainty":"No generalization measured","failure_conditions":"Invalid artifacts block transitions","strongest_counterargument":"Real research may fail despite passing local gates","claim_ids":["C1"]})
    p.advance("DELIVER")
    out=p.path/"outputs/demo-report.md"; out.write_text("# Synthetic lifecycle demonstration\n\nSynthetic plumbing only; no external research inference.\n\nThe fixture reports a count of ten. [[claim:C1]]\n")
    atomic_json(p.path/"deliverables.json",{"contract_review":"Synthetic one-file contract fulfilled","files":[{"path":"outputs/demo-report.md","kind":"report","claim_ids":["C1"],"sha256":file_hash(out),"format_review":"Markdown read","citation_review":"C1 maps to S1; synthetic"}]})
    p.advance("MEMORY")
    atomic_json(p.path/"lessons.json",{"outcome":"Synthetic flow only; no reusable empirical lesson","proposals":[]})
    p.advance("EVALUATE")
    atomic_json(p.path/"evaluation.json",{"criteria":["Valid local control path; no research accuracy claim"],"results":"Local control path exercised","failures":"None in fixture run","limitations":"No Copilot or external research","next_actions":"Run authorized real session and blinded evaluation","research_quality_proven":False})
    p.advance("COMPLETE")
    return p
