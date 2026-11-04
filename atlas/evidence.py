"""Mechanical provenance checks. A passed check does not establish semantic truth."""
from urllib.parse import urlparse
import ipaddress
from .io import AtlasError, confined, file_hash, date, now, read_json, digest
from .quant import run_analysis, D
from .sourcegraph import group_origins
from .verification import assessment_binds


def validate_evidence(data, root, as_of=None):
    try:
        return _validate_evidence(data,root,as_of)
    except (TypeError,KeyError,AttributeError,ValueError) as e:
        return {"ok":False,"errors":[{"code":"schema","path":"$","message":"Malformed nested evidence: "+str(e)}],"warnings":[],"metrics":{}}


def _validate_evidence(data, root, as_of=None):
    errors=[]; warnings=[]; sources={}; claims={}; texts={}; groups=set(); assessed=set()
    def err(code,path,message): errors.append({"code":code,"path":path,"message":message})
    def warn(code,path,message): warnings.append({"code":code,"path":path,"message":message})
    current=date(as_of or now())
    if not isinstance(data,dict): return {"ok":False,"errors":[{"code":"schema","path":"$","message":"Expected object"}],"warnings":[],"metrics":{}}
    if data.get("schema_version") not in {1,2}: err("schema","schema_version","Expected supported evidence schema 1 or 2")
    strict=data.get("schema_version")==2
    for key in ["sources","claims","assessments","calculations"]:
        if not isinstance(data.get(key),list): err("schema",key,"Expected list")
    if errors: return {"ok":False,"errors":errors,"warnings":warnings,"metrics":{}}
    for i,s in enumerate(data["sources"]):
        path=f"sources[{i}]"
        if not isinstance(s,dict): err("schema",path,"Expected object"); continue
        sid=s.get("id")
        if not isinstance(sid,str) or not sid.strip() or sid in sources: err("source_id",path,"Missing or duplicate ID"); continue
        sources[sid]=s
        for key in ["url","title","accessed_at","origin_group","snapshot","sha256"]:
            if not isinstance(s.get(key),str) or not s[key].strip(): err("source_field",path,key+" missing")
        try:
            u=urlparse(s.get("url","")); host=(u.hostname or "").rstrip(".")
            local=s.get("source_type")=="local"
            invalid=u.scheme not in {"https","http"} or not host or u.username is not None
            invalid=invalid or host.endswith((".invalid",".test",".example",".localhost")) or host in {"localhost","example.com","example.org","example.net"}
            try: invalid=invalid or not ipaddress.ip_address(host).is_global
            except ValueError: pass
            if local:
                if u.scheme!="local" or not isinstance(s.get("provenance_note"),str) or not s["provenance_note"].strip():
                    err("local_provenance",path,"Local evidence requires local: identifier and explicit provenance note")
                warn("local_source",path,"Local evidence is user/fixture supplied; authenticity requires independent review")
            elif invalid: err("source_url",path,"URL not eligible as public external evidence")
            accessed=date(s.get("accessed_at"))
            if accessed>current: err("future_access",path,"Access date is in future")
            if s.get("published_at") and date(s["published_at"])>accessed: err("date_order",path,"Publication after access")
            if s.get("expires_at") and date(s["expires_at"])<current: warn("stale",path,"Evidence freshness window expired")
            p=confined(root,s.get("snapshot",""),True)
            if p.stat().st_size>10_000_000: raise AtlasError("Snapshot exceeds 10 MB")
            if file_hash(p)!=s.get("sha256"): err("snapshot_hash",path,"Snapshot altered")
            texts[sid]=p.read_text(encoding="utf-8")
            if isinstance(s.get("origin_group"),str): groups.add(s["origin_group"])
        except (AtlasError,OSError,UnicodeError,TypeError,ValueError) as e: err("source_artifact",path,str(e))
    hashes={}
    for sid,s in sources.items():
        h=s.get("sha256")
        if not isinstance(h,str): continue
        if h in hashes:
            warn("duplicate_content",sid,"Same bytes as "+hashes[h]+"; not independent evidence")
            if s.get("origin_group")!=sources[hashes[h]].get("origin_group"):
                err("origin_mismatch",sid,"Identical content assigned different origin groups")
        hashes[h]=sid
    for i,c in enumerate(data["claims"]):
        path=f"claims[{i}]"
        if not isinstance(c,dict): err("schema",path,"Expected object"); continue
        cid=c.get("id")
        if not isinstance(cid,str) or not cid.strip() or cid in claims: err("claim_id",path,"Missing or duplicate ID"); continue
        claims[cid]=c
        if not isinstance(c.get("text"),str) or not c["text"].strip(): err("claim_text",path,"Missing atomic claim")
        if c.get("kind") not in {"factual","numeric","inference"}: err("claim_kind",path,"Unknown kind")
        if type(c.get("material")) is not bool: err("claim_material",path,"material must be boolean")
        if c.get("kind")=="numeric":
            try:
                D(c.get("numeric_value"))
                if not isinstance(c.get("units"),str) or not c["units"].strip(): raise AtlasError("Numeric claim units required")
            except AtlasError as e: err("numeric_value",path,str(e))
        if "reported_statistic" in c and type(c["reported_statistic"]) is not bool: err("reported_statistic",path,"reported_statistic must be boolean")
        if not isinstance(c.get("author"),str) or not c["author"].strip(): err("claim_author",path,"Author required")
        refs=c.get("source_ids")
        if not isinstance(refs,list) or not refs or any(not isinstance(s,str) or s not in sources for s in refs): err("claim_sources",path,"Valid nonempty source references required")
        elif len(set(refs))!=len(refs): err("claim_sources",path,"Duplicate source reference")
        if strict:
            if not isinstance(c.get("scope"),str) or not c["scope"].strip(): err("claim_scope",path,"Explicit population, geography and time scope required")
            uncertainty=c.get("uncertainty",{})
            if not isinstance(uncertainty,dict) or uncertainty.get("level") not in {"low","medium","high","unknown"}:
                err("uncertainty",path,"Uncertainty level must be low/medium/high/unknown, not an invented probability")
            elif (not isinstance(uncertainty.get("basis"),str) or not uncertainty["basis"].strip()
                  or not isinstance(uncertainty.get("limitations"),list) or not uncertainty["limitations"]
                  or any(not isinstance(x,str) or not x.strip() for x in uncertainty["limitations"])):
                err("uncertainty",path,"Uncertainty needs a basis and explicit limitations")
    try:
        graph=group_origins(list(sources.values()))
    except AtlasError as e:
        err("lineage","sources",str(e)); graph={"distinct_origin_clusters":0,"untraced_source_ids":[]}
    for i,a in enumerate(data["assessments"]):
        path=f"assessments[{i}]"
        if not isinstance(a,dict): err("schema",path,"Expected object"); continue
        cid,sid=a.get("claim_id"),a.get("source_id")
        if not isinstance(cid,str) or not isinstance(sid,str): err("assessment_ref",path,"References must be strings"); continue
        if cid not in claims or sid not in sources: err("assessment_ref",path,"Unresolved claim/source"); continue
        if sid not in claims[cid].get("source_ids",[]): err("assessment_ref",path,"Source not attached to claim")
        if a.get("verdict") not in {"supports","contradicts","insufficient"}: err("assessment_verdict",path,"Unknown verdict")
        excerpt=a.get("excerpt")
        if not isinstance(excerpt,str) or not excerpt.strip() or excerpt not in texts.get(sid,""): err("excerpt_match",path,"Exact excerpt absent from snapshot")
        for k in ["locator","reasoning","reviewer"]:
            if not isinstance(a.get(k),str) or not a[k].strip(): err("assessment_field",path,k+" required")
        if a.get("reviewer_type") not in {"human","model"}: err("reviewer_type",path,"Must be human or model")
        if type(a.get("independent")) is not bool: err("reviewer_independence",path,"Boolean independence required")
        if a.get("independent") and a.get("reviewer")==claims[cid].get("author"): err("self_review",path,"Same author and reviewer")
        try:
            reviewed=date(a.get("reviewed_at"))
            if reviewed>current: err("future_review",path,"Review in future")
            if strict and reviewed<date(sources[sid].get("accessed_at")): err("review_date",path,"Review predates source access")
        except AtlasError: err("review_date",path,"Invalid review date")
        bound=assessment_binds(a,claims[cid],sources,strict)
        if strict and not bound: err("review_binding",path,"Review must bind the current claim revision and snapshot hash, with a distinct reviewer")
        if a.get("verdict")=="supports" and a.get("independent") is True and bound: assessed.add(cid)
        if a.get("verdict")=="contradicts" and (not isinstance(claims[cid].get("resolution"),str) or not claims[cid]["resolution"].strip()):
            err("unresolved_contradiction",path,"Material contradiction needs explicit adjudication or conditional scope")
    calculated=set()
    for i,calc in enumerate(data["calculations"]):
        path=f"calculations[{i}]"
        try:
            if not isinstance(calc,dict): raise AtlasError("Expected calculation object")
            p=confined(root,calc["path"],True)
            if file_hash(p)!=calc["sha256"]: raise AtlasError("Calculation artifact altered")
            item=read_json(p)
            expected=run_analysis(item["input"],engine=item["result"].get("engine"))
            if canonical_output(expected)!=canonical_output(item["result"]): raise AtlasError("Calculation does not reproduce")
            if not isinstance(calc.get("claim_ids"),list) or not calc["claim_ids"]: raise AtlasError("Calculation needs a nonempty claim list")
            for cid in calc["claim_ids"]:
                if cid not in claims: raise AtlasError("Unknown calculation claim")
            for binding in calc.get("bindings",[]):
                cid=binding["claim_id"]
                if cid not in calc["claim_ids"]: raise AtlasError("Binding not in calculation claim list")
                pointer=binding["pointer"]
                if not isinstance(pointer,str) or not pointer.startswith("/"): raise AtlasError("Binding needs JSON pointer into result")
                value=item["result"]
                for part in pointer[1:].split("/"):
                    part=part.replace("~1","/").replace("~0","~")
                    value=value[int(part)] if isinstance(value,list) else value[part]
                if D(value)!=D(claims[cid]["numeric_value"]): raise AtlasError("Claim numeric value differs from reproduced output")
                if binding.get("units")!=claims[cid].get("units") or not binding.get("units"): raise AtlasError("Claim/binding units disagree")
                if binding["units"]!=expected["output_units"].get(pointer): raise AtlasError("Claim units do not match the calculation output unit map")
                calculated.add(cid)
        except (AtlasError,KeyError,TypeError,OSError,ValueError,IndexError) as e: err("calculation",path,str(e))
    for cid,c in claims.items():
        if c.get("material") and cid not in assessed: err("unreviewed_claim",cid,"Material claim lacks an independent supporting assessment")
        if c.get("kind")=="numeric" and cid not in calculated and not c.get("reported_statistic"):
            err("numeric_artifact",cid,"Derived numeric claim requires reproducible calculation; reported statistics must be explicitly labeled")
    if not claims: warn("empty", "$", "No claims; research completion cannot pass")
    warn("semantic_limit","$","Excerpts, identities, origin groups and URLs remain operator supplied. Matching text and arithmetic do not prove entailment, authenticity, or completeness.")
    if not strict: warn("legacy_contract","$","Legacy evidence lacks mandatory revision-bound review and structured uncertainty; migrate and re-review before claiming schema 2 controls.")
    return {"ok":not errors,"verification_level":"mechanical_consistency_only","errors":errors,"warnings":warnings,"metrics":{"sources":len(sources),"claims":len(claims),"origin_groups":len(groups),"origin_clusters":graph["distinct_origin_clusters"],"independently_assessed":len(assessed),"reproduced_numeric_claims":len(calculated)}}


def canonical_output(value):
    return digest(value)
