"""Reproducible decision arithmetic. Inputs are assumptions, never estimated by this module."""
from decimal import Decimal, InvalidOperation, DecimalException, localcontext
import math
import random
from .io import AtlasError, digest


def D(value):
    if isinstance(value, bool): raise AtlasError("Boolean is not a number")
    if len(str(value))>512: raise AtlasError("Numeric input exceeds size bound")
    try: x = Decimal(str(value))
    except (InvalidOperation, ValueError) as e: raise AtlasError("Invalid numeric input") from e
    if not x.is_finite(): raise AtlasError("Nonfinite numeric input")
    if x and abs(x.adjusted())>100: raise AtlasError("Numeric magnitude outside supported range")
    return x


def nonnegative(value):
    x = D(value)
    if x < 0: raise AtlasError("Expected nonnegative amount")
    return x


def probability(value):
    x = D(value)
    if not 0 <= x <= 1: raise AtlasError("Probability/rate outside [0,1]")
    return x


def unit_economics(s):
    price = nonnegative(s["price_gross"])
    vat = probability(s.get("vat_rate", 0))
    # All percentage fees in this model use net revenue. Change formula explicitly if contract differs.
    net = price / (1 + vat)
    costs = {k: nonnegative(s.get(k, 0)) for k in ["landed_cost", "fulfillment", "payment_fixed", "ad_cost_per_order", "expected_return_cost"]}
    fee = net * probability(s.get("fee_rate_on_net", 0))
    contribution = net - sum(costs.values()) - fee
    fixed = nonnegative(s.get("fixed_cost_per_period", 0))
    units = nonnegative(s.get("units_per_period", 0))
    return {"net_revenue_per_order": str(net), "variable_cost_per_order": str(sum(costs.values())+fee),
            "contribution_per_order": str(contribution), "period_profit": str(contribution*units-fixed),
            "break_even_units": format((fixed/contribution).to_integral_value(rounding="ROUND_CEILING"),"f") if contribution > 0 else None,
            "break_even_ad_cost": str(contribution+costs["ad_cost_per_order"]),
            "warning": "Accounting model only; expected return cost must include refunds/net revenue effects consistently. No sales forecast is inferred."}


def cashflow(s):
    if not isinstance(s.get("periods"),list) or not s["periods"]: raise AtlasError("Nonempty cashflow periods required")
    cash = D(s["opening_cash"]); rows = []; rate = probability(s.get("discount_rate_per_period", 0))
    npv = -nonnegative(s.get("initial_investment", 0))
    for t, row in enumerate(s["periods"], 1):
        inflow = nonnegative(row["inflow"]); outflow = nonnegative(row["outflow"])
        net = inflow-outflow; cash += net; npv += net/(1+rate)**t
        rows.append({"period": t, "net": str(net), "closing_cash": str(cash)})
    return {"periods": rows, "minimum_cash": str(min([D(s["opening_cash"])]+[D(r["closing_cash"]) for r in rows])),
            "npv": str(npv), "warning": "Opening cash is after any initial investment; inflows reflect payment timing, not booked revenue."}


def _weights(values):
    p = [probability(v) for v in values]
    if abs(sum(p)-1) > Decimal("0.000000001"): raise AtlasError("Probabilities must sum to one")
    return p


def monte_carlo(s):
    n = s.get("draws", 10000)
    if type(n) is not int or not 100 <= n <= 1000000: raise AtlasError("draws must be integer 100..1000000")
    if type(s.get("seed")) is not int: raise AtlasError("Explicit integer random seed required")
    rows = s["scenarios"]
    if not rows: raise AtlasError("At least one scenario required")
    weights = _weights([r["probability"] for r in rows])
    values = [float(D(r["net_value"])) for r in rows]
    if not all(math.isfinite(v) for v in values): raise AtlasError("Scenario magnitude too large")
    samples = sorted(random.Random(s["seed"]).choices(values, weights=[float(w) for w in weights], k=n))
    def q(p): return samples[round((n-1)*p)]
    return {"draws": n, "seed": s["seed"], "mean": math.fsum(v/n for v in samples),
            "p05": q(.05), "p50": q(.5), "p95": q(.95),
            "loss_probability": sum(x<0 for x in samples)/n,
            "exact_scenario_expected_value": str(sum(D(r["net_value"])*w for r,w in zip(rows,weights))),
            "interpretation": "Conditional on supplied joint scenarios/probabilities; percentiles are simulation outcomes, not confidence intervals."}


def mcda(s):
    criteria = s["criteria"]; alternatives = s["alternatives"]
    if not criteria or len(alternatives)<2: raise AtlasError("Need criteria and at least two alternatives")
    names=[c["name"] for c in criteria]
    if len(set(names))!=len(names): raise AtlasError("Duplicate criterion")
    weights=[nonnegative(c["weight"]) for c in criteria]
    if sum(weights)<=0: raise AtlasError("Weights sum to zero")
    normalized={}
    for name, vals in alternatives.items():
        scores=[]
        for c in criteria:
            low,high=D(c["low"]),D(c["high"]); value=D(vals[c["name"]])
            if high<=low or not low<=value<=high: raise AtlasError("Invalid MCDA bounds/value")
            if c["direction"] not in {"benefit","cost"}: raise AtlasError("Unknown direction")
            score=(value-low)/(high-low)
            scores.append(score if c["direction"]=="benefit" else 1-score)
        normalized[name]=scores
    def rank(ws):
        return sorted(({"name": name, "score": str(sum(a*b for a,b in zip(scores,ws))/sum(ws))} for name,scores in normalized.items()),key=lambda r:(-D(r["score"]),r["name"]))
    sensitivity=[]
    for i,c in enumerate(criteria):
        for factor in [Decimal("0.8"),Decimal("1.2")]:
            ws=weights.copy(); ws[i]*=factor
            sensitivity.append({"criterion": c["name"],"factor":str(factor),"ranking":rank(ws)})
    return {"ranking":rank(weights),"weight_sensitivity":sensitivity,
            "warning":"Explicit fixed bounds; additive utility assumes preferential independence. Weight sensitivity is local, not exhaustive robustness."}


def bayes(s):
    prior=probability(s["prior"]); likelihood=probability(s["p_e_given_h"]); alternative=probability(s["p_e_given_not_h"])
    denominator=prior*likelihood+(1-prior)*alternative
    if denominator==0: raise AtlasError("Evidence has zero probability")
    return {"posterior":str(prior*likelihood/denominator),"interpretation":"Conditional on explicit prior and likelihoods; no learned calibration implied."}


def evpi(s):
    probs=_weights(s["probabilities"]); rows=s["payoffs"]
    if not rows or any(len(v)!=len(probs) for v in rows.values()): raise AtlasError("Payoff dimensions disagree")
    expected={k:sum(D(v)*p for v,p in zip(vals,probs)) for k,vals in rows.items()}
    perfect=sum(max(D(vals[i]) for vals in rows.values())*p for i,p in enumerate(probs))
    return {"expected_values":{k:str(v) for k,v in expected.items()},"best_current_value":str(max(expected.values())),
            "perfect_information_value":str(perfect),"evpi_upper_bound":str(perfect-max(expected.values())),
            "interpretation":"Upper bound on information value in stated utility units. Does not estimate value of a particular search or experiment."}


FUNCTIONS={"unit_economics":unit_economics,"cashflow":cashflow,"monte_carlo":monte_carlo,"mcda":mcda,"bayes":bayes,"evpi":evpi}


def output_units(kind,units,output,legacy=False):
    """Explicit pointer-to-unit map for numerical claim binding; labels are user supplied."""
    if kind=="unit_economics":
        return {"/output/"+key:("orders per period" if key=="break_even_units" else units+" per period" if key=="period_profit" else units+" per order")
                for key in output if key!="warning"}
    if kind=="cashflow":
        rows={"/output/minimum_cash":units,"/output/npv":units}
        for i in range(len(output["periods"])):
            rows.update({f"/output/periods/{i}/net":units,f"/output/periods/{i}/closing_cash":units})
        return rows
    if kind=="monte_carlo":
        return {"/output/"+key:("probability" if key=="loss_probability" else units) for key in
                ["mean","p05","p50","p95","loss_probability","exact_scenario_expected_value"]}
    if kind=="bayes": return {"/output/posterior":"probability"}
    if kind=="evpi":
        rows={"/output/"+key:units for key in ["best_current_value","perfect_information_value","evpi_upper_bound"]}
        rows.update({"/output/expected_values/"+key.replace("~","~0").replace("/","~1"):units for key in output["expected_values"]})
        return rows
    if kind=="ecommerce_economics":
        if not legacy:
            per_order={"net_revenue_if_kept","expected_net_revenue_per_order","expected_variable_cost_per_order","contribution_per_order"}
            return {"/output/"+key:("orders per period" if key=="break_even_orders" else
                                   "fraction" if key=="contribution_margin_on_expected_revenue" else
                                   units+" per period" if key=="period_operating_profit" else
                                   units+" per order" if key in per_order else units)
                    for key in output if key!="warning"}
        return {"/output/"+k:("orders per period" if k=="break_even_orders" else "fraction" if k=="contribution_margin_on_expected_revenue" else units) for k in output if k!="warning"}
    if kind=="evsi_binary": return {"/output/"+k:units for k in output if k!="warning"}
    if kind=="reverse_stress": return {"/output/"+k:units for k in output if k!="warning"}
    if kind=="correlated_simulation": return {"/output/"+k:("probability" if k=="loss_probability" else units) for k in ("mean","p05","p50","p95","loss_probability")}
    return {f"/output/ranking/{i}/score":"unitless utility" for i in range(len(output["ranking"]))}


def run_analysis(spec,engine=None):
    engine=engine or "atlas.quant/4.0.0"
    if engine not in {"atlas.quant/3.0.0","atlas.quant/4.0.0"}: raise AtlasError("Unsupported calculation engine; do not silently reinterpret old artifacts")
    if not isinstance(spec,dict) or not isinstance(spec.get("kind"),str): raise AtlasError("Unknown analysis kind")
    # Import advanced models only on demand to avoid a circular import with D().
    advanced={"ecommerce_economics":"ecommerce_economics", "correlated_simulation":"correlated_simulation", "reverse_stress":"reverse_stress", "evsi_binary":"evsi_binary"}
    if spec["kind"] not in FUNCTIONS and spec["kind"] not in advanced: raise AtlasError("Unknown analysis kind")
    if not isinstance(spec.get("units"),str) or not spec["units"].strip(): raise AtlasError("Analysis must declare a base unit label")
    if not isinstance(spec.get("assumptions"),list) or not spec["assumptions"] or any(not isinstance(a,str) or not a.strip() for a in spec["assumptions"]): raise AtlasError("Analysis requires explicit nonempty assumption statements")
    try:
        with localcontext() as ctx:
            ctx.prec=28
            if spec["kind"] in advanced:
                if spec["kind"]=="evsi_binary":
                    from .experiment import evsi_binary
                    output=evsi_binary(spec)
                else:
                    from . import decision
                    output=getattr(decision,advanced[spec["kind"]])(spec)
            else:
                output=FUNCTIONS[spec["kind"]](spec)
    except (KeyError,TypeError,IndexError,AttributeError,DecimalException) as e: raise AtlasError("Missing, malformed or numerically unsupported analysis input") from e
    return {"schema_version":1 if engine=="atlas.quant/3.0.0" else 2,"engine":engine,"input_sha256":digest(spec),"kind":spec["kind"],"units":spec["units"],"output":output,
            "output_units":output_units(spec["kind"],spec["units"],output,legacy=engine=="atlas.quant/3.0.0")}
