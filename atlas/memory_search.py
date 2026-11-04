"""Scope-aware retrieval through the same validated method-memory loader."""
from .io import AtlasError
from .memory import retrieve
from .retrieval import bm25_search


def retrieve_ranked(root,query="",scope=None,tags=None,limit=15):
    if type(limit) is not int or not 1<=limit<=200: raise AtlasError("Memory limit must be 1..200")
    if not isinstance(query,str): raise AtlasError("Memory query must be text")
    if scope is not None and (not isinstance(scope,str) or not scope.strip()): raise AtlasError("Scope must be nonempty text")
    tags=[] if tags is None else tags
    if not isinstance(tags,list) or any(not isinstance(tag,str) or not tag.strip() for tag in tags):
        raise AtlasError("Tags must be nonempty strings")
    rows=[row for row in retrieve(root) if (scope is None or row["scope"]==scope)
          and (not tags or set(tags).intersection(row.get("tags",[])))]
    if not query.strip(): return rows[:limit]
    scored=bm25_search(query,[{"id":row["id"],"text":" ".join([row["method"],row["scope"]]+row.get("tags",[]))} for row in rows],limit=limit)
    lookup={row["id"]:row for row in rows}
    return [dict(lookup[item["id"]],retrieval_score=item["score"]) for item in scored]
