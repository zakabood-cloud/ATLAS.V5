"""Opt-in, budget-gated external research adapters. Never silently connect or spend.

Adapters are typed transport clients, not fully autonomous research engines.
Users must approve transmission of query/context and provider-side billing limits.
No credential values are serialized in reports. Mockable with an injected transport.
"""
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from .io import AtlasError, now, atomic_json
from .budget import Budget

DOCS = {
    "openai": "https://developers.openai.com/api/docs/guides/tools-web-search",
    "gemini": "https://ai.google.dev/gemini-api/docs/generate-content/google-search",
}
ENDPOINTS = {
    "openai": "https://api.openai.com/v1/responses",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
}
CREDENTIALS = {"openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}

@dataclass(frozen=True)
class ProviderRequest:
    provider: str
    model: str
    query: str
    request_id: str
    max_cost_usd: str
    authorized: bool = False
    private_data_approved: bool = False


def build_request(request: ProviderRequest, credential: str):
    if request.provider not in ENDPOINTS:
        raise AtlasError("Unsupported research provider")
    if (not re.fullmatch(r"[a-zA-Z0-9_.-]{2,100}", request.model)
            or request.model.startswith(".") or ".." in request.model):
        raise AtlasError("Invalid model name")
    if not isinstance(request.query, str) or not request.query.strip() or len(request.query) > 12000:
        raise AtlasError("Research query must be 1..12000 characters")
    if not isinstance(request.request_id,str) or not re.fullmatch(r"[a-zA-Z0-9_-]{4,100}",request.request_id):
        raise AtlasError("Invalid stable request ID")
    if not credential or not request.authorized or not request.private_data_approved:
        raise AtlasError("Configured credential, use approval and query-sharing approval required")
    if request.provider == "openai":
        payload = {"model":request.model,"tools":[{"type":"web_search"}],"input":request.query}
        endpoint = ENDPOINTS["openai"]
        headers={"Authorization":"Bearer "+credential,"Content-Type":"application/json"}
    else:
        payload={"contents":[{"parts":[{"text":request.query}]}],"tools":[{"google_search":{}}]}
        endpoint=ENDPOINTS["gemini"].format(model=request.model)
        headers={"x-goog-api-key":credential,"Content-Type":"application/json"}
    return endpoint,headers,payload


def default_transport(url, headers, payload, timeout=90):
    request=urllib.request.Request(url,data=json.dumps(payload).encode("utf-8"),headers=headers,method="POST")
    try:
        with urllib.request.urlopen(request,timeout=timeout) as response:
            data=response.read(6_000_001)
    except urllib.error.HTTPError as exc:
        # Do not emit potentially sensitive error bodies or request headers.
        raise AtlasError(f"Provider HTTP status {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise AtlasError("Provider unavailable or timed out: " + type(exc).__name__) from exc
    if len(data)>6_000_000:
        raise AtlasError("Provider reply exceeded safety limit")
    return json.loads(data)


def extract(result, provider):
    if not isinstance(result,dict): raise AtlasError("Provider must return a JSON object")
    citations=[]; texts=[]
    if provider=="openai":
        for part in result.get("output",[]):
            if part.get("type")=="message":
                for item in part.get("content",[]):
                    if isinstance(item.get("text"),str): texts.append(item["text"])
                    for annotation in item.get("annotations",[]):
                        if annotation.get("type")=="url_citation":
                            citations.append({"url":annotation.get("url"),"title":annotation.get("title")})
    elif provider=="gemini":
        for candidate in result.get("candidates",[]):
            for part in candidate.get("content",{}).get("parts",[]):
                if isinstance(part.get("text"),str):texts.append(part["text"])
            for chunk in candidate.get("groundingMetadata",{}).get("groundingChunks",[]):
                web=chunk.get("web",{})
                if web.get("uri"): citations.append({"url":web.get("uri"),"title":web.get("title")})
    return {"text":"\n".join(texts),"citations":list({(r["url"],r.get("title")):r for r in citations if r.get("url")}.values()),
            "warning":"Generated synthesis and provider citations are candidate leads; inspect and independently verify original sources."}


def execute(request: ProviderRequest, *, budget_file: Path, ceiling_usd: str, result_path:Path,
            credential=None, transport:Callable=default_transport):
    if not request.authorized or not request.private_data_approved:
        raise AtlasError("Explicit provider use and query-sharing approval are required")
    # A maximum-call estimate is a reservation, NOT a hard provider-side billing cap.
    key=request.provider+":"+request.request_id
    budget=Budget(budget_file,ceiling_usd)
    secret=credential or os.environ.get(CREDENTIALS.get(request.provider,""),"")
    endpoint,headers,payload=build_request(request,secret)
    result_path=Path(result_path)
    if result_path.exists(): raise AtlasError("Output already exists; choose a new idempotency key")
    reservation=budget.reserve(key,request.max_cost_usd,request.provider,authorized=True)
    if not reservation["dispatch_allowed"]: raise AtlasError("Duplicate provider request; no automatic repeat charged call")
    try:
        raw=transport(endpoint,headers,payload)
        summary=extract(raw,request.provider)
        output={"request_id":request.request_id,"provider":request.provider,"model_requested":request.model,
                "retrieved_at":now(),"endpoint":endpoint,"authorization_recorded":True,
                "provider_response":raw,"extracted":summary,"cost_status":"RESERVED_NOT_SETTLED_PROVIDER_BILLING_UNKNOWN",
                "provider_docs":DOCS[request.provider]}
        atomic_json(result_path,output)
        # Do not automatically settle a guessed actual bill.
        return {"request_id":request.request_id,"output":str(result_path),"citations":len(summary["citations"]),
                "cost_status":output["cost_status"],"budget":budget.status(),"verification_level":"provider_response_only"}
    except Exception:
        # An HTTP timeout does not prove provider didn't process or bill the request.
        # Retain the pending reservation and don't auto-retry.
        raise
