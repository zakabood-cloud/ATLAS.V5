"""Exact expected value of a binary diagnostic experiment, declared inputs only."""
from .quant import D,probability,nonnegative
from .io import AtlasError

def evsi_binary(spec):
    """Prior and observation accuracy must be defensible externally; no learned forecast."""
    prior=probability(spec['prior_h']); sensitivity=probability(spec['p_positive_if_h']);false_positive=probability(spec['p_positive_if_not_h']);
    payoffs=spec['payoffs']
    if not isinstance(payoffs,dict) or len(payoffs)<2: raise AtlasError('Need at least two decisions with H/not-H payoffs')
    parsed={k:(D(v['h']),D(v['not_h'])) for k,v in payoffs.items()}
    current={k:prior*v[0]+(1-prior)*v[1] for k,v in parsed.items()}
    base=max(current.values())
    signals=[(sensitivity,false_positive),(1-sensitivity,1-false_positive)]
    tested=sum(max(prior*ph*v[0]+(1-prior)*pnh*v[1] for v in parsed.values()) for ph,pnh in signals)
    evsi=tested-base
    if evsi<0 and abs(evsi)<D('1e-12'): evsi=D('0')
    cost=nonnegative(spec.get('experiment_cost',0))
    return {'without_experiment':str(base),'with_experiment_before_cost':str(tested),
            'evsi':str(evsi),'experiment_cost':str(cost),'net_value_of_experiment':str(evsi-cost),
            'warning':'Exact in the declared binary model; requires independently supported prior, likelihoods and payoffs.'}
