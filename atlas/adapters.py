"""Opt-in, bounded bibliographic metadata requests; never full-text verification."""
from urllib.parse import urlencode, urlsplit
from urllib.request import build_opener, Request, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
from uuid import uuid4
from datetime import timedelta
from .io import AtlasError, now, parse_json, digest, atomic_json, date, confined
from .access import AccessBlocked
from .sourcegraph import normalize_doi
from . import __version__

HOSTS={"crossref":"api.crossref.org","openalex":"api.openalex.org"}
MAX_RESPONSE=3_000_000


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise AtlasError("Provider redirect blocked; inspect the endpoint manually")


def _allowed(url,provider):
    parsed=urlsplit(url)
    if (provider not in HOSTS or parsed.scheme!="https" or parsed.hostname!=HOSTS[provider]
            or parsed.username is not None or parsed.password is not None or parsed.port is not None
            or parsed.path!="/works" or parsed.fragment):
        raise AtlasError("URL is not an exact permitted provider endpoint")
    return parsed.hostname


def http_json(url,provider,timeout=15,opener=None):
    _allowed(url,provider)
    if type(timeout) not in (int,float) or not 1<=timeout<=60: raise AtlasError("Invalid timeout")
    client=opener or build_opener(NoRedirect())
    try:
        request=Request(url,headers={"Accept":"application/json","User-Agent":f"ATLAS-Research-OS/{__version__} (read-only metadata)"})
        with client.open(request,timeout=timeout) as response:
            if getattr(response,"status",200)!=200: raise AtlasError("Provider returned non-200 response")
            length=response.headers.get("Content-Length")
            if length is not None and (not length.isdecimal() or int(length)>MAX_RESPONSE):
                raise AtlasError("Invalid or oversized provider Content-Length")
            content_type=response.headers.get("Content-Type","").split(";")[0].strip().lower()
            if content_type and content_type!="application/json" and not content_type.endswith("+json"):
                raise AtlasError("Provider did not return JSON")
            raw=response.read(MAX_RESPONSE+1)
            if len(raw)>MAX_RESPONSE: raise AtlasError("Provider response too large")
            data=parse_json(raw.decode("utf-8"))
            if not isinstance(data,dict): raise AtlasError("Provider JSON must be an object")
            return data
    except HTTPError as error:
        retry_after=error.headers.get("Retry-After") if error.headers else None
        detail=f"Provider HTTP {error.code}; no automatic retry was made"
        if retry_after: detail+="; Retry-After="+retry_after[:80]
        raise AtlasError(detail) from error
    except (URLError,TimeoutError,UnicodeError) as error:
        raise AtlasError("Provider retrieval failed: "+type(error).__name__) from error


def search(provider,query,limit=10,cursor=None,**kwargs):
    if provider not in HOSTS: raise AtlasError("No adapter for provider")
    if not isinstance(query,str) or not query.strip() or len(query)>400: raise AtlasError("Query required (max 400 characters)")
    if type(limit) is not int or not 1<=limit<=50: raise AtlasError("Search limit must be 1..50")
    if cursor is not None and (not isinstance(cursor,str) or not cursor or len(cursor)>8192):
        raise AtlasError("Cursor must be nonempty text of at most 8192 characters")
    params={"query.bibliographic":query,"rows":str(limit)} if provider=="crossref" else {"search":query,"per_page":str(limit)}
    if cursor is not None: params["cursor"]=cursor
    url=f"https://{HOSTS[provider]}/works?"+urlencode(params)
    data=http_json(url,provider,**kwargs)
    if not isinstance(data,dict) or data.get("error") or data.get("status") not in (None,"ok"):
        raise AtlasError("Provider returned an error or malformed object")
    container=data.get("message") if provider=="crossref" else data
    key="items" if provider=="crossref" else "results"
    if not isinstance(container,dict) or not isinstance(container.get(key),list):
        raise AtlasError("Provider schema missing the result list; this is not an empty search")
    metadata=container if provider=="crossref" else data.get("meta",{})
    if not isinstance(metadata,dict): raise AtlasError("Malformed pagination metadata")
    next_cursor=metadata.get("next-cursor" if provider=="crossref" else "next_cursor")
    if next_cursor is not None and (not isinstance(next_cursor,str) or not next_cursor or len(next_cursor)>8192):
        raise AtlasError("Malformed next cursor")
    total=metadata.get("total-results" if provider=="crossref" else "count")
    if total is not None and (type(total) is not int or total<0): raise AtlasError("Malformed provider result count")
    items=container[key]; out=[]
    for index,item in enumerate(items):
        if not isinstance(item,dict): raise AtlasError(f"Malformed provider result at index {index}")
        title=item.get("title") or item.get("display_name") or ""
        if isinstance(title,list):
            if any(not isinstance(value,str) for value in title): raise AtlasError("Malformed title list")
            title=title[0] if title else ""
        doi=item.get("DOI") or item.get("doi") or ""
        uri=item.get("URL") or item.get("id") or ""
        if any(not isinstance(value,str) for value in (title,doi,uri)):
            raise AtlasError("Provider title, DOI and URL must be text")
        if not uri and not doi: raise AtlasError("Provider result has no traceable identifier")
        year=item.get("publication_year")
        if year is None and provider=="crossref":
            issued=item.get("issued",{})
            if not isinstance(issued,dict): raise AtlasError("Malformed publication date")
            parts=issued.get("date-parts",[])
            if parts:
                if not isinstance(parts,list) or not isinstance(parts[0],list) or not parts[0]:
                    raise AtlasError("Malformed publication date parts")
                year=parts[0][0]
        if year is not None and (type(year) is not int or not 1<=year<=9999): raise AtlasError("Invalid publication year")
        if "is_retracted" in item and type(item["is_retracted"]) is not bool: raise AtlasError("Malformed retraction flag")
        out.append({"title":title[:600],"doi":normalize_doi(doi),"url":uri,
                    "publication_year":year,"provider":provider,"provider_id":item.get("id") or doi or uri,
                    "is_retracted":item.get("is_retracted"),
                    "metadata_warnings":([] if title else ["missing_title"])+([] if year else ["missing_publication_year"]),
                    "source_type":"external_bibliographic_metadata",
                    "note":"Metadata only; inspect original context and correction/retraction status before using as claim evidence."})
    return {"provider":provider,"query":query,"requested_url":url,"observed_at":now(),
            "items":out[:limit],"total_returned":min(len(out),limit),"total_received":len(out),
            "total_available":total,"cursor":cursor,"next_cursor":next_cursor,
            "truncated":len(out)>limit,"response_sha256":digest(data),"hash_scope":"canonical provider JSON",
            "retrieval_type":"live_if_called",
            "limitations":"One bounded request, no automatic retries. Provider counts and metadata are not verified full text, exhaustive coverage or proof that a work is unretracted."}


def guarded_search(project,need_id,provider,query,limit=10,cursor=None,probe=False,plan_id=None,**kwargs):
    if provider not in HOSTS: raise AtlasError("No adapter for provider")
    resource=f"https://{HOSTS[provider]}/works"
    project.prepare_search(need_id,query,probe,plan_id)
    if probe and (limit!=1 or cursor is not None):
        raise AtlasError("Preflight probes require limit=1 without pagination; use planned RESEARCH searches for substantive retrieval")
    project.require_access(need_id,resource,"scholarly-search",consume_retry=True)
    request_id="search-"+uuid4().hex
    retrieval_artifact="retrieval/"+request_id+".json"
    observation={"id":request_id,"need_id":need_id,"provider":provider,"query":query,"limit":limit,
                 "cursor":cursor,"purpose":"probe" if probe else "research","plan_id":plan_id,
                 "resource":resource,"at":now()}
    try:
        result=search(provider,query,limit,cursor,**kwargs)
    except (AtlasError,OSError) as error:
        impact="Bibliographic coverage and source verification may be incomplete; no substitute or retry has been attempted."
        atomic_json(confined(project.path,retrieval_artifact),dict(observation,ok=False,error=str(error)))
        project.record_search(retrieval_artifact)
        project.block_access(resource,"scholarly-search",str(error),impact,need_id)
        blocked=AccessBlocked(resource,"scholarly-search",str(error),impact,need_id)
        blocked.recorded=True
        raise blocked from error
    atomic_json(confined(project.path,retrieval_artifact),dict(observation,ok=True,result=result))
    project.record_search(retrieval_artifact)
    stamp=now(); artifact="access-tests/"+need_id+"-"+stamp.replace(":","-")+".json"
    atomic_json(confined(project.path,artifact),{"ok":True,"resource":resource,"operation":"scholarly-search",
                "observed_at":stamp,"expires_at":(date(stamp)+timedelta(days=1)).isoformat(),
                "response_sha256":result["response_sha256"],"limitations":result["limitations"]})
    project.record_access_test(need_id,artifact)
    return dict(result,retrieval_artifact=retrieval_artifact,purpose=observation["purpose"])
