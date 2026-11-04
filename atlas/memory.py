"""Versioned method memory, separate from topic evidence and never executable."""
import re
from pathlib import Path
from .io import AtlasError, confined, read_json, atomic_json, file_hash, date, now, text_required


def promote(root,proposal):
    root=Path(root)
    if not isinstance(proposal,dict): raise AtlasError("Memory proposal must be object")
    for k in ["id","method","scope","author","reviewer","expires_at","validation_artifact","validation_sha256"]: text_required(proposal,k)
    if not re.fullmatch(r"[a-z0-9-]{1,64}",proposal["id"]): raise AtlasError("Invalid memory ID")
    if proposal.get("kind")!="method" or proposal.get("status")!="validated": raise AtlasError("Only validated methods enter active memory")
    if proposal["author"]==proposal["reviewer"]: raise AtlasError("Distinct reviewer required")
    tags=proposal.get("tags",[])
    if not isinstance(tags,list) or any(not isinstance(tag,str) or not tag.strip() for tag in tags):
        raise AtlasError("Memory tags must be nonempty strings")
    if date(proposal["expires_at"])<=date(now()): raise AtlasError("Memory expires in past")
    p=confined(root,proposal["validation_artifact"],True)
    if file_hash(p)!=proposal["validation_sha256"]: raise AtlasError("Validation receipt changed")
    receipt=read_json(p)
    if (not isinstance(receipt,dict) or receipt.get("passed") is not True
            or not isinstance(receipt.get("tests"),list) or not receipt["tests"]):
        raise AtlasError("Validation receipt must contain passed=true, tests, and limitations")
    text_required(receipt,"limitations")
    dest=confined(root,"memory/"+proposal["id"]+".json")
    previous=read_json(dest) if dest.exists() else None
    version=previous["version"]+1 if previous else 1
    if previous:
        atomic_json(confined(root,f"memory/history/{proposal['id']}-v{previous['version']}.json"),previous)
    out=dict(proposal,version=version,promoted_at=now())
    atomic_json(dest,out)
    return out


def retrieve(root,query="",as_of=None):
    current=date(as_of or now()); rows=[]
    for p in sorted((Path(root)/"memory").glob("*.json")):
        if p.is_symlink(): raise AtlasError("Symlink in active method memory: "+p.name)
        row=read_json(p)
        if not isinstance(row,dict): raise AtlasError("Method memory must be an object: "+p.name)
        for key in ["id","method","scope","expires_at","author","reviewer"]: text_required(row,key)
        if row["id"]!=p.stem or row.get("kind")!="method": raise AtlasError("Invalid method memory identity")
        if not isinstance(row.get("tags",[]),list) or any(not isinstance(tag,str) for tag in row.get("tags",[])):
            raise AtlasError("Memory tags must be strings")
        if row.get("status")!="validated": raise AtlasError("Invalid active method status: "+row["id"])
        if date(row["expires_at"])<=current: continue
        receipt_path=confined(root,text_required(row,"validation_artifact"),True)
        if file_hash(receipt_path)!=text_required(row,"validation_sha256"):
            raise AtlasError("Active method validation receipt changed: "+row["id"])
        receipt=read_json(receipt_path)
        if (not isinstance(receipt,dict) or receipt.get("passed") is not True
                or not isinstance(receipt.get("tests"),list) or not receipt["tests"]):
            raise AtlasError("Invalid active method validation receipt: "+row["id"])
        text_required(receipt,"limitations")
        if row.get("author")==row.get("reviewer") or not row.get("author") or not row.get("reviewer"):
            raise AtlasError("Invalid active method reviewer")
        if query and query.lower() not in (row["method"]+" "+row["scope"]+" "+" ".join(row.get("tags",[]))).lower(): continue
        rows.append(row)
    return rows
