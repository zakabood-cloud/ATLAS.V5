"""python3 -m atlas --help"""
import argparse
import json
import sys
from pathlib import Path
from . import __version__
from .io import AtlasError, atomic_json, read_json, now
from .project import Project, STATES
from .intake import questions
from .integrations import discover_capabilities
from .structure import check
from .quant import run_analysis
from . import memory

READY="ATLAS Research OS is initialized and ready to receive your research inquiry."


def parser():
    p=argparse.ArgumentParser(description="ATLAS local research controls; network calls are opt-in")
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--version",action="version",version=__version__)
    sub=p.add_subparsers(dest="cmd",required=True)
    for c in ["init","doctor","check"]: sub.add_parser(c)
    a=sub.add_parser("session-profile"); a.add_argument("surface",choices=["copilot_sandbox","copilot_actions","copilot_cli","copilot_ide","claude_code","codex","unknown"])
    n=sub.add_parser("new"); n.add_argument("slug"); n.add_argument("--question",required=True); n.add_argument("--domain",default="general")
    for c in ["status","intake","validate","checkpoint"]: sub.add_parser(c).add_argument("slug")
    a=sub.add_parser("answer"); a.add_argument("slug"); a.add_argument("key"); a.add_argument("value")
    a=sub.add_parser("ask"); a.add_argument("slug"); a.add_argument("key"); a.add_argument("prompt"); a.add_argument("--essential",action="store_true")
    a=sub.add_parser("mandate"); a.add_argument("slug"); a.add_argument("--assumptions",type=Path); a.add_argument("--acknowledged",action="store_true"); a.add_argument("--paid-budget",default="0")
    a=sub.add_parser("advance"); a.add_argument("slug"); a.add_argument("state",choices=STATES)
    a=sub.add_parser("reopen"); a.add_argument("slug"); a.add_argument("state",choices=STATES); a.add_argument("--reason",required=True)
    a=sub.add_parser("restore"); a.add_argument("slug"); a.add_argument("checkpoint")
    a=sub.add_parser("hold"); a.add_argument("slug"); a.add_argument("kind",choices=["paused","blocked","aborted"]); a.add_argument("--reason",required=True)
    a=sub.add_parser("resume"); a.add_argument("slug"); a.add_argument("--reason",required=True); a.add_argument("--authorization"); a.add_argument("--scope",choices=["retry","continue-with-gaps"])
    for c in ["access-needs","access-status"]: sub.add_parser(c).add_argument("slug")
    for c in ["copilot-features","enablement-status"]: sub.add_parser(c).add_argument("slug")
    a=sub.add_parser("enablement-approve"); a.add_argument("slug"); a.add_argument("decisions",type=Path); a.add_argument("--authorization",required=True)
    a=sub.add_parser("access-approve"); a.add_argument("slug"); a.add_argument("decisions",type=Path); a.add_argument("--authorization",required=True)
    a=sub.add_parser("access-test"); a.add_argument("slug"); a.add_argument("need_id"); a.add_argument("artifact")
    a=sub.add_parser("access-resolve"); a.add_argument("slug"); a.add_argument("block_id"); a.add_argument("artifact")
    a=sub.add_parser("access-block"); a.add_argument("slug"); a.add_argument("--resource",required=True); a.add_argument("--operation",required=True); a.add_argument("--reason",required=True); a.add_argument("--quality-impact",required=True); a.add_argument("--need-id"); a.add_argument("--severity",choices=["critical","optional","security"],default="critical")
    a=sub.add_parser("migrate"); a.add_argument("slug"); a.add_argument("--backup",type=Path,required=True); a.add_argument("--authorization",required=True); a.add_argument("--quiesced",action="store_true")
    a=sub.add_parser("task"); a.add_argument("slug"); a.add_argument("id"); a.add_argument("status"); a.add_argument("--output"); a.add_argument("--reason")
    a=sub.add_parser("run-workers"); a.add_argument("slug"); a.add_argument("--worker",choices=["fixture"],default="fixture"); a.add_argument("--max-workers",type=int,default=2); a.add_argument("--max-tasks",type=int,default=50); a.add_argument("--timeout",type=float,default=120)
    a=sub.add_parser("dispatch-plan"); a.add_argument("slug"); a.add_argument("--max-workers",type=int,default=4)
    a=sub.add_parser("queries"); a.add_argument("question"); a.add_argument("--coverage",required=True); a.add_argument("--output",type=Path)
    a=sub.add_parser("corpus-search"); a.add_argument("query"); a.add_argument("documents",type=Path)
    a=sub.add_parser("method-score"); a.add_argument("spec",type=Path)
    a=sub.add_parser("report-audit"); a.add_argument("slug"); a.add_argument("report",type=Path); a.add_argument("--non-strict",action="store_true")
    a=sub.add_parser("review-packet"); a.add_argument("slug"); a.add_argument("claim_id")
    a=sub.add_parser("memory-search"); a.add_argument("query")
    a=sub.add_parser("continuation"); a.add_argument("slug"); a.add_argument("--output",type=Path)
    a=sub.add_parser("claim-check"); a.add_argument("claim"); a.add_argument("passages",type=Path)
    a=sub.add_parser("model-inputs-audit"); a.add_argument("spec",type=Path)
    a=sub.add_parser("research-api"); a.add_argument("provider",choices=["openai","gemini"]); a.add_argument("model"); a.add_argument("query"); a.add_argument("--request-id",required=True); a.add_argument("--max-cost",required=True); a.add_argument("--budget-limit",required=True); a.add_argument("--budget-db",type=Path,default=Path(".atlas/external_budget.sqlite3")); a.add_argument("--output",type=Path,required=True); a.add_argument("--authorize",action="store_true"); a.add_argument("--share-query-approved",action="store_true")
    a=sub.add_parser("scholarly-search"); a.add_argument("provider",choices=["openalex","crossref"]); a.add_argument("query"); a.add_argument("--live",action="store_true"); a.add_argument("--limit",type=int,default=10); a.add_argument("--project",required=True); a.add_argument("--need-id",required=True); a.add_argument("--cursor"); a.add_argument("--output",type=Path)
    a.add_argument("--probe",action="store_true"); a.add_argument("--plan-id")
    a=sub.add_parser("bench-eval"); a.add_argument("cases",type=Path); a.add_argument("results",type=Path)
    a=sub.add_parser("retrieval-eval"); a.add_argument("queries",type=Path); a.add_argument("results",type=Path); a.add_argument("--k",type=int,default=10)
    a=sub.add_parser("compare-eval"); a.add_argument("left",type=Path); a.add_argument("right",type=Path)
    sub.add_parser("source-audit").add_argument("slug")
    a=sub.add_parser("ingest"); a.add_argument("file",type=Path); a.add_argument("--output",type=Path)
    a=sub.add_parser("project-backup"); a.add_argument("slug"); a.add_argument("archive",type=Path); a.add_argument("--quiesced",action="store_true")
    a=sub.add_parser("project-restore"); a.add_argument("archive",type=Path); a.add_argument("target",type=Path)
    a=sub.add_parser("budget"); a.add_argument("action",choices=["status","reserve","settle","cancel","amend"]); a.add_argument("--db",type=Path,default=Path(".atlas/budget.sqlite3")); a.add_argument("--limit",required=True); a.add_argument("--key"); a.add_argument("--amount"); a.add_argument("--provider"); a.add_argument("--authorize",action="store_true")
    a=sub.add_parser("cost"); a.add_argument("slug"); a.add_argument("id"); a.add_argument("amount"); a.add_argument("--note",required=True)
    a=sub.add_parser("quant"); a.add_argument("spec",type=Path); a.add_argument("--output",type=Path)
    a=sub.add_parser("memory"); a.add_argument("--query",default=""); a.add_argument("--promote",type=Path)
    return p


def main(argv=None):
    args=parser().parse_args(argv); root=args.root.resolve(); result=None
    try:
        if args.cmd in {"init","check"}:
            result=check(root)
            if not result["ok"]: print(json.dumps(result,indent=2)); return 1
            if sys.version_info<(3,10): raise AtlasError("Python 3.10+ required")
            if args.cmd=="init":
                result.update(version=__version__,capabilities=discover_capabilities(root),state="AWAITING_INQUIRY")
                atomic_json(root/".atlas/installation.json",dict(result,at=now()))
                print(json.dumps(result,indent=2)); print(READY)
                return 0 # deliberately no intake, topic research, API call, or project creation
        elif args.cmd=="doctor": result=discover_capabilities(root)
        elif args.cmd=="session-profile":
            from .session import session_profile
            result=session_profile(args.surface)
        elif args.cmd=="new": result=Project.create(root,args.slug,args.question,args.domain).status()
        elif args.cmd=="quant":
            spec=read_json(args.spec); result={"input":spec,"result":run_analysis(spec)}
            if args.output: atomic_json(args.output,result)
        elif args.cmd=="memory": result=memory.promote(root,read_json(args.promote)) if args.promote else memory.retrieve(root,args.query)
        elif args.cmd=="memory-search":
            from .memory_search import retrieve_ranked
            result=retrieve_ranked(root,args.query)
        elif args.cmd=="continuation":
            from .continuation import save,snapshot
            project=Project(root,args.slug)
            result=save(project,root/args.output) if args.output else snapshot(project)
        elif args.cmd=="claim-check":
            from .claim_checks import check_claim_context
            data=read_json(args.passages)
            result=check_claim_context(args.claim,data["passages"])
        elif args.cmd=="model-inputs-audit":
            from .analysis_inputs import validate_inputs
            result=validate_inputs(read_json(args.spec))
        elif args.cmd=="research-api":
            from .model_research import ProviderRequest,execute
            if not args.authorize or not args.share_query_approved:
                raise AtlasError("Explicit external spend and query transmission approval required")
            req=ProviderRequest(args.provider,args.model,args.query,args.request_id,args.max_cost,authorized=True,private_data_approved=True)
            result=execute(req,budget_file=root/args.budget_db,ceiling_usd=args.budget_limit,result_path=root/args.output)
        elif args.cmd=="queries":
            from .retrieval import expand_queries
            result=expand_queries(args.question,args.coverage.split(','))
            if args.output: atomic_json(args.output,result)
        elif args.cmd=="corpus-search":
            from .retrieval import bm25_search
            result=bm25_search(args.query,read_json(args.documents))
        elif args.cmd=="method-score":
            from .methodology import score_methods
            spec=read_json(args.spec)
            result=score_methods(spec["candidates"],spec.get("weights"),spec.get("minimum_scores"))
        elif args.cmd=="scholarly-search":
            if not args.live: raise AtlasError("Live public requests require --live; verify provider terms and possible metered API costs first")
            from .adapters import guarded_search
            result=guarded_search(Project(root,args.project),args.need_id,args.provider,args.query,args.limit,args.cursor,
                                  probe=args.probe,plan_id=args.plan_id)
            if args.output: atomic_json(args.output,result)
        elif args.cmd=="bench-eval":
            from .evaluation import evaluate_cases
            result=evaluate_cases(read_json(args.cases),read_json(args.results))
        elif args.cmd=="retrieval-eval":
            from .evaluation import evaluate_retrieval
            result=evaluate_retrieval(read_json(args.queries),read_json(args.results),k=args.k)
        elif args.cmd=="compare-eval":
            from .evaluation import compare_runs
            result=compare_runs(read_json(args.left),read_json(args.right))
        elif args.cmd=="source-audit":
            from .sourcegraph import group_origins,contradictions
            evidence=Project(root,args.slug).artifact("evidence.json")
            result={"origins":group_origins(evidence["sources"]),"contradictions":contradictions(evidence)}
        elif args.cmd=="ingest":
            from .ingest import ingest
            result=ingest(args.file)
            if args.output: atomic_json(args.output,result)
        elif args.cmd=="project-backup":
            from .project_archive import backup
            result=backup(Project(root,args.slug).path,args.archive,args.quiesced)
        elif args.cmd=="project-restore":
            from .project_archive import restore
            result=restore(args.archive,args.target)
        elif args.cmd=="budget":
            from .budget import Budget
            b=Budget(root/args.db,args.limit)
            if args.action=="status": result=b.status()
            elif args.action=="reserve": result=b.reserve(args.key,args.amount,args.provider,authorized=args.authorize)
            elif args.action=="settle": result=b.settle(args.key,args.amount)
            elif args.action=="amend": result=b.amend_limit(args.amount,args.authorize)
            else: result=b.cancel(args.key)
        elif args.cmd=="run-workers":
            from .scheduler import run_ready,FixtureWorker
            import asyncio
            worker=FixtureWorker()
            result=asyncio.run(run_ready(Project(root,args.slug),worker,args.max_workers,args.max_tasks,args.timeout))
        elif args.cmd=="dispatch-plan":
            from .dispatch import dispatch_plan
            result=dispatch_plan(Project(root,args.slug).dispatch_context(args.max_workers),args.max_workers)
        elif args.cmd=="report-audit":
            from .verification import report_audit
            result=report_audit(args.report.read_text(encoding="utf-8"),Project(root,args.slug).artifact("evidence.json"),strict=not args.non_strict)
        elif args.cmd=="review-packet":
            from .verification import review_packet
            p=Project(root,args.slug)
            result=review_packet(p.artifact("evidence.json"),p.path,args.claim_id)
        elif args.cmd=="restore": result=Project.restore(root,args.slug,args.checkpoint)
        else:
            project=Project(root,args.slug)
            if args.cmd=="status": result=project.status()
            elif args.cmd=="intake":
                state=project.status()
                if state["state"]!="INTAKE": raise AtlasError("Project no longer in intake")
                result={"questions":questions(root,state["domain"],state["answers"],state["extra_questions"]),"guidance":"Ask relevant unanswered questions in adaptive batches; no arbitrary question cap. Partial answers allowed. User may end with acknowledged assumptions."}
            elif args.cmd=="answer": project.answer(args.key,args.value); result={"recorded":args.key}
            elif args.cmd=="ask": project.add_question(args.key,args.prompt,args.essential); result={"added":args.key}
            elif args.cmd=="mandate": result=project.mandate(read_json(args.assumptions) if args.assumptions else None,args.acknowledged,args.paid_budget)
            elif args.cmd=="advance": result=project.advance(args.state)
            elif args.cmd=="reopen": result=project.reopen(args.state,args.reason)
            elif args.cmd=="hold": result=project.hold(args.kind,args.reason)
            elif args.cmd=="resume": result=project.resume(args.reason,args.authorization,args.scope)
            elif args.cmd=="access-needs":
                from .access import recommend_needs
                state=project.status(); result=recommend_needs(state["question"],state["domain"])
            elif args.cmd=="copilot-features":
                from .enablement import feature_inventory
                result=feature_inventory(project.status()["question"])
            elif args.cmd=="enablement-approve": result=project.approve_enablement(read_json(args.decisions)["decisions"],args.authorization)
            elif args.cmd=="enablement-status": result={"approval":project.status().get("enablement"),"state":project.status()["state"]}
            elif args.cmd=="access-status":
                state=project.status(); result={"approval":state.get("access"),"blocks":state.get("access_blocks",[]),"hold":state.get("hold")}
            elif args.cmd=="access-approve": result=project.approve_access(read_json(args.decisions)["decisions"],args.authorization)
            elif args.cmd=="access-test": result=project.record_access_test(args.need_id,args.artifact)
            elif args.cmd=="access-resolve": result=project.resolve_external_access(args.block_id,args.artifact)
            elif args.cmd=="access-block":
                result=project.block_access(args.resource,args.operation,args.reason,args.quality_impact,args.need_id,severity=args.severity)
                result["ok"]=False
            elif args.cmd=="migrate": result=project.migrate(args.backup,args.authorization,args.quiesced)
            elif args.cmd=="task": result=project.task(args.id,args.status,args.output,args.reason)
            elif args.cmd=="checkpoint": result={"checkpoint":project.checkpoint()}
            elif args.cmd=="cost": project.record_cost(args.id,args.amount,args.note); result={"recorded":args.id}
            elif args.cmd=="validate":
                result=project.validate()
                if not result["evidence"]["ok"]: print(json.dumps(result,indent=2)); return 1
        print(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
        return 1 if isinstance(result,dict) and result.get("ok") is False else 0
    except (AtlasError,OSError,ValueError,KeyError,TypeError) as e:
        print(json.dumps({"ok":False,"error":str(e)},ensure_ascii=False),file=sys.stderr); return 2


if __name__=="__main__": sys.exit(main())
