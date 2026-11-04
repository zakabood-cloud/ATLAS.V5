"""Auditable lexical consistency checks; cannot prove semantic entailment."""
import re
from .io import AtlasError

_NUM=re.compile(r'(?<!\w)(?:[$€£]\s*)?-?\d[\d,]*(?:\.\d+)?\s*(?:%|million|billion|thousand|USD|AED|EUR|kg|years?)?(?!\w)',re.I)
_NEG=re.compile(r'\b(no|not|never|without|decreased|declined|fell|failed|unprofitable)\b',re.I)


def check_claim_context(claim, passages):
    """Flag numerical/negation mismatch; independent review remains mandatory."""
    if not isinstance(claim,str) or not claim.strip(): raise AtlasError('Nonempty claim required')
    if not isinstance(passages,list) or not passages or not all(isinstance(p,str) for p in passages):
        raise AtlasError('Passage texts required')
    combined=' '.join(passages)
    cnum=set(' '.join(n.group().split()).lower() for n in _NUM.finditer(claim) if n.group().strip())
    pnum=set(' '.join(n.group().split()).lower() for n in _NUM.finditer(combined) if n.group().strip())
    unmapped=sorted(cnum-pnum)
    cneg=bool(_NEG.search(claim)); pneg=bool(_NEG.search(combined))
    flags=[]
    if unmapped: flags.append({"code":"claim_numbers_absent_from_passages","tokens":unmapped})
    if cneg!=pneg: flags.append({"code":"possible_negation_mismatch","claim_negated":cneg,"passage_negated":pneg})
    return {"flags":flags,"lexical_only":True,"verdict":"requires_independent_semantic_review",
            "notes":"Different numeric formats and contextual negations can produce false positives or miss real contradictions."}
