"""Review observable Copilot features without changing platform settings or permissions."""
from .io import AtlasError, text_required, confined, read_json, file_hash, date, now

FEATURES={
    "subagents":("Subagents and parallel delegation","Independent research, implementation and review workstreams"),
    "model_selection":("Model selection and Auto","Use the available task-start model policy; never infer hidden routing"),
    "mcp":("MCP connections","Topic-specific approved external capabilities"),
    "web_access":("Web and network access","Original source discovery and retrieval"),
    "repository_access":("Repository access","Read required repositories and perform separately authorized writes"),
    "execution":("Code and command execution","Reproducible calculations and local validation"),
    "file_access":("File and attachment tools","Read supplied material and inspect generated deliverables"),
    "customizations":("Instructions, skills and custom agents","Load the repository's research workflow and specialist profiles"),
}


def feature_inventory(question):
    if not isinstance(question,str) or not question.strip(): raise AtlasError("Inquiry required")
    return {"schema_version":1,"question":question,"environment":"Record the actual Copilot client and session",
            "discovery_limits":"Offline checklist only. Hidden settings, plan entitlements and administrator controls are not introspectable here. Add any other observed topic-relevant feature.",
            "features":[{"id":key,"name":name,"status":"unknown","needed":False,"basis":"Not inspected",
                         "controlled_by":"unknown","enablement_steps":"Inspect the actual client and official account settings; ask the user or administrator when needed.",
                         "cost":"Unverified; do not approve paid use implicitly",
                         "privacy":"Review the minimum permissions and destinations before enabling",
                         "quality_impact":purpose} for key,(name,purpose) in FEATURES.items()]}


def validate_features(plan,question,root):
    if not isinstance(plan,dict) or plan.get("schema_version")!=1 or plan.get("question")!=question:
        raise AtlasError("Enablement review must use schema 1 and the current inquiry")
    for key in ("environment","discovery_limits"): text_required(plan,key)
    rows=plan.get("features")
    if not isinstance(rows,list): raise AtlasError("Feature inventory required")
    features={}
    for row in rows:
        fid=text_required(row,"id")
        if fid in features: raise AtlasError("Duplicate feature ID")
        features[fid]=row
        for key in ("name","basis","enablement_steps","cost","privacy","quality_impact"):
            text_required(row,key)
        if row.get("status") not in {"enabled","disabled","unavailable","unknown"}:
            raise AtlasError("Unknown feature availability")
        if row.get("controlled_by") not in {"user","administrator","plan","platform","unknown"}:
            raise AtlasError("Identify who controls feature availability")
        if type(row.get("needed")) is not bool: raise AtlasError("Feature needed must be boolean")
        if row["status"]=="enabled":
            verification=row.get("verification",{})
            path=confined(root,verification.get("artifact",""),True)
            if file_hash(path)!=verification.get("sha256"): raise AtlasError("Feature verification artifact changed: "+fid)
            receipt=read_json(path)
            if not isinstance(receipt,dict) or receipt.get("feature_id")!=fid or receipt.get("status")!="enabled":
                raise AtlasError("Feature receipt does not verify the declared feature")
            for key in ("method","limitations"): text_required(receipt,key)
            if date(receipt.get("observed_at"))>date(now()) or date(receipt.get("expires_at"))<=date(now()):
                raise AtlasError("Feature observation is future-dated or expired: "+fid)
            if date(receipt["expires_at"])<=date(receipt["observed_at"]):
                raise AtlasError("Invalid feature observation window")
    if not FEATURES.keys()<=features.keys(): raise AtlasError("Review every standard Copilot capability; add others when discovered")
    return features


def validate_feature_decisions(features,decisions,ready=False):
    if not isinstance(decisions,list): raise AtlasError("Explicit feature decisions required")
    seen=set(); blocked=[]
    for row in decisions:
        fid=text_required(row,"feature_id")
        if fid not in features or fid in seen: raise AtlasError("Unknown or duplicate feature decision")
        seen.add(fid); text_required(row,"reason")
        feature=features[fid]; action=row.get("decision")
        if action not in {"use","enable","accept_limit","not_needed"}: raise AtlasError("Unknown feature decision")
        if action=="use" and feature["status"]!="enabled":
            raise AtlasError("Disabled/unknown/unavailable features cannot be claimed usable")
        if action=="not_needed" and feature["needed"]:
            raise AtlasError("A needed feature requires use, enablement or explicit acceptance of its limitation")
        if action=="enable": blocked.append(fid)
    if seen!=set(features): raise AtlasError("Ask the user to decide every reviewed feature")
    if ready and blocked: raise AtlasError("Enable and reverify requested features before research: "+", ".join(blocked))
    return {"ok":not blocked,"ready":not blocked,"awaiting_enablement":blocked,
            "limitations":"Recorded user choices and local observation receipts are not platform permission grants. No feature, safeguard, policy or subscription was changed."}
