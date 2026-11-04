"""Conservative source-lineage clustering, not proof of independent evidence."""
from collections import defaultdict
from urllib.parse import unquote
from .io import AtlasError, text_required


def normalize_doi(value):
    if not isinstance(value,str): raise AtlasError("DOI must be text")
    value=unquote(value).strip().casefold()
    for prefix in ("https://doi.org/","http://doi.org/","https://dx.doi.org/","http://dx.doi.org/","doi:"):
        if value.startswith(prefix):
            value=value[len(prefix):].strip()
            break
    return value


def group_origins(sources):
    if not isinstance(sources,list): raise AtlasError("Sources must be a list")
    ids=[text_required(source,"id") for source in sources]
    if len(ids)!=len(set(ids)): raise AtlasError("Duplicate source ID")
    parent={sid:sid for sid in ids}; dependencies={}
    def find(key):
        while parent[key]!=key:
            parent[key]=parent[parent[key]]
            key=parent[key]
        return key
    def union(a,b):
        first,second=sorted((find(a),find(b)))
        parent[second]=first
    refs={}
    for source in sources:
        sid=source["id"]
        links=source.get("derived_from",[])
        if not isinstance(links,list) or any(not isinstance(x,str) or x not in parent for x in links):
            raise AtlasError("Unknown source-lineage reference")
        if len(links)!=len(set(links)): raise AtlasError("Duplicate source-lineage reference")
        dependencies[sid]=links
        for linked in links: union(sid,linked)
        for key in ("origin_group","sha256","doi","dataset_id","original_publication_id"):
            value=source.get(key)
            if value is None or value=="": continue
            if not isinstance(value,str) or not value.strip(): raise AtlasError("Invalid lineage "+key)
            value=normalize_doi(value) if key=="doi" else value.strip()
            identity=(key,value)
            if identity in refs: union(sid,refs[identity])
            else: refs[identity]=sid
    remaining={sid:len(links) for sid,links in dependencies.items()}
    dependents=defaultdict(list)
    for sid,links in dependencies.items():
        for linked in links: dependents[linked].append(sid)
    ready=[sid for sid in ids if not remaining[sid]]; visited=0
    while ready:
        sid=ready.pop(); visited+=1
        for dependent in dependents[sid]:
            remaining[dependent]-=1
            if not remaining[dependent]: ready.append(dependent)
    if visited!=len(ids): raise AtlasError("Cyclic source lineage")
    groups=defaultdict(list)
    for sid in ids: groups[find(sid)].append(sid)
    return {
        "groups":sorted(sorted(group) for group in groups.values()),
        "distinct_origin_clusters":len(groups),
        "untraced_source_ids":sorted(s["id"] for s in sources if not s.get("origin_group")),
        "limitation":"Clusters use declared lineage, identifiers and exact hashes. Different clusters are not proven independent; trace underlying studies and datasets.",
    }


def contradictions(evidence):
    by=defaultdict(lambda:defaultdict(set))
    if not isinstance(evidence,dict) or not isinstance(evidence.get("assessments"),list):
        raise AtlasError("Evidence assessments must be a list")
    for row in evidence["assessments"]:
        cid=text_required(row,"claim_id"); sid=text_required(row,"source_id")
        if row.get("verdict") not in {"supports","contradicts","insufficient"}:
            raise AtlasError("Unknown assessment verdict")
        by[cid][row["verdict"]].add(sid)
    return [
        {"claim_id":cid,"supporters":sorted(rows["supports"]),"contradictions":sorted(rows["contradicts"])}
        for cid,rows in sorted(by.items()) if rows["contradicts"]
    ]
