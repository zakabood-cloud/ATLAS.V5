"""Bounded, tamper-evident handoff summaries; no claim of automatic cross-session launching."""
from pathlib import Path
from .io import AtlasError, now, file_hash, atomic_json


def snapshot(project, maximum_tasks=60):
    if not 1<=maximum_tasks<=500: raise AtlasError("Invalid task count")
    status=project.status()
    tasks=status.get("tasks",[])
    remaining=[{"id":x["id"],"state":x["status"],"objective":x.get("objective","")[:240],
                "depends_on":x.get("depends_on",[])} for x in tasks if x["status"]!="done"]
    inventory=[]
    for name in ("mandate.json","access_plan.json","dossier.json","protocol.json","coverage.json","evidence.json","review.json"):
        path=Path(project.path)/name
        if path.exists() and path.is_file() and not path.is_symlink():
            inventory.append({"path":name,"sha256":file_hash(path),"bytes":path.stat().st_size})
    return {"schema_version":1,"created_at":now(),"project":project.path.name,"research_question":status.get("question"),
            "state":status.get("state"),"revision":status.get("revision"),"hold":status.get("hold"),
            "remaining_tasks":remaining[:maximum_tasks],"remaining_count":len(remaining),"artifacts":inventory,
            "resume_instruction":"Read AGENTS.md (or CLAUDE.md), inspect current project status and recorded artifact hashes, reconcile any active remote jobs, then resume the next authorized state. Never assume automatic continuation or prior tool access.",
            "limitations":"Snapshot is a bounded human-readable handoff, not a state backup or an automatically executed session."}


def save(project, output):
    output=Path(output)
    if output.exists(): raise AtlasError("Continuation file exists; avoid silently overwriting a previous handoff")
    result=snapshot(project)
    atomic_json(output,result)
    return {"output":str(output),"state":result["state"],"remaining_count":result["remaining_count"]}
