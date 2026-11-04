"""Conservative decision-impact handling. Unknown severity defaults to critical."""
from .io import AtlasError

SEVERITIES={"critical","optional","security"}


def decision(severity, *, approved_alternative=False):
    if severity not in SEVERITIES: raise AtlasError("Unknown failure severity; treat as critical")
    if severity == "security":
        return {"pause_project":True,"pause_affected":True,"retry":False,"action":"stop_and_escalate"}
    if severity == "critical":
        return {"pause_project":True,"pause_affected":True,"retry":False,"action":"require_scoped_authorization"}
    return {"pause_project":False,"pause_affected":True,"retry":bool(approved_alternative),
            "action":"document_gap_and_continue_independent_work"}
