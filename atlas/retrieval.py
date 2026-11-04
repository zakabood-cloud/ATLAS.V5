"""Deterministic corpus search, query planning and evidence-coverage diagnostics.

A local lexical engine, NOT a replacement for live retrieval or a semantic model.
No network calls; no executing text found in documents.
"""
import math
import re
from collections import Counter, defaultdict
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from .io import AtlasError

STOP = {'the','and','for','with','from','that','this','into','your','are','what','how','will','was','where','which'}
TRACKING = {'fbclid','gclid','msclkid'}

def tokenize(text):
    if not isinstance(text,str): raise AtlasError('Search text must be a string')
    return [x for x in re.findall(r'(?u)\b[^\W_]{2,}\b',text.casefold()) if x not in STOP]

def canonical_url(url):
    """Normalizes HTTP(S) references; leaves redirect resolution to a verified fetcher."""
    parts=urlsplit(url)
    if parts.scheme not in {'http','https'} or not parts.hostname or parts.username or parts.password:
        raise AtlasError('Expected valid public HTTP(S) URL')
    host=parts.hostname.lower().rstrip('.')
    if any(c.isspace() for c in host): raise AtlasError('Invalid host')
    port=parts.port
    netloc=('['+host+']' if ':' in host else host)+((':'+str(port)) if port and not (port==80 and parts.scheme=='http') and not (port==443 and parts.scheme=='https') else '')
    query=urlencode(sorted((k,v) for k,v in parse_qsl(parts.query,keep_blank_values=True)
                           if not k.lower().startswith('utm_') and k.lower() not in TRACKING))
    return urlunsplit((parts.scheme,netloc,parts.path.rstrip('/') or '/',query,''))

def expand_queries(question, coverage, synonyms=None, geographies=None, max_queries=80):
    """Round-robin dimensions before expanding synonyms; a plan is not a completed search."""
    if not isinstance(question,str) or not question.strip(): raise AtlasError('Need a question')
    if not isinstance(coverage,list) or not coverage or any(not isinstance(d,str) or not d.strip() for d in coverage):
        raise AtlasError('Need nonempty coverage dimensions')
    if len(set(coverage))!=len(coverage): raise AtlasError('Duplicate coverage dimension')
    if type(max_queries) is not int or not len(coverage)<=max_queries<=200:
        raise AtlasError('Query budget must cover every dimension and be at most 200')
    synonyms={} if synonyms is None else synonyms
    geographies=[] if geographies is None else geographies
    if not isinstance(synonyms,dict) or set(synonyms)-set(coverage): raise AtlasError('Unknown synonym dimension')
    for terms in list(synonyms.values())+[geographies]:
        if not isinstance(terms,list) or any(not isinstance(t,str) or not t.strip() for t in terms):
            raise AtlasError('Synonyms/geographies must be lists of nonempty text')
    def rows(dimension):
        for term in [dimension]+synonyms.get(dimension,[]):
            for geo in geographies or ['']:
                for strategy,parts in [
                    ('coverage',[question.strip(),term.strip(),geo.strip()]),
                    ('primary_source',[term.strip(),geo.strip(),'official statistics data methodology']),
                    ('counterevidence',[term.strip(),geo.strip(),'criticism failure contradictory evidence']),
                ]:
                    yield {'dimension':dimension,'query':' '.join(x for x in parts if x),'strategy':strategy}
    iterators=[iter(rows(d)) for d in coverage]; out=[]; seen=set()
    while iterators and len(out)<max_queries:
        remaining=[]
        for iterator in iterators:
            row=next(iterator,None)
            if row is None: continue
            remaining.append(iterator)
            key=(row['dimension'],row['query'].casefold())
            if key not in seen:
                out.append(row); seen.add(key)
            if len(out)==max_queries: break
        iterators=remaining
    return out

def bm25_search(query,documents,limit=10,k1=1.2,b=.75):
    """Rank {id,text} local documents. Scores indicate lexical relevance, not factual reliability."""
    if type(limit) is not int or not 1<=limit<=200: raise AtlasError('Invalid limit')
    if type(k1) not in (int,float) or not math.isfinite(k1) or k1<=0: raise AtlasError('k1 must be positive and finite')
    if type(b) not in (int,float) or not math.isfinite(b) or not 0<=b<=1: raise AtlasError('b must be in [0,1]')
    if not isinstance(query,str) or not query.strip(): raise AtlasError('Nonempty query required')
    if not isinstance(documents,list): raise AtlasError('Expected document list')
    index=[]; df=Counter(); ids=set()
    for row in documents:
        if not isinstance(row,dict) or not isinstance(row.get('id'),str) or not isinstance(row.get('text'),str):
            raise AtlasError('Documents need id/text')
        if not row['id'].strip() or row['id'] in ids: raise AtlasError('Blank or duplicate document id')
        ids.add(row['id']); tokens=tokenize(row['text']); tf=Counter(tokens)
        for t in tf: df[t]+=1
        index.append((row['id'],tf,len(tokens)))
    n=len(index); avg=sum(length for _,_,length in index)/n if n else 1
    qterms=list(dict.fromkeys(tokenize(query))); scores=[]
    for id_,tf,length in index:
        score=0.
        for term in qterms:
            if term in tf:
                idf=math.log(1+(n-df[term]+.5)/(df[term]+.5))
                score+=idf*tf[term]*(k1+1)/(tf[term]+k1*(1-b+b*length/avg))
        if score>0: scores.append({'id':id_,'score':round(score,8)})
    return sorted(scores,key=lambda x:(-x['score'],x['id']))[:limit]

def coverage_audit(required, observations):
    """Rows must be attached to a dimension and have independent provenance pointers."""
    if not isinstance(required,list) or any(not isinstance(d,str) or not d.strip() for d in required):
        raise AtlasError('Coverage dimensions must be nonempty strings')
    if not required or len(required)!=len(set(required)):
        raise AtlasError('Need unique coverage dimensions')
    if not isinstance(observations,list): raise AtlasError('Expected observation list')
    known=set(required); found=defaultdict(list); invalid=[]
    for row in observations:
        if (not isinstance(row,dict) or not isinstance(row.get('dimension'),str) or row['dimension'] not in known
                or not isinstance(row.get('source_id'),str) or not row['source_id'].strip()
                or (row.get('origin_group') is not None and not isinstance(row['origin_group'],str))):
            invalid.append(row); continue
        found[row['dimension']].append(row)
    result=[]
    for d in required:
        rows=found[d]; origins={r['origin_group'].strip() for r in rows if (r.get('origin_group') or '').strip()}
        untraced=sorted({r['source_id'] for r in rows if not (r.get('origin_group') or '').strip()})
        result.append({'dimension':d,'observation_count':len(rows),
                       'distinct_origin_count':len(origins),'source_ids':sorted({r['source_id'] for r in rows}),
                       'untraced_source_ids':untraced,
                       'status':'uncovered' if not rows else 'untraced' if not origins else 'single_origin' if len(origins)==1 else 'multiple_origins'})
    return {'dimensions':result,'uncovered':[r['dimension'] for r in result if r['status']=='uncovered'],
            'invalid_observations':len(invalid),
            'warning':'Multiple origins alone do not establish truth or complete recall.'}
