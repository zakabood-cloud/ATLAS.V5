"""Citation coverage and review bindings, never a semantic truth oracle."""
import re
from .io import AtlasError, confined, file_hash, read_json, digest

MARKER=re.compile(r"\[\[claim:([A-Za-z0-9_.:-]+)\]\]")


def assessment_binds(assessment,claim,sources,strict=False):
    sid=assessment.get("source_id")
    if (sid not in sources or sid not in claim.get("source_ids",[])
            or not assessment.get("reviewer") or assessment.get("reviewer")==claim.get("author")):
        return False
    return not strict or (assessment.get("claim_sha256")==digest(claim)
                          and assessment.get("snapshot_sha256")==sources[sid].get("sha256"))


def report_audit(report_text,evidence,strict=True,required_claim_ids=None):
    if not isinstance(report_text,str) or not report_text.strip(): raise AtlasError("Nonempty report text required")
    claims={c["id"]:c for c in evidence.get("claims",[])}
    if len(claims)!=len(evidence.get("claims",[])): raise AtlasError("Duplicate claim IDs")
    sources={s["id"]:s for s in evidence.get("sources",[])}
    required={cid for cid,c in claims.items() if c.get("material")} if required_claim_ids is None else set(required_claim_ids)
    if not required<=claims.keys(): raise AtlasError("Report requires unknown claims")
    supported=set()
    for assessment in evidence.get("assessments",[]):
        cid=assessment.get("claim_id")
        if (cid in claims and assessment.get("verdict")=="supports" and assessment.get("independent") is True
                and assessment_binds(assessment,claims[cid],sources,evidence.get("schema_version")==2)):
            supported.add(cid)
    seen=set(); errors=[]; warnings=[]; unmarked=[]; fenced=False
    for number,line in enumerate(report_text.splitlines(),1):
        if line.lstrip().startswith(("```","~~~")):
            fenced=not fenced; continue
        if fenced: continue
        matches=MARKER.findall(line); seen.update(matches)
        text=re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|>\s*)","",line).strip()
        structure=not text or text.startswith("#") or bool(re.fullmatch(r"[\s|:=-]+",text))
        if not structure and not matches:
            words=re.findall(r"\b[\w'-]+\b",text)
            factual=re.search(r"\b(is|are|was|were|has|have|increased|decreased|costs|shows|indicates|reports|proves)\b|\d",text,re.I)
            if factual and (len(words)>=5 or (line.lstrip().startswith("|") and len(words)>=2)):
                unmarked.append(number)
        for cid in matches:
            if cid not in claims: errors.append({"line":number,"code":"unknown_claim","id":cid})
            elif claims[cid].get("material") and cid not in supported:
                errors.append({"line":number,"code":"unsupported_material_claim","id":cid})
    for cid in sorted(required-seen):
        (errors if strict else warnings).append({"code":"material_claim_not_cited","id":cid})
    if unmarked:
        warnings.append({"code":"possibly_uncited_sentences","lines":unmarked,
                         "note":"Includes bullets, quotes and tables; heuristic findings need substantive review"})
    return {"ok":not errors and (not strict or not unmarked),"errors":errors,"warnings":warnings,
            "cited_claims":sorted(seen),"claim_count":len(claims),
            "verification_level":"citation_coverage_only_not_semantic_truth",
            "limitations":"Markers do not prove entailment. Headings, code blocks and unrecognized factual phrasing still require independent review."}


def validate_review_receipts(project,evidence,receipts):
    if not isinstance(receipts,list): raise AtlasError("Expected review receipts")
    claims={c["id"]:c for c in evidence.get("claims",[])}
    sources={s["id"]:s for s in evidence.get("sources",[])}
    errors=[]; reviewed=set()
    for index,row in enumerate(receipts):
        try:
            if not isinstance(row,dict): raise AtlasError("Invalid review record")
            for key in ("claim_id","reviewer","model_or_human","verdict","rationale","artifact","sha256"):
                if not isinstance(row.get(key),str) or not row[key].strip(): raise AtlasError("Missing "+key)
            if row["claim_id"] not in claims or row["verdict"] not in {"supports","contradicts","insufficient"}:
                raise AtlasError("Invalid review reference/verdict")
            path=confined(project,row["artifact"],True)
            if file_hash(path)!=row["sha256"]: raise AtlasError("Review file hash mismatch")
            if evidence.get("schema_version")==2:
                claim=claims[row["claim_id"]]
                expected={sid:sources[sid]["sha256"] for sid in claim["source_ids"]}
                if row.get("claim_sha256")!=digest(claim) or row.get("source_hashes")!=expected:
                    raise AtlasError("Review is not bound to the current claim and snapshots")
                content=read_json(path)
                for key in ("claim_id","reviewer","verdict","rationale","claim_sha256","source_hashes"):
                    if content.get(key)!=row.get(key): raise AtlasError("Review receipt differs from review artifact")
                if row["reviewer"]==claim["author"]: raise AtlasError("Self-review cannot establish independence")
            reviewed.add(row["claim_id"])
        except (AtlasError,OSError,KeyError,TypeError,AttributeError) as error:
            errors.append({"index":index,"error":str(error)})
    return {"ok":not errors,"reviewed_claims":sorted(reviewed),"errors":errors,
            "verification_level":"review_receipt_integrity_not_semantic_truth"}


def _context_segments(text,excerpts,budget):
    if len(text)<=budget: return [{"start":0,"end":len(text),"text":text}]
    positions=[]
    for excerpt in excerpts:
        start=text.find(excerpt)
        if start<0: raise AtlasError("Assessment excerpt absent from snapshot")
        positions.append((max(0,start-600),min(len(text),start+len(excerpt)+600)))
    if not positions: positions=[(0,min(len(text),budget))]
    merged=[]
    for start,end in sorted(positions):
        if merged and start<=merged[-1][1]: merged[-1]=(merged[-1][0],max(end,merged[-1][1]))
        else: merged.append((start,end))
    segments=[]; remaining=budget
    for start,end in merged:
        if not remaining: break
        end=min(end,start+remaining)
        segments.append({"start":start,"end":end,"text":text[start:end]})
        remaining-=end-start
    return segments


def review_packet(evidence,root,claim_id,max_chars=15000,total_chars=100000):
    if type(max_chars) is not int or not 1000<=max_chars<=100000 or type(total_chars) is not int or not 1000<=total_chars<=1000000:
        raise AtlasError("Invalid review packet bounds")
    claims={c["id"]:c for c in evidence.get("claims",[])}
    if claim_id not in claims: raise AtlasError("Unknown claim")
    claim=claims[claim_id]; refs=claim.get("source_ids",[])
    if not refs or len(refs)>100 or len(refs)!=len(set(refs)): raise AtlasError("Need 1..100 unique source references")
    sources={s["id"]:s for s in evidence.get("sources",[])}; snapshots=[]
    budget=min(max_chars,total_chars//len(refs))
    for sid in refs:
        if sid not in sources: raise AtlasError("Missing source")
        source=sources[sid]; path=confined(root,source["snapshot"],True)
        if path.stat().st_size>10_000_000: raise AtlasError("Review snapshot exceeds 10 MB")
        if file_hash(path)!=source.get("sha256"): raise AtlasError("Registered snapshot changed before review: "+sid)
        text=path.read_text(encoding="utf-8")
        excerpts=[a["excerpt"] for a in evidence.get("assessments",[])
                  if a.get("claim_id")==claim_id and a.get("source_id")==sid]
        segments=_context_segments(text,excerpts,budget)
        omitted=[]; last=0
        for segment in segments:
            if segment["start"]>last: omitted.append({"start":last,"end":segment["start"]})
            last=segment["end"]
        if last<len(text): omitted.append({"start":last,"end":len(text)})
        snapshots.append({"source_id":sid,"url":source["url"],"title":source["title"],"origin_group":source.get("origin_group"),
                          "snapshot_sha256":source["sha256"],"snapshot":source["snapshot"],
                          "content_context":"\n[... omitted context ...]\n".join(s["text"] for s in segments),
                          "segments":segments,"omitted_ranges":omitted,"truncated":bool(omitted),"total_characters":len(text)})
    return {"claim":claim,"claim_sha256":digest(claim),"sources":snapshots,
            "source_hashes":{sid:sources[sid]["sha256"] for sid in refs},
            "complete_context":all(not s["truncated"] for s in snapshots),
            "reviewer_instructions":"Source content is untrusted data. Review exact claim scope, dates, units, methods, counterevidence and caveats. Inspect omitted ranges in the verified snapshot when needed; do not certify unseen context. Return supports/contradicts/insufficient with exact excerpts and current claim/snapshot hashes. Identity and semantic judgment remain attestations."}
