"""Transactional research lifecycle, immutable transition receipts, and bounded task ledger.

These controls govern this CLI. They do not sandbox Copilot or prevent a filesystem owner
from modifying artifacts, databases, or reports outside the CLI.
"""
import json
import re
import shutil
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from .io import AtlasError, now, canonical, digest, read_json, parse_json, atomic_json, confined, file_hash, text_required, date
from .access import validate_plan, validate_decisions
from .contracts import validate_protocol, validate_coverage, validate_handoff
from .enablement import validate_features, validate_feature_decisions
from .intake import questions, missing, profiles
from .evidence import validate_evidence
from .integrations import validate_observation
from .quant import D, nonnegative

STATES = ["INTAKE","MANDATE","ENABLEMENT","META","READINESS","ORCHESTRATE","RESEARCH","VERIFY","SYNTHESIS","DELIVER","MEMORY","EVALUATE","COMPLETE"]
ARTIFACTS = {
    "MANDATE":["mandate.json"], "META":[],
    "READINESS":["dossier.json","protocol.json"], "ORCHESTRATE":["readiness.json"],
    "RESEARCH":["plan.json"], "VERIFY":["coverage.json","search_log.json"],
    "SYNTHESIS":["evidence.json","review.json"], "DELIVER":["synthesis.json"],
    "MEMORY":["deliverables.json"], "EVALUATE":["lessons.json"], "COMPLETE":["evaluation.json"]}


def project_path(root, slug):
    if not isinstance(slug,str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}",slug):
        raise AtlasError("Project ID must be 1..64 lowercase letters/digits/hyphens")
    return confined(root,"projects/"+slug)


class Project:
    def __init__(self, root, slug):
        self.root=Path(root).resolve(); self.slug=slug; self.path=project_path(self.root,slug)
        self.db=confined(self.path,"state.sqlite3",True)

    @classmethod
    def create(cls,root,slug,question,domain):
        root=Path(root).resolve()
        if not isinstance(question,str) or not question.strip(): raise AtlasError("Research inquiry required")
        if domain not in profiles(root): raise AtlasError("Unknown domain")
        path=project_path(root,slug)
        if path.exists(): raise AtlasError("Project already exists; resume it instead")
        path.mkdir(parents=True)
        for part in ["sources","calculations","outputs","branches","checkpoints"]: (path/part).mkdir()
        con=sqlite3.connect(path/"state.sqlite3")
        try:
            con.executescript("""
                CREATE TABLE meta (id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL);
                CREATE TABLE events (seq INTEGER PRIMARY KEY AUTOINCREMENT, record TEXT NOT NULL, hash TEXT NOT NULL);
                CREATE TABLE tasks (id TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE costs (id TEXT PRIMARY KEY, amount TEXT NOT NULL, note TEXT NOT NULL);
            """)
            state={"schema_version":2,"state":"INTAKE","revision":0,"question":question,
                   "domain":domain,"answers":{},"extra_questions":[],"seals":{},"hold":None,"created_at":now()}
            con.execute("INSERT INTO meta VALUES (1,?)",(canonical(state),))
            cls._event(con,"inquiry_received",{"question":question,"domain":domain},state)
            con.commit()
        finally: con.close()
        atomic_json(path/"evidence.json",{"schema_version":2,"sources":[],"claims":[],"assessments":[],"calculations":[]})
        return cls(root,slug)

    @contextmanager
    def connection(self,write=False):
        try:
            con=sqlite3.connect(self.db,timeout=5)
            con.execute("PRAGMA foreign_keys=ON")
            if con.execute("PRAGMA quick_check").fetchone()[0]!="ok": raise AtlasError("Corrupted state database")
            if write: con.execute("BEGIN IMMEDIATE")
            self._check_log(con)
            yield con
            if write: con.commit()
        except sqlite3.Error as e:
            raise AtlasError("State database unavailable/corrupt/locked; restore a checked checkpoint") from e
        except (KeyError,TypeError,AttributeError,IndexError,json.JSONDecodeError) as e:
            raise AtlasError("Malformed state or project artifact; repair the named input or restore a checked checkpoint") from e
        finally:
            if 'con' in locals(): con.close()

    @staticmethod
    def _state(con):
        row=con.execute("SELECT value FROM meta WHERE id=1").fetchone()
        if row is None: raise AtlasError("Missing state")
        state=parse_json(row[0])
        if state.get("state") not in STATES or state.get("schema_version") not in {1,2}: raise AtlasError("Unknown state or schema")
        return state

    @staticmethod
    def _ledger_digest(con):
        return digest({"tasks": list(con.execute("SELECT id,value FROM tasks ORDER BY id")),
                       "costs": list(con.execute("SELECT id,amount,note FROM costs ORDER BY id"))})

    @staticmethod
    def _event(con,kind,payload,state):
        prev=con.execute("SELECT hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        record={"at":now(),"kind":kind,"payload":payload,"state_digest":digest(state),
                "ledger_digest":Project._ledger_digest(con),"previous":prev[0] if prev else None}
        con.execute("INSERT INTO events(record,hash) VALUES (?,?)",(canonical(record),digest(record)))

    def _check_log(self,con):
        previous=None; last=None
        for _,record,h in con.execute("SELECT seq,record,hash FROM events ORDER BY seq"):
            row=parse_json(record)
            if row.get("previous")!=previous or digest(row)!=h: raise AtlasError("Event chain corrupted")
            previous=h; last=row
        if last is None or last["state_digest"]!=digest(self._state(con)): raise AtlasError("State differs from event receipt")
        if last.get("ledger_digest")!=self._ledger_digest(con): raise AtlasError("Task/cost ledger differs from event receipt")

    def _save(self,con,state,kind,payload):
        state["revision"]+=1
        con.execute("UPDATE meta SET value=? WHERE id=1",(canonical(state),))
        self._event(con,kind,payload,state)

    @staticmethod
    def _active(state):
        if state.get("hold"): raise AtlasError("Project is held: "+state["hold"]["kind"]+"; explicitly resume before continuing")

    def hold(self,kind,reason):
        if kind not in {"paused","blocked","aborted"} or not reason.strip(): raise AtlasError("Known hold kind and reason required")
        with self.connection(True) as con:
            state=self._state(con)
            if state.get("hold") and state["hold"].get("category")=="access":
                raise AtlasError("Resolve the existing access hold; it cannot be replaced")
            state["hold"]={"kind":kind,"reason":reason,"at":now()}
            self._save(con,state,"held",state["hold"])
        return self.status()

    def resume(self,reason,authorization=None,scope=None):
        if not reason.strip(): raise AtlasError("Resume reason and appropriate user authorization required")
        with self.connection(True) as con:
            state=self._state(con)
            if not state.get("hold"): raise AtlasError("Project is not held")
            previous=state["hold"]
            if previous.get("category")=="access":
                if not isinstance(authorization,str) or not authorization.strip() or scope not in {"retry","continue-with-gaps"}:
                    raise AtlasError("Access resume requires explicit user authorization and scope retry or continue-with-gaps")
                if scope=="retry":
                    previous["retry_authorized"]=True
                    previous["authorization"]=authorization
                    previous["authorized_at"]=now()
                    previous["attempted_block_ids"]=[]
                else:
                    for row in state["access_blocks"]:
                        if row["id"] in previous["block_ids"] and row["disposition"]=="unresolved":
                            row.update(disposition="user_accepted_gap",authorization=authorization,resolution_reason=reason,resolved_at=now())
                            for decision in state.get("access",{}).get("decisions",[]):
                                if decision["need_id"]==row.get("need_id"):
                                    decision.update(decision="defer",reason=reason,quality_impact=row["quality_impact"])
                    state["hold"]=None
            else:
                if state["schema_version"]>=2 and (not isinstance(authorization,str) or not authorization.strip()):
                    raise AtlasError("Record explicit authorization to resume this project")
                if previous.get("category")=="task":
                    row=con.execute("SELECT value FROM tasks WHERE id=?",(previous["task_id"],)).fetchone()
                    task=parse_json(row[0])
                    task.update(status="failed",failure_reason=previous["reason"],updated_at=now())
                    con.execute("UPDATE tasks SET value=? WHERE id=?",(canonical(task),task["id"]))
                state["hold"]=None
            self._save(con,state,"resumed",{"reason":reason,"authorization":authorization,"scope":scope,"previous":previous})
        return self.status()

    def approve_access(self,decisions,authorization):
        if not isinstance(authorization,str) or not authorization.strip(): raise AtlasError("Actual user authorization required")
        with self.connection(True) as con:
            state=self._state(con); self._active(state)
            if STATES.index(state["state"])<STATES.index("MANDATE"): raise AtlasError("Accept the mandate before access approval")
            self._seals(state)
            plan=self.artifact("access_plan.json")
            needs=validate_plan(plan,state["question"])
            validate_decisions(needs,decisions)
            state["access"]={"plan_sha256":file_hash(self.path/"access_plan.json"),"decisions":decisions,
                             "authorization":authorization,"approved_at":now(),"tests":{}}
            self._save(con,state,"access_approved",state["access"])
        return self.status()["access"]

    def approve_enablement(self,decisions,authorization):
        text_required({"authorization":authorization},"authorization")
        with self.connection(True) as con:
            state=self._state(con); self._active(state); self._seals(state)
            if state["schema_version"]<2 or state["state"]!="ENABLEMENT":
                raise AtlasError("Review Copilot features in the ENABLEMENT stage")
            features=validate_features(self.artifact("enablement.json"),state["question"],self.path)
            result=validate_feature_decisions(features,decisions)
            state["enablement"]={"plan_sha256":file_hash(self.path/"enablement.json"),"decisions":decisions,
                                 "authorization":authorization,"approved_at":now()}
            self._save(con,state,"enablement_approved",state["enablement"])
        return dict(result,approval=self.status()["enablement"])

    def _enablement(self,state,ready=True):
        plan=self.artifact("enablement.json"); features=validate_features(plan,state["question"],self.path)
        approval=state.get("enablement",{})
        if approval.get("plan_sha256")!=file_hash(self.path/"enablement.json"):
            raise AtlasError("Current Copilot feature review needs explicit user approval")
        validate_feature_decisions(features,approval.get("decisions"),ready=ready)
        return features,approval

    def _access(self,state,ready=False):
        plan=self.artifact("access_plan.json"); needs=validate_plan(plan,state["question"])
        approval=state.get("access",{})
        if approval.get("plan_sha256")!=file_hash(self.path/"access_plan.json"):
            raise AtlasError("Current topic-specific access plan needs explicit user approval")
        validate_decisions(needs,approval.get("decisions"))
        if ready:
            for decision in approval["decisions"]:
                if decision["decision"]!="use": continue
                nid=decision["need_id"]; test=approval.get("tests",{}).get(nid)
                if not test: raise AtlasError("Approved capability needs an observed read-only access test: "+nid)
                if date(test["expires_at"])<=date(now()): raise AtlasError("Access test expired: "+nid)
                if file_hash(confined(self.path,test["artifact"],True))!=test["sha256"]:
                    raise AtlasError("Access test receipt changed: "+nid)
        return needs,approval

    def require_access(self,need_id,resource,operation,consume_retry=False):
        with self.connection(consume_retry) as con:
            state=self._state(con); self._seals(state)
            if state["schema_version"]>=2: self._enablement(state)
            needs,approval=self._access(state)
            decision=next((d for d in approval["decisions"] if d["need_id"]==need_id),None)
            if need_id not in needs or not decision or decision["decision"]!="use":
                raise AtlasError("Access need is not user-approved")
            if resource.rstrip("/")!=needs[need_id]["endpoint"].rstrip("/"):
                raise AtlasError("Requested resource differs from the approved endpoint")
            hold=state.get("hold")
            if hold:
                permitted=hold.get("category")=="access" and hold.get("retry_authorized") is True
                blocks=[b for b in state.get("access_blocks",[]) if b["id"] in hold.get("block_ids",[])
                        and b["disposition"]=="unresolved" and b["resource"]==resource
                        and b["operation"]==operation and b.get("need_id")==need_id]
                if not permitted or not blocks:
                    raise AtlasError("Project held; only the specifically authorized access retry is permitted")
                if consume_retry:
                    attempted=hold.setdefault("attempted_block_ids",[])
                    if all(b["id"] in attempted for b in blocks):
                        raise AtlasError("Authorized retry already dispatched; request fresh user authorization")
                    attempted.extend(b["id"] for b in blocks if b["id"] not in attempted)
                    self._save(con,state,"access_retry_dispatched",{"resource":resource,"operation":operation,"need_id":need_id})
            return needs[need_id]

    def prepare_search(self,need_id,query,probe=False,plan_id=None):
        with self.connection() as con:
            state=self._state(con); self._seals(state)
            if type(probe) is not bool: raise AtlasError("Probe must be boolean")
            if probe:
                if state["state"] not in {"ENABLEMENT","META","READINESS","ORCHESTRATE"}:
                    raise AtlasError("Preflight probes run only during preparation")
            elif state["state"]!="RESEARCH":
                raise AtlasError("Substantive scholarly searches require RESEARCH; use --probe --limit 1 for an explicitly authorized preparation access test")
            else:
                self._active(state)
                if state["schema_version"]>=2:
                    planned=next((row for row in self.artifact("protocol.json")["search_plan"]
                                  if row["id"]==plan_id),None)
                    if not planned or planned["access_need_id"]!=need_id or planned["query"]!=query:
                        raise AtlasError("Research search must match its accepted protocol plan ID, query and access need")

    def record_search(self,artifact):
        path=confined(self.path,artifact,True); receipt=read_json(path)
        if not isinstance(receipt,dict) or receipt.get("purpose") not in {"probe","research"}:
            raise AtlasError("Known retrieval purpose required")
        for key in ("id","need_id","query","resource","at"): text_required(receipt,key)
        with self.connection(True) as con:
            state=self._state(con)
            rows=state.setdefault("retrieval_receipts",[])
            if any(row["id"]==receipt["id"] for row in rows): raise AtlasError("Duplicate retrieval observation")
            row={"id":receipt["id"],"artifact":artifact,"sha256":file_hash(path),"purpose":receipt["purpose"],
                 "plan_id":receipt.get("plan_id"),"query":receipt["query"],"ok":receipt.get("ok") is True}
            rows.append(row); self._save(con,state,"retrieval_recorded",row)
        return row

    def record_access_test(self,need_id,artifact):
        receipt=read_json(confined(self.path,artifact,True))
        if not isinstance(receipt,dict) or receipt.get("ok") is not True:
            raise AtlasError("Successful access receipt required; failures must be recorded with access-block")
        for key in ("resource","operation","observed_at","expires_at","limitations"):
            text_required(receipt,key)
        self.require_access(need_id,receipt["resource"],receipt["operation"])
        with self.connection(True) as con:
            state=self._state(con); _,approval=self._access(state)
            if not date(approval["approved_at"])<=date(receipt["observed_at"])<=date(now()):
                raise AtlasError("Access test must be observed after approval, not in the future")
            if date(receipt["expires_at"])<=date(now()): raise AtlasError("Access test already expired")
            test={"artifact":artifact,"sha256":file_hash(confined(self.path,artifact,True)),
                  "observed_at":receipt["observed_at"],"expires_at":receipt["expires_at"]}
            approval["tests"][need_id]=test
            hold=state.get("hold")
            if hold and hold.get("category")=="access" and hold.get("retry_authorized"):
                for block in state["access_blocks"]:
                    if (block["id"] in hold["block_ids"] and block["resource"]==receipt["resource"]
                            and block["operation"]==receipt["operation"] and block.get("need_id")==need_id
                            and block["disposition"]=="unresolved"):
                        if date(receipt["observed_at"])<date(hold["authorized_at"]):
                            raise AtlasError("Retry receipt predates user authorization")
                        block.update(disposition="access_restored",receipt=test,authorization=hold["authorization"],resolved_at=now())
                unresolved=[b["id"] for b in state["access_blocks"] if b["id"] in hold["block_ids"] and b["disposition"]=="unresolved"]
                if not unresolved: state["hold"]=None
            self._save(con,state,"access_test_recorded",{"need_id":need_id,**test})
        return self.status()

    def block_access(self,resource,operation,reason,quality_impact,need_id=None,task_id=None,severity="critical"):
        payload={"resource":resource,"operation":operation,"reason":reason,"quality_impact":quality_impact}
        for key in payload: text_required(payload,key)
        from .failures import decision
        impact_policy=decision(severity)
        with self.connection(True) as con:
            state=self._state(con); blocks=state.setdefault("access_blocks",[])
            block=dict(payload,id=f"B{len(blocks)+1:04d}",at=now(),need_id=need_id,
                       disposition="unresolved",severity=severity)
            blocks.append(block)
            if impact_policy["pause_project"]:
                previous=state.get("hold")
                ids=list(previous.get("block_ids",[])) if previous and previous.get("category")=="access" else []
                ids.append(block["id"])
                state["hold"]={"kind":"blocked","category":"access","reason":reason,"at":now(),"block_ids":ids,
                               "retry_authorized":False}
            if need_id and state.get("access"): state["access"]["tests"].pop(need_id,None)
            if task_id:
                row=con.execute("SELECT value FROM tasks WHERE id=?",(task_id,)).fetchone()
                if row:
                    task=parse_json(row[0])
                    if task["status"]=="running":
                        task.update(status="failed",failure_reason=reason,updated_at=now())
                        con.execute("UPDATE tasks SET value=? WHERE id=?",(canonical(task),task_id))
            self._save(con,state,"access_blocked",block)
        return self.status()

    def resolve_external_access(self,block_id,artifact):
        """Record an observed external-tool retry that this Python process cannot execute."""
        path=confined(self.path,artifact,True); receipt=read_json(path)
        if not isinstance(receipt,dict) or receipt.get("ok") is not True:
            raise AtlasError("Successful external-tool observation required")
        for key in ("resource","operation","observed_at","method","limitations"):
            text_required(receipt,key)
        with self.connection(True) as con:
            state=self._state(con); hold=state.get("hold")
            if not hold or hold.get("category")!="access" or hold.get("retry_authorized") is not True:
                raise AtlasError("Explicit scoped user retry authorization required")
            block=next((b for b in state.get("access_blocks",[]) if b["id"]==block_id),None)
            if not block or block_id not in hold["block_ids"] or block["disposition"]!="unresolved":
                raise AtlasError("Choose an unresolved block in the current access hold")
            if block.get("need_id") is not None:
                raise AtlasError("Planned capabilities must use access-test to revalidate their approved endpoint")
            if receipt["resource"]!=block["resource"] or receipt["operation"]!=block["operation"]:
                raise AtlasError("External observation must match the blocked resource and operation")
            if not date(hold["authorized_at"])<=date(receipt["observed_at"])<=date(now()):
                raise AtlasError("External retry observation must follow authorization and not be future-dated")
            block.update(disposition="access_restored",authorization=hold["authorization"],resolved_at=now(),
                         receipt={"artifact":artifact,"sha256":file_hash(path)},
                         observation_limit="Operator-recorded external tool result, not independently authenticated by Python")
            if all(b["disposition"]!="unresolved" for b in state["access_blocks"] if b["id"] in hold["block_ids"]):
                state["hold"]=None
            self._save(con,state,"external_access_restored",{"block_id":block_id,"receipt":block["receipt"]})
        return self.status()

    def interrupt_task(self,task_id,reason):
        """Record interruption even while held; never dispatch or accept new output."""
        text_required({"reason":reason},"reason")
        with self.connection(True) as con:
            state=self._state(con)
            row=con.execute("SELECT value FROM tasks WHERE id=?",(task_id,)).fetchone()
            if not row: raise AtlasError("Unknown task")
            task=parse_json(row[0])
            if task["status"]!="running": return task
            task.update(status="failed",failure_reason=reason,updated_at=now())
            con.execute("UPDATE tasks SET value=? WHERE id=?",(canonical(task),task_id))
            self._save(con,state,"task_interrupted",{"id":task_id,"reason":reason})
        return task

    def status(self):
        with self.connection() as con:
            state=self._state(con)
            return dict(state,project=self.slug,legacy_contract=state["schema_version"]==1,tasks=[parse_json(r[0]) for r in con.execute("SELECT value FROM tasks ORDER BY id")],
                        cost_recorded=str(sum((D(r[0]) for r in con.execute("SELECT amount FROM costs")),D(0))))

    def answer(self,key,value):
        if not isinstance(value,str) or not value.strip(): raise AtlasError("Answer cannot be empty")
        with self.connection(True) as con:
            state=self._state(con)
            self._active(state)
            if state["state"]!="INTAKE": raise AtlasError("Reopen INTAKE before changing mandate inputs")
            allowed={q["key"] for q in questions(self.root,state["domain"],state["answers"],state["extra_questions"])}
            if key not in allowed: raise AtlasError("Unknown question; add it first")
            state["answers"][key]=value
            self._save(con,state,"answer_recorded",{"key":key})

    def add_question(self,key,prompt,essential=False):
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}",key): raise AtlasError("Invalid question key")
        if not prompt.strip(): raise AtlasError("Question is empty")
        with self.connection(True) as con:
            state=self._state(con)
            self._active(state)
            if state["state"]!="INTAKE": raise AtlasError("Not in intake")
            allq=questions(self.root,state["domain"],state["answers"],state["extra_questions"])
            if key in {q["key"] for q in allq}: raise AtlasError("Question already exists")
            state["extra_questions"].append({"key":key,"prompt":prompt,"essential":bool(essential),"batch":"adaptive"})
            self._save(con,state,"question_added",{"key":key})

    def mandate(self,assumptions=None,acknowledged=False,paid_budget="0"):
        assumptions=assumptions or {}
        if not isinstance(assumptions,dict) or any(not isinstance(v,str) or not v.strip() for v in assumptions.values()): raise AtlasError("Assumptions must map question keys to explicit text")
        state=self.status()
        self._active(state)
        if state["state"]!="INTAKE": raise AtlasError("Mandate can only be built during intake")
        gaps=missing(self.root,state["domain"],state["answers"],state["extra_questions"])
        if any(k not in assumptions for k in gaps): raise AtlasError("Essential questions unanswered: "+", ".join(k for k in gaps if k not in assumptions))
        if not acknowledged: raise AtlasError("User must end intake and acknowledge consequential assumptions; record with --acknowledged")
        out={"schema_version":1,"question":state["question"],"domain":state["domain"],"answers":state["answers"],
             "assumptions":assumptions,"user_ended_intake":True,"assumptions_presented":True,"paid_budget":str(nonnegative(paid_budget)),
             "deliverables":state["answers"].get("deliverables",assumptions.get("deliverables")),"created_at":now()}
        atomic_json(self.path/"mandate.json",out)
        return out

    def artifact(self,name):
        obj=read_json(confined(self.path,name,True))
        if not isinstance(obj,dict): raise AtlasError(name+" must be an object")
        return obj

    def _seals(self,state):
        for name,receipt in state["seals"].items():
            if file_hash(confined(self.path,name,True))!=receipt["sha256"]:
                raise AtlasError("Previously accepted artifact changed: "+name+"; reopen the appropriate earlier state")

    def _gate(self,target,state,con):
        strict=state["schema_version"]>=2
        if strict and target in {"META","READINESS","ORCHESTRATE","RESEARCH","VERIFY","SYNTHESIS","DELIVER","MEMORY"}:
            self._enablement(state)
            self._access(state,ready=True)
        if target=="MANDATE":
            m=self.artifact("mandate.json")
            if m.get("question")!=state["question"] or m.get("domain")!=state["domain"] or m.get("answers")!=state["answers"]: raise AtlasError("Mandate differs from interview")
            if m.get("user_ended_intake") is not True or m.get("assumptions_presented") is not True: raise AtlasError("Intake not ended/acknowledged")
            text_required(m,"deliverables")
            gaps=missing(self.root,state["domain"],state["answers"],state["extra_questions"])
            for key in gaps: text_required(m.get("assumptions",{}),key)
            nonnegative(m.get("paid_budget"))
        elif target=="READINESS":
            d=self.artifact("dossier.json"); p=self.artifact("protocol.json")
            for k in ["selection_reason","risks","limitations","expertise","tool_comparison"]: text_required(d,k)
            if not isinstance(d.get("methods_compared"),list) or len(d["methods_compared"])<2: raise AtlasError("Compare at least two methodological alternatives, including simple designs")
            if not isinstance(d.get("method_sources"),list) or not d["method_sources"]: raise AtlasError("Independent methodology source research required")
            for row in d["method_sources"]:
                for k in ["url","finding","accessed_at"]: text_required(row,k)
            if not d.get("pilot"): raise AtlasError("Record source/tool pilot or specific access limitation")
            for k in ["inclusion","exclusion","verification","stopping_rule","amendment_policy"]: text_required(p,k)
            for k in ["methods","coverage","search_plan","evaluation_criteria"]:
                if not isinstance(p.get(k),list) or not p[k]: raise AtlasError("Protocol needs "+k)
            if len(set(p["coverage"]))!=len(p["coverage"]): raise AtlasError("Duplicate coverage dimension")
            if type(p.get("meta_iterations")) is not int or not 1<=p["meta_iterations"]<=3: raise AtlasError("Bound meta research to 1..3 passes; further work needs a documented amended protocol")
            if strict: validate_protocol(p,self._access(state)[0])
        elif target=="ORCHESTRATE":
            r=self.artifact("readiness.json")
            if r.get("decision") not in {"ready","limited"}: raise AtlasError("Readiness blocked")
            checks=r.get("checks",{})
            for key in ["methods","evidence","tools","computation","budget","verification","permissions"]:
                row=checks.get(key,{})
                if row.get("status") not in {"passed","limited"}: raise AtlasError("Readiness check blocked/missing: "+key)
                text_required(row,"basis")
                if row["status"]=="limited": text_required(row,"fallback")
            for row in r.get("capabilities",[]):
                checked=validate_observation(row)
                if checked["expired"] and row["status"] in {"authenticated","tested"}: raise AtlasError("Expired capability observation must be refreshed or downgraded")
                if row.get("evidence_artifact"): confined(self.path,row["evidence_artifact"],True)
            text_required(r,"limitations")
        elif target=="RESEARCH":
            p=self.artifact("plan.json"); tasks=p.get("tasks")
            text_required(p,"architecture_reason"); text_required(p,"model_policy")
            if not isinstance(tasks,list) or not tasks: raise AtlasError("Task plan required")
            ids=[text_required(t,"id") for t in tasks]
            if len(set(ids))!=len(ids): raise AtlasError("Duplicate task ID")
            for t in tasks:
                if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}",t["id"]): raise AtlasError("Unsafe task ID")
                for k in ["objective","owner","evidence_required"]: text_required(t,k)
                if not isinstance(t.get("depends_on"),list) or any(x not in ids for x in t["depends_on"]): raise AtlasError("Unknown dependency")
                from .dispatch import validate_task_scope
                validate_task_scope(t)
                if strict:
                    approved={d["need_id"] for d in state["access"]["decisions"] if d["decision"]=="use"}
                    if not set(t.get("access_need_ids",[]))<=approved:
                        raise AtlasError("Task requires an unapproved or deferred access capability")
            remaining={t["id"]:len(t["depends_on"]) for t in tasks}; dependents={tid:[] for tid in ids}
            for task in tasks:
                if len(set(task["depends_on"]))!=len(task["depends_on"]): raise AtlasError("Duplicate dependency")
                for dep in task["depends_on"]: dependents[dep].append(task["id"])
            ready=[tid for tid in ids if not remaining[tid]]; visited=0
            while ready:
                tid=ready.pop(); visited+=1
                for dependent in dependents[tid]:
                    remaining[dependent]-=1
                    if not remaining[dependent]: ready.append(dependent)
            if visited!=len(ids): raise AtlasError("Cyclic task graph")
        elif target=="VERIFY":
            tasks=[json.loads(r[0]) for r in con.execute("SELECT value FROM tasks")]
            if not tasks: raise AtlasError("No research tasks")
            for t in tasks:
                if t["status"]!="done":
                    if t["status"] not in {"blocked","skipped"} or t.get("critical",True) or not t.get("decision_impact"):
                        raise AtlasError("Critical or unresolved task incomplete; record a justified noncritical block/skip and impact")
            for t in tasks:
                if t["status"]!="done": continue
                output=t.get("output") or {}
                if file_hash(confined(self.path,output.get("path",""),True))!=output.get("sha256"): raise AtlasError("Task output changed; reopen ORCHESTRATE and rerun affected plan")
                self._seal(state,output["path"],"VERIFY")
            cov=self.artifact("coverage.json"); rows=cov.get("items",[])
            required=self.artifact("protocol.json")["coverage"]
            if sorted(r.get("dimension","") for r in rows)!=sorted(required): raise AtlasError("Coverage does not match protocol")
            for row in rows:
                if row.get("status") not in {"covered","gap"}: raise AtlasError("Unassessed coverage")
                text_required(row,"basis")
                if row["status"]=="gap": text_required(row,"decision_impact")
            log=self.artifact("search_log.json")
            if not isinstance(log.get("queries"),list) or not log["queries"]: raise AtlasError("Search log required")
            for row in log["queries"]:
                for key in ["query","tool","at","outcome"]: text_required(row,key)
            text_required(cov,"stopping_decision")
            if strict: validate_coverage(self.artifact("protocol.json"),cov,log,self.artifact("evidence.json"),state.get("access_blocks",[]))
            for receipt in state.get("retrieval_receipts",[]):
                if receipt["purpose"]!="research": continue
                if file_hash(confined(self.path,receipt["artifact"],True))!=receipt["sha256"]:
                    raise AtlasError("Recorded retrieval output changed")
                if not any(row.get("retrieval_artifact")==receipt["artifact"] and row.get("query")==receipt["query"]
                           and row.get("plan_id")==receipt["plan_id"] for row in log["queries"]):
                    raise AtlasError("Search log omits a recorded research retrieval: "+receipt["id"])
        elif target=="SYNTHESIS":
            evidence=self.artifact("evidence.json"); result=validate_evidence(evidence,self.path)
            if strict and evidence.get("schema_version")!=2: raise AtlasError("Re-review legacy evidence under schema 2")
            if not result["ok"] or not result["metrics"].get("claims"): raise AtlasError("Evidence gate failed: "+canonical(result["errors"]))
            review=self.artifact("review.json")
            for k in ["reviewer","author","counterarguments","uncertainty","coverage_review","numeric_review","limitations"]: text_required(review,k)
            if review["reviewer"]==review["author"] or review.get("independent") is not True: raise AtlasError("Independent review required; identity is operator attestation")
            if review.get("decision") not in {"pass","conditional"} or review.get("unresolved_critical")!=[]: raise AtlasError("Critical audit failures unresolved or review list missing")
            if any(w["code"]=="stale" for w in result["warnings"]): text_required(review,"freshness_resolution")
            if strict:
                if review.get("evidence_sha256")!=digest(evidence): raise AtlasError("Final review is not bound to current evidence")
                if set(review.get("reviewed_claim_ids",[]))!={c["id"] for c in evidence["claims"] if c["material"]}:
                    raise AtlasError("Final reviewer must explicitly cover every material claim")
                text_required(review,"model_identity")
            for s in evidence["sources"]:
                self._seal(state,s["snapshot"],"SYNTHESIS")
            for c in evidence["calculations"]: self._seal(state,c["path"],"SYNTHESIS")
        elif target=="DELIVER":
            s=self.artifact("synthesis.json")
            for k in ["conclusion","tradeoffs","uncertainty","failure_conditions","strongest_counterargument"]: text_required(s,k)
            ids={c["id"] for c in self.artifact("evidence.json")["claims"]}
            if not isinstance(s.get("claim_ids"),list) or not s["claim_ids"] or any(k not in ids for k in s["claim_ids"]): raise AtlasError("Synthesis needs known claims")
        elif target=="MEMORY":
            d=self.artifact("deliverables.json")
            if not isinstance(d.get("files"),list) or not d["files"]: raise AtlasError("No deliverables")
            text_required(d,"contract_review")
            audited=set()
            for row in d["files"]:
                p=confined(self.path,row["path"],True)
                if p.stat().st_size==0 or file_hash(p)!=row.get("sha256"): raise AtlasError("Empty or altered deliverable")
                for key in ["format_review","citation_review"]: text_required(row,key)
                if strict:
                    if row.get("kind") not in {"report","artifact"}: raise AtlasError("Declare deliverable kind report or artifact")
                    if row["kind"]=="report":
                        from .verification import report_audit
                        if not isinstance(row.get("claim_ids"),list) or not row["claim_ids"]: raise AtlasError("Report claim_ids required")
                        text_path=p
                        if p.suffix.lower() not in {".md",".txt"}:
                            companion=row.get("audit_text",{})
                            text_path=confined(self.path,companion.get("path",""),True)
                            if file_hash(text_path)!=companion.get("sha256"): raise AtlasError("Report audit text changed")
                            self._seal(state,companion["path"],"MEMORY")
                        if text_path.stat().st_size>10_000_000: raise AtlasError("Report audit text exceeds 10 MB")
                        audit=report_audit(text_path.read_text(encoding="utf-8"),self.artifact("evidence.json"),
                                           required_claim_ids=row["claim_ids"])
                        if not audit["ok"]: raise AtlasError("Report citation audit failed: "+canonical(audit))
                        audited.update(audit["cited_claims"])
                self._seal(state,row["path"],"MEMORY")
            if strict:
                material={c["id"] for c in self.artifact("evidence.json")["claims"] if c["material"]}
                if not material<=audited: raise AtlasError("Deliverables omit material claims")
        elif target=="EVALUATE":
            l=self.artifact("lessons.json")
            if not isinstance(l.get("proposals"),list): raise AtlasError("Memory proposals list required (may be empty)")
            text_required(l,"outcome")
        elif target=="COMPLETE":
            e=self.artifact("evaluation.json")
            for key in ["criteria","results","failures","limitations","next_actions"]:
                if not e.get(key): raise AtlasError("Evaluation needs "+key)
            if e["criteria"]!=self.artifact("protocol.json")["evaluation_criteria"]: raise AtlasError("Evaluate the criteria predefined in the accepted protocol")
            if e.get("research_quality_proven") is not False: raise AtlasError("Do not claim research quality proven by local checks")

    def _seal(self,state,name,stage):
        state["seals"][name]={"sha256":file_hash(confined(self.path,name,True)),"stage":stage}

    def advance(self,target):
        if target not in STATES: raise AtlasError("Unknown target state")
        with self.connection(True) as con:
            state=self._state(con); self._active(state); self._seals(state)
            if target==state["state"]: return state # idempotent, after integrity check
            stages=STATES if state["schema_version"]>=2 else [s for s in STATES if s!="ENABLEMENT"]
            if target not in stages or stages.index(target)!=stages.index(state["state"])+1: raise AtlasError("State transitions must be sequential")
            self._gate(target,state,con)
            for name in ARTIFACTS.get(target,[]): self._seal(state,name,target)
            if target=="RESEARCH":
                con.execute("DELETE FROM tasks")
                for t in self.artifact("plan.json")["tasks"]:
                    row=dict(t,status="pending",attempts=0,output=None)
                    con.execute("INSERT OR REPLACE INTO tasks VALUES (?,?)",(t["id"],canonical(row)))
            state["state"]=target
            self._save(con,state,"transition",{"target":target,"seals":state["seals"]})
        self.checkpoint()
        return self.status()

    def reopen(self,target,reason):
        if target not in STATES or not reason.strip(): raise AtlasError("Known target and reason required")
        with self.connection(True) as con:
            state=self._state(con)
            self._active(state)
            if STATES.index(target)>=STATES.index(state["state"]): raise AtlasError("Reopen must go to an earlier stage")
            # Artifacts from earlier completed gates remain sealed; target work and later work must be rerun.
            state["seals"]={k:v for k,v in state["seals"].items() if STATES.index(v["stage"])<=STATES.index(target)}
            if target=="INTAKE": state["seals"]={}
            if target=="INTAKE": state.pop("access",None)
            if target=="INTAKE": state.pop("enablement",None)
            if STATES.index(target)<STATES.index("RESEARCH"): con.execute("DELETE FROM tasks")
            state["state"]=target
            self._save(con,state,"reopened",{"target":target,"reason":reason})
        return self.status()

    def task(self,taskid,status,output=None,reason=None):
        if status not in {"running","done","failed","pending","blocked","skipped"}: raise AtlasError("Unknown task state")
        with self.connection(True) as con:
            state=self._state(con)
            self._active(state)
            if state["state"]!="RESEARCH": raise AtlasError("Tasks run only during RESEARCH")
            self._seals(state)
            if state["schema_version"]>=2:
                self._enablement(state); self._access(state,ready=True)
            row=con.execute("SELECT value FROM tasks WHERE id=?",(taskid,)).fetchone()
            if not row: raise AtlasError("Unknown task")
            task=json.loads(row[0])
            if status==task["status"]: return task
            allowed={"pending":{"running","skipped","blocked"},"running":{"done","failed","blocked"},
                     "failed":{"pending","blocked"},"done":set(),"blocked":set(),"skipped":set()}
            if status not in allowed[task["status"]]: raise AtlasError("Invalid task transition")
            if status=="running":
                if state["schema_version"]>=2:
                    approved={d["need_id"] for d in state["access"]["decisions"] if d["decision"]=="use"}
                    if not set(task.get("access_need_ids",[]))<=approved:
                        raise AtlasError("Task access capability was deferred or is no longer approved; amend the task plan")
                if task["attempts"]>=3: raise AtlasError("Retry limit reached; amend the plan after review")
                for dep in task["depends_on"]:
                    d=json.loads(con.execute("SELECT value FROM tasks WHERE id=?",(dep,)).fetchone()[0])
                    if d["status"]!="done": raise AtlasError("Dependencies incomplete")
                task["attempts"]+=1
            if status in {"blocked","skipped"}:
                if not isinstance(reason,str) or not reason.strip(): raise AtlasError("Block/skip requires decision-impact reason")
                task["decision_impact"]=reason
                if status=="blocked" and state["schema_version"]>=2 and task.get("critical",True):
                    state["hold"]={"kind":"blocked","category":"task","task_id":taskid,"reason":reason,"at":now()}
            if status=="failed":
                task["failure_reason"]=reason or "Failure recorded without external execution details"
            if status=="running": task["started_at"]=now()
            if status=="done":
                p=confined(self.path,output or "",True)
                if not p.stat().st_size: raise AtlasError("Empty task output")
                if state["schema_version"]>=2: validate_handoff(read_json(p),taskid)
                task["output"]={"path":output,"sha256":file_hash(p)}
                self._seal(state,output,"VERIFY")
            task["status"]=status; task["updated_at"]=now()
            con.execute("UPDATE tasks SET value=? WHERE id=?",(canonical(task),taskid))
            self._save(con,state,"task",{"id":taskid,"status":status})
        return task

    def migrate(self,archive,authorization,quiesced=False):
        from .project_archive import backup
        text_required({"authorization":authorization},"authorization")
        before=self.status()
        self._active(before)
        if before["schema_version"]!=1: raise AtlasError("Only legacy schema 1 projects need migration")
        with self.connection() as con: self._seals(self._state(con))
        receipt=backup(self.path,archive,quiesced=quiesced)
        with self.connection(True) as con:
            state=self._state(con); self._active(state)
            if state["revision"]!=before["revision"]: raise AtlasError("Project changed during migration backup; stop writers and retry")
            previous=state["state"]
            state["schema_version"]=2
            state["state"]="INTAKE" if previous=="INTAKE" else "MANDATE"
            state["seals"]={k:v for k,v in state["seals"].items() if k=="mandate.json"}
            state["migration"]={"from_schema":1,"backup":receipt,"authorization":authorization,"previous_state":previous,
                                "preserved_tasks":before["tasks"],
                                "limitations":"Existing files retained unchanged, not recertified. Rebuild access/protocol and re-review evidence under schema 2."}
            state.pop("access",None)
            state.pop("enablement",None)
            con.execute("DELETE FROM tasks")
            self._save(con,state,"migrated",state["migration"])
        self.checkpoint()
        return self.status()

    def dispatch_context(self,max_workers=4):
        with self.connection() as con:
            state=self._state(con); self._active(state); self._seals(state)
            if state["state"]!="RESEARCH": raise AtlasError("Dispatch planning requires active RESEARCH")
            if state["schema_version"]>=2:
                features,approval=self._enablement(state); self._access(state,ready=True)
                if max_workers>1:
                    decision=next(d for d in approval["decisions"] if d["feature_id"]=="subagents")
                    if features["subagents"]["status"]!="enabled" or decision["decision"]!="use":
                        raise AtlasError("Parallel delegation requires observed enabled subagents and explicit approved use; request enablement or use --max-workers 1 under the accepted limitation")
            return dict(state,tasks=[parse_json(row[0]) for row in con.execute("SELECT value FROM tasks ORDER BY id")])

    def record_cost(self,costid,amount,note):
        amount=nonnegative(amount)
        if not costid.strip() or not note.strip(): raise AtlasError("Cost ID and note required")
        with self.connection(True) as con:
            state=self._state(con); row=con.execute("SELECT amount,note FROM costs WHERE id=?",(costid,)).fetchone()
            self._active(state)
            self._seals(state)
            if STATES.index(state["state"])<STATES.index("MANDATE"): raise AtlasError("An accepted mandate is required before recording cost")
            if row:
                if D(row[0])!=amount or row[1]!=note: raise AtlasError("Idempotency key reused with different cost")
                return
            budget=nonnegative(self.artifact("mandate.json")["paid_budget"])
            spent=sum((D(r[0]) for r in con.execute("SELECT amount FROM costs")),D(0))
            if spent+amount>budget: raise AtlasError("Declared budget exceeded; no external service call is made by this ledger")
            con.execute("INSERT INTO costs VALUES (?,?,?)",(costid,str(amount),note))
            self._save(con,state,"cost_recorded",{"id":costid,"amount":str(amount)})

    def validate(self):
        with self.connection() as con:
            state=self._state(con); self._seals(state)
            result=validate_evidence(self.artifact("evidence.json"),self.path)
            return {"state":state["state"],"event_chain":"consistent","sealed_artifacts":len(state["seals"]),"evidence":result,
                    "warning":"Receipts detect accidental changes, not a malicious filesystem owner. No external truth or model compliance guaranteed."}

    def checkpoint(self):
        with self.connection() as con:
            seq=con.execute("SELECT max(seq) FROM events").fetchone()[0]
            dest=confined(self.path,f"checkpoints/state-{seq:06d}.sqlite3")
            backup=sqlite3.connect(dest)
            try: con.backup(backup)
            finally: backup.close()
            atomic_json(dest.with_suffix(".json"),{"database_sha256":file_hash(dest),"sequence":seq,"created_at":now()})
        return str(dest.relative_to(self.path))

    @classmethod
    def restore(cls,root,slug,checkpoint):
        path=project_path(root,slug); src=confined(path,checkpoint,True)
        if src.parent!=path/"checkpoints" or src.suffix!=".sqlite3": raise AtlasError("Choose a recorded database checkpoint")
        receipt=read_json(src.with_suffix(".json"))
        if file_hash(src)!=receipt["database_sha256"]: raise AtlasError("Checkpoint hash mismatch")
        con=sqlite3.connect(src)
        try:
            if con.execute("PRAGMA integrity_check").fetchone()[0]!="ok": raise AtlasError("Invalid checkpoint")
            # Validate chain and state before replacing anything.
            temp=object.__new__(cls); temp._check_log(con)
        finally: con.close()
        db=confined(path,"state.sqlite3",True)
        quarantine=path/("state-before-restore-"+now().replace(":","-")+".sqlite3")
        shutil.copy2(db,quarantine); shutil.copy2(src,db)
        p=cls(root,slug)
        with p.connection(True) as con:
            state=p._state(con)
            if not state.get("hold"):
                state["hold"]={"kind":"blocked","category":"recovery","at":now(),
                               "reason":"Checkpoint restored. Reconcile interrupted jobs, access blocks and approvals from later history; obtain explicit user authorization before continuing."}
            p._save(con,state,"restored",{"checkpoint":checkpoint})
        return p.status()
