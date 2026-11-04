"""Denominator-safe evaluation of verified labels and frozen retrieval judgments."""
import math
from .io import AtlasError, canonical, digest, text_required


def _index(rows,label):
    if not isinstance(rows,list): raise AtlasError(label+" must be a list")
    result={}
    for row in rows:
        key=text_required(row,"id")
        if key in result: raise AtlasError("Duplicate "+label+" ID: "+key)
        result[key]=row
    return result


def _wilson(hits,total):
    if not total: return None
    z=1.959963984540054
    p=hits/total; denominator=1+z*z/total
    center=(p+z*z/(2*total))/denominator
    radius=z*math.sqrt((p*(1-p)+z*z/(4*total))/total)/denominator
    return [max(0.,center-radius),min(1.,center+radius)]


def evaluate_cases(cases,results):
    expected=_index(cases,"case"); observed=_index(results,"result")
    if not expected: raise AtlasError("Need test cases")
    if set(observed)-set(expected): raise AtlasError("Result IDs absent from frozen cases")
    rows=[]; correct=answered=failures=0; probabilities=[]
    for key,case in expected.items():
        if "expected" not in case or case["expected"] is None: raise AtlasError("Each case needs a known non-null expected answer")
        result=observed.get(key,{})
        prediction=result.get("answer"); responded=prediction is not None
        status=result.get("status","answered" if responded else "abstained")
        if status not in {"answered","abstained","failed"} or (status=="answered")!=responded:
            raise AtlasError("Answer and result status disagree")
        hit=responded and canonical(prediction)==canonical(case["expected"])
        answered+=responded; correct+=hit; failures+=status=="failed"
        rows.append({"id":key,"answered":responded,"correct":hit,"expected":case["expected"],
                     "prediction":prediction,"status":status,"evidence":result.get("evidence",[])})
        if "probability" in result:
            p=result["probability"]
            if type(case["expected"]) is not bool: raise AtlasError("Binary calibration requires boolean outcomes")
            if type(p) not in (int,float) or not math.isfinite(p) or not 0<=p<=1:
                raise AtlasError("probability must be finite P(outcome=True) in [0,1]")
            probabilities.append((p,int(case["expected"])))
    bins=[]
    for index in range(10):
        values=[(p,y) for p,y in probabilities if min(int(p*10),9)==index]
        if values:
            bins.append({"lower":index/10,"upper":(index+1)/10,"count":len(values),
                         "mean_probability":sum(p for p,_ in values)/len(values),
                         "outcome_rate":sum(y for _,y in values)/len(values)})
    total=len(expected)
    return {
        "cases":total,"answered":answered,"abstained":total-answered-failures,"failed":failures,
        "coverage_rate":answered/total,"accuracy_over_all":correct/total,
        "accuracy_on_answered":correct/answered if answered else None,
        "accuracy_wilson_95":_wilson(correct,total),"case_digest":digest(cases),"per_case":rows,
        "calibration":{"count":len(probabilities),"coverage":len(probabilities)/total,
                       "brier_score":sum((p-y)**2 for p,y in probabilities)/len(probabilities) if probabilities else None,
                       "bins":bins},
        "warning":"Exact JSON-label scoring needs independently verified answers. Missing/failed cases stay in the denominator. Wilson intervals assume binomial sampling; heterogeneous or selected cases do not establish generalization. Calibration applies only to observed binary outcomes.",
    }


def compare_runs(left,right):
    la=_index(left.get("per_case"),"left case"); ra=_index(right.get("per_case"),"right case")
    if not la or set(la)!=set(ra): raise AtlasError("Paired runs must contain exactly the same nonempty case IDs")
    out={"left_only_correct":[],"right_only_correct":[],"both_correct":[],"neither_correct":[]}
    for key in sorted(la):
        a,b=la[key],ra[key]
        if "expected" not in a or "expected" not in b or canonical(a["expected"])!=canonical(b["expected"]):
            raise AtlasError("Paired answer keys differ")
        for row in (a,b):
            if type(row.get("correct")) is not bool or type(row.get("answered")) is not bool:
                raise AtlasError("Paired cases require boolean outcomes")
            recomputed=row.get("prediction") is not None and canonical(row["prediction"])==canonical(row["expected"])
            if row["correct"]!=recomputed or row["answered"]!=(row.get("prediction") is not None):
                raise AtlasError("Paired correctness does not match the recorded prediction")
        label="both_correct" if a["correct"] and b["correct"] else "left_only_correct" if a["correct"] else "right_only_correct" if b["correct"] else "neither_correct"
        out[label].append(key)
    return {"paired_cases":len(la),**out,
            "accuracy_difference_right_minus_left":(len(out["right_only_correct"])-len(out["left_only_correct"]))/len(la),
            "note":"Matched descriptive comparison, not a significance or superiority claim. Freeze cases and resources before independent evaluation."}


def evaluate_retrieval(queries,results,k=10):
    if type(k) is not int or not 1<=k<=200: raise AtlasError("k must be 1..200")
    expected=_index(queries,"query"); observed=_index(results,"retrieval result")
    if not expected or set(observed)-set(expected): raise AtlasError("Need known, nonempty query IDs")
    rows=[]
    for key,query in expected.items():
        relevant=query.get("relevant_ids"); ranked=observed.get(key,{}).get("ranked_ids",[])
        for values in (relevant,ranked):
            if not isinstance(values,list) or any(not isinstance(v,str) or not v.strip() for v in values) or len(values)!=len(set(values)):
                raise AtlasError("Relevance/ranking IDs must be unique nonempty strings")
        top=ranked[:k]; hits=sum(doc in relevant for doc in top)
        ranks=[i for i,doc in enumerate(top,1) if doc in relevant]
        ideal=sum(1/math.log2(i+1) for i in range(1,min(k,len(relevant))+1))
        rows.append({"id":key,"retrieved":len(top),"relevant":len(relevant),"hits":hits,
                     "precision_at_k":hits/k,"recall_at_k":hits/len(relevant) if relevant else None,
                     "reciprocal_rank":1/ranks[0] if ranks else 0.,
                     "ndcg_at_k":sum(1/math.log2(i+1) for i in ranks)/ideal if ideal else None})
    def average(field):
        values=[row[field] for row in rows if row[field] is not None]
        return sum(values)/len(values) if values else None
    return {"queries":len(rows),"k":k,"judgment_digest":digest(queries),"per_query":rows,
            "macro_precision_at_k":average("precision_at_k"),"macro_recall_at_k":average("recall_at_k"),
            "mrr":average("reciprocal_rank"),"macro_ndcg_at_k":average("ndcg_at_k"),
            "warning":"Measures retrieval against the supplied frozen judgments only. Missing runs score zero; empty relevance sets have undefined recall/nDCG. No web-completeness or evidence-independence claim."}
