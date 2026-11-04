"""Topic-specific access planning and operator-recorded authorization contracts.

These controls do not configure MCP servers or intercept external Copilot tools.
"""
import re
from urllib.parse import urlsplit
from .io import AtlasError, date, now, text_required


class AccessBlocked(AtlasError):
    def __init__(self, resource, operation, reason, quality_impact, need_id=None):
        self.resource=resource
        self.operation=operation
        self.reason=reason
        self.quality_impact=quality_impact
        self.need_id=need_id
        super().__init__(f"Access blocked: {resource}: {reason}. Stop and obtain explicit user authorization.")


def string_list(value, label, nonempty=True):
    if (not isinstance(value,list) or (nonempty and not value)
            or any(not isinstance(x,str) or not x.strip() for x in value)
            or len(set(value))!=len(value)):
        raise AtlasError(label+" must be a unique list of nonempty strings")
    return value


def validate_plan(plan, question):
    if not isinstance(plan,dict) or plan.get("schema_version")!=1:
        raise AtlasError("Access plan schema_version must be 1")
    if plan.get("question")!=question:
        raise AtlasError("Access plan must address the current inquiry exactly")
    text_required(plan,"selection_reason")
    dimensions=string_list(plan.get("coverage"),"Access coverage")
    needs=plan.get("needs")
    if not isinstance(needs,list) or not needs:
        raise AtlasError("Plan at least one access need, including local tools when no MCP is needed")
    ids=set(); covered=set()
    for need in needs:
        nid=text_required(need,"id")
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}",nid) or nid in ids:
            raise AtlasError("Invalid or duplicate access need ID")
        ids.add(nid)
        if need.get("kind") not in {"mcp","builtin","local","manual"}:
            raise AtlasError("Unknown access kind")
        for key in ("name","purpose","endpoint","data_shared","privacy","cost","alternatives","quality_impact"):
            text_required(need,key)
        for key in ("required","paid"):
            if type(need.get(key)) is not bool: raise AtlasError("Access "+key+" must be boolean")
        string_list(need.get("permissions"),"Permissions")
        covered.update(string_list(need.get("coverage"),"Need coverage"))
        if any(x not in dimensions for x in need["coverage"]):
            raise AtlasError("Need refers to unknown coverage")
        endpoint=urlsplit(need["endpoint"])
        if endpoint.username is not None or endpoint.password is not None or endpoint.query or endpoint.fragment:
            raise AtlasError("Access endpoints must not contain credentials, queries or fragments")
        if need["kind"]=="mcp":
            text_required(need,"publisher")
            url=urlsplit(text_required(need,"verification_url"))
            if url.scheme!="https" or not url.hostname or url.username or url.password:
                raise AtlasError("MCP publisher verification requires a public official HTTPS reference")
            if date(need.get("publisher_verified_at"))>date(now()):
                raise AtlasError("Publisher verification cannot be in the future")
    if covered!=set(dimensions): raise AtlasError("Every access coverage dimension needs a planned capability")
    return {row["id"]:row for row in needs}


def validate_decisions(needs, decisions):
    if not isinstance(decisions,list): raise AtlasError("Access decisions must be a list")
    seen=set()
    for row in decisions:
        nid=text_required(row,"need_id")
        if nid not in needs or nid in seen: raise AtlasError("Unknown or duplicate access decision")
        seen.add(nid)
        if row.get("decision") not in {"use","defer"}: raise AtlasError("Access decision must be use or defer")
        text_required(row,"reason")
        if row["decision"]=="defer": text_required(row,"quality_impact")
        if row["decision"]=="use" and needs[nid]["paid"] and row.get("paid_approved") is not True:
            raise AtlasError("Paid access requires separate explicit approval")
    if seen!=set(needs): raise AtlasError("User must decide every proposed access need")
    return decisions


def recommend_needs(question, domain):
    """Planning prompts, not a claimed exhaustive/live MCP registry."""
    if not isinstance(question,str) or not question.strip(): raise AtlasError("Inquiry required")
    common=[
        ("primary_sources","Original authoritative documents, exact passages and counterevidence"),
        ("local_analysis","Reproducible calculations, data inspection and citation/evidence checks"),
    ]
    specialized={
        "science":[("scholarly_metadata","Literature discovery, citation chasing and correction/retraction checks"),
                   ("full_text","Original methods, results, supplements and risk-of-bias assessment")],
        "technology":[("official_docs_code","Versioned official specifications, code, issues and executable examples"),
                      ("scholarly_metadata","Relevant research and independent evaluations")],
        "finance":[("filings","Original regulatory filings, audited accounts and definitions"),
                   ("market_data","Licensed point-in-time prices, series, currencies and revisions")],
        "markets":[("official_statistics","Population, demand and trade data with dates and denominators")],
        "commerce":[("commerce_data","Authorized catalog, fee, order, return and customer data")],
        "amazon":[("marketplace_data","Authorized marketplace data, fees and applicable policies")],
        "opportunity":[("market_validation","Independent demand, alternatives and failure/base-rate evidence")],
        "general":[("topic_specific_sources","Identify the field's authoritative sources and missing access")],
    }
    if domain not in specialized: raise AtlasError("Unknown domain")
    return {"question":question,"domain":domain,
            "candidate_capabilities":[{"capability":key,"purpose":purpose} for key,purpose in common+specialized[domain]],
            "required_next_action":"Copilot must tailor this list to the inquiry, verify candidate publishers/endpoints, compare existing tools with MCP alternatives, write access_plan.json, and ask the user to connect/approve before research.",
            "limitations":"Offline planning aid, not exhaustive discovery or proof any server exists, is connected, authenticated or suitable. Do not install or connect anything automatically."}
