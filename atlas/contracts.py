"""Versioned research contracts: observable accounting, not semantic certification."""
import re
from .access import string_list
from .io import AtlasError, date, now, text_required
from .sourcegraph import group_origins


def validate_protocol(protocol, access_needs):
    if protocol.get("schema_version")!=2: raise AtlasError("New projects require protocol schema 2")
    dimensions=string_list(protocol.get("coverage"),"Protocol coverage")
    for key in ("freshness_policy","uncertainty_policy","synthesis_method"):
        text_required(protocol,key)
    string_list(protocol.get("bias_controls"),"Bias controls")
    plans=protocol.get("search_plan")
    if not isinstance(plans,list) or not plans: raise AtlasError("Structured search plan required")
    ids=set(); strategies={d:set() for d in dimensions}
    for row in plans:
        pid=text_required(row,"id")
        if pid in ids: raise AtlasError("Duplicate planned search ID")
        ids.add(pid)
        text_required(row,"query")
        if row.get("dimension") not in strategies: raise AtlasError("Search dimension not in protocol")
        if row.get("strategy") not in {"primary","counterevidence","background","replication"}:
            raise AtlasError("Unknown search strategy")
        strategies[row["dimension"]].add(row["strategy"])
        if row.get("access_need_id") not in access_needs: raise AtlasError("Search requires a planned access capability")
    if any(not {"primary","counterevidence"}<=s for s in strategies.values()):
        raise AtlasError("Plan primary-source and counterevidence searches for every dimension")
    bounds=protocol.get("stopping_criteria",{})
    for key,maximum in (("max_queries",10000),("min_sources_per_dimension",1000),
                        ("min_independent_origins",1000),("consecutive_no_new",1000)):
        if type(bounds.get(key)) is not int or not 1<=bounds[key]<=maximum:
            raise AtlasError("Invalid stopping criterion: "+key)
    if bounds["max_queries"]<len(plans): raise AtlasError("Query budget cannot cover the planned searches")
    return {row["id"]:row for row in plans}


def validate_coverage(protocol, coverage, log, evidence, access_blocks):
    plans={row["id"]:row for row in protocol["search_plan"]}
    sources={row["id"]:row for row in evidence["sources"]}
    rows=log.get("queries")
    if not isinstance(rows,list) or not rows: raise AtlasError("Nonempty structured search log required")
    if len(rows)>protocol["stopping_criteria"]["max_queries"]:
        raise AtlasError("Search budget exceeded; amend the protocol transparently")
    logged={}; executed=set(); encountered=set(); novelty=[]
    blocks={row["id"]:row for row in access_blocks}
    for row in rows:
        qid=text_required(row,"id")
        if qid in logged: raise AtlasError("Duplicate search log ID")
        logged[qid]=row
        plan=plans.get(row.get("plan_id"))
        if not plan: raise AtlasError("Unplanned search; amend the protocol before including it")
        executed.add(row["plan_id"])
        for key in ("query","tool","at","outcome"): text_required(row,key)
        if date(row["at"])>date(now()): raise AtlasError("Future search observation")
        if row.get("status") not in {"complete","blocked"}: raise AtlasError("Unknown search completion status")
        if row["status"]=="blocked":
            block=blocks.get(row.get("access_block_id"),{})
            if block.get("disposition")!="user_accepted_gap":
                raise AtlasError("Blocked search requires recorded user-authorized continuation")
        retrieved=set(string_list(row.get("retrieved_ids"),"Retrieved IDs",False))
        included=set(string_list(row.get("included_ids"),"Included IDs",False))
        excluded=row.get("exclusions")
        if not isinstance(excluded,list): raise AtlasError("Explicit exclusion accounting required")
        excluded_ids=[]
        for item in excluded:
            excluded_ids.append(text_required(item,"id")); text_required(item,"reason")
        if len(excluded_ids)!=len(set(excluded_ids)): raise AtlasError("Duplicate excluded record")
        if included & set(excluded_ids) or included | set(excluded_ids)!=retrieved:
            raise AtlasError("Every retrieved record must be included or explicitly excluded exactly once")
        if not included<=sources.keys(): raise AtlasError("Included record lacks a registered source")
        novelty.append(len(included-encountered)); encountered.update(included)
    dimensions=set()
    for row in coverage.get("items",[]):
        dimension=row.get("dimension")
        if dimension not in protocol["coverage"] or dimension in dimensions:
            raise AtlasError("Duplicate or unknown coverage dimension")
        dimensions.add(dimension)
        text_required(row,"basis")
        if row.get("status") not in {"covered","gap"}: raise AtlasError("Unknown coverage status")
        search_ids=string_list(row.get("search_ids"),"Coverage search references")
        if any(q not in logged or plans[logged[q]["plan_id"]]["dimension"]!=dimension for q in search_ids):
            raise AtlasError("Coverage cites an unknown or unrelated search")
        source_ids=string_list(row.get("source_ids"),"Coverage sources",False)
        found={sid for q in search_ids for sid in logged[q]["included_ids"]}
        if not set(source_ids)<=found: raise AtlasError("Coverage source was not included in its cited searches")
        if row["status"]=="covered":
            selected=[sources[sid] for sid in source_ids]
            graph=group_origins(evidence["sources"])
            independent=sum(any(sid in source_ids and sources[sid].get("origin_group") for sid in cluster)
                            for cluster in graph["groups"])
            criteria=protocol["stopping_criteria"]
            if len(selected)<criteria["min_sources_per_dimension"] or independent<criteria["min_independent_origins"]:
                raise AtlasError("Coverage falls below the predefined source/origin threshold")
        else: text_required(row,"decision_impact")
    if dimensions!=set(protocol["coverage"]): raise AtlasError("Coverage does not match protocol")
    text_required(coverage,"stopping_decision")
    reason=coverage.get("stopping_reason")
    if reason=="plan_complete":
        if executed!=set(plans): raise AtlasError("Unexecuted planned searches remain")
    elif reason=="saturation":
        count=protocol["stopping_criteria"]["consecutive_no_new"]
        completed_plans={row["plan_id"] for row in rows if row["status"]=="complete"}
        if len(novelty)<count or any(novelty[-count:]) or completed_plans!=set(plans):
            raise AtlasError("Saturation requires all planned searches and the declared no-new-source window")
        if any(row["status"]!="complete" for row in rows[-count:]):
            raise AtlasError("Blocked access is not a saturation observation")
    elif reason=="authorized_limit":
        text_required(coverage,"user_authorization")
        if any(row["status"]!="gap" for row in coverage["items"] if
               any(p["dimension"]==row["dimension"] and p["id"] not in executed for p in plans.values())):
            raise AtlasError("Unsearched dimensions must remain gaps")
    else: raise AtlasError("Record plan_complete, saturation or authorized_limit stopping reason")
    return {"queries":len(rows),"included_sources":len(encountered),"new_sources_per_query":novelty}


def validate_handoff(item, task_id):
    if not isinstance(item,dict) or item.get("task_id")!=task_id:
        raise AtlasError("Task output requires a matching task_id")
    text_required(item,"summary")
    execution=item.get("execution")
    for key in ("executor","kind","model_selection","model_identity","observed_at"):
        text_required(execution,key)
    if execution["kind"] not in {"synthetic","local-code","research"}:
        raise AtlasError("Unknown execution kind")
    if date(execution["observed_at"])>date(now()): raise AtlasError("Future execution receipt")
    string_list(execution.get("tools"),"Observed execution tools",False)
    for key in ("source_ids","limitations","unresolved"):
        string_list(item.get(key),"Task "+key,False)
    return item
