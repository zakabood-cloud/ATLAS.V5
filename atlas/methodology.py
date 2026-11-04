"""Compare declared pilot observations without allowing scores to hide hard constraints."""
import math
from .io import AtlasError, text_required

DEFAULT_WEIGHTS={"evidence_quality":.30,"coverage":.25,"reproducibility":.20,"feasibility":.15,"cost_efficiency":.10}


def _unit(value):
    if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=1:
        raise AtlasError("Rubric values must be finite numbers in [0,1]")
    return value


def score_methods(candidates,weights=None,minimum_scores=None):
    weights=DEFAULT_WEIGHTS.copy() if weights is None else weights
    minimum_scores={} if minimum_scores is None else minimum_scores
    if not isinstance(weights,dict) or not weights or any(not isinstance(k,str) or not k.strip() for k in weights):
        raise AtlasError("Nonempty named method weights required")
    for value in weights.values(): _unit(value)
    if sum(weights.values())<=0: raise AtlasError("Weights sum to zero")
    if not isinstance(minimum_scores,dict) or set(minimum_scores)-set(weights): raise AtlasError("Unknown threshold dimension")
    for value in minimum_scores.values(): _unit(value)
    if not isinstance(candidates,list) or len(candidates)<2: raise AtlasError("Compare at least two methodologies")
    names=set(); output=[]; excluded=[]
    for method in candidates:
        name=text_required(method,"name")
        if name in names: raise AtlasError("Duplicate method name")
        names.add(name)
        text_required(method,"pilot_evidence")
        observed=method.get("pilot")
        if not isinstance(observed,dict) or set(weights)-set(observed): raise AtlasError("Missing pilot dimension for "+name)
        for key in weights: _unit(observed[key])
        if type(method.get("feasible",True)) is not bool: raise AtlasError("feasible must be boolean")
        reasons=[]
        if not method.get("feasible",True):
            reasons.append(text_required(method,"infeasibility_reason"))
        reasons.extend("Below predefined minimum: "+k for k,v in minimum_scores.items() if observed[k]<v)
        if reasons:
            excluded.append({"name":name,"reasons":reasons,"pilot":observed,"pilot_evidence":method["pilot_evidence"]})
            continue
        score=sum(weights[k]*observed[k] for k in weights)/sum(weights.values())
        output.append({"name":name,"score":round(score,6),"pilot":observed,
                       "pilot_evidence":method["pilot_evidence"],"limitations":method.get("limitations",[])})
    output.sort(key=lambda row:(-row["score"],row["name"]))
    return {"ok":bool(output),"ranking":output,"selected":output[0]["name"] if output else None,
            "excluded":excluded,"weights":weights,"minimum_scores":minimum_scores,
            "caveat":"Scores and pilot receipts are operator supplied. Predeclare thresholds; ineligible designs cannot win by compensation. This is not universal or independently verified method quality."}
